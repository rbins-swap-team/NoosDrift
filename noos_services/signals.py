import json
import logging
import os
from subprocess import SubprocessError, CalledProcessError

from celery.signals import task_failure, task_success, task_prerun, task_postrun, task_revoked
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from noosDrift.settings import CENTRAL_ROLE, ENV_DICT, HOSTNAME, NODE_ROLE, NOOS_CENTRAL_ID, NOOS_ERROR_CODES, \
    NOOS_NODE_ID, NOOS_ROLE, NOOS_RESULTS_DIR, NOOS_USER
from noos_services.helper import Helper
from noos_services.models import ForcingCouple, LoggingMessage, Node, NoosModel, SimulationDemand, UploadedFile
from noos_services.ns_const import SignalsConst, StatusConst

logger = logging.getLogger(__name__)
messagetmp = "Initializing process for request {} on node {}:{}"


simulation_creation_helper = None
loggingmessages_creation_helper = None
if ENV_DICT[NOOS_ROLE] == NODE_ROLE:
    simulation_creation_helper = Helper.node_simulation_demand_help
    loggingmessages_creation_helper = Helper.node_logging_messages_help

elif ENV_DICT[NOOS_ROLE] == CENTRAL_ROLE:
    simulation_creation_helper = Helper.central_dispatching_help
    loggingmessages_creation_helper = Helper.logging_messages_help
    uploadedfile_creation_helper = Helper.central_uploadedfile_help
else:
    errmsg = "Signals.py, Node role \"{}\" not \"{}\" or \"{}\"".format(
        ENV_DICT[NOOS_ROLE], NODE_ROLE, CENTRAL_ROLE)
    assert ENV_DICT[NOOS_ROLE] in [NODE_ROLE, CENTRAL_ROLE], errmsg


def common_logging(**kwargs):
    """
    This will contain all the commonalities in logging messages
    :param kwargs:
    :return:
    """
    object_and_method = "Signals.common_logging"
    logger.info("{}, start".format(object_and_method))
    logger.debug("{}, kwargs : {}".format(object_and_method, kwargs))

    the_simulation_id = kwargs[SignalsConst.SIMULATION_DEMAND_ID]
    central = Node.objects.get(pk=ENV_DICT[NOOS_CENTRAL_ID])
    the_simulation = SimulationDemand.objects.get(pk=the_simulation_id)
    this_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
    this_couple = ForcingCouple.objects.get(pk=kwargs[SignalsConst.FORCING_COUPLE_ID])

    local_message = LoggingMessage()
    local_message.simulation_demand = the_simulation
    local_message.node = this_node
    local_message.forcing_couple = this_couple
    local_message.noos_model = this_node.model
    local_message.status = kwargs[SignalsConst.LOG_STATUS]
    local_message.message = kwargs[SignalsConst.LOG_MESSAGE]

    logger.debug("{}, saving message in DB".format(object_and_method))
    local_message.save()
    logger.debug("{}, message in DB saved".format(object_and_method))

    if kwargs[SignalsConst.LOG_STATUS] == StatusConst.PREPROCESSING_FAILED or \
            kwargs[SignalsConst.LOG_STATUS] == StatusConst.MODEL_FAILED or \
            kwargs[SignalsConst.LOG_STATUS] == StatusConst.POSTPROCESSING_FAILED or \
            kwargs[SignalsConst.LOG_STATUS] == StatusConst.UPLOAD_FAILED:
        message_parameters = {SignalsConst.SIMULATION_DEMAND: the_simulation_id,
                              SignalsConst.FORCING_COUPLE: kwargs[SignalsConst.FORCING_COUPLE_ID],
                              SignalsConst.NODE: ENV_DICT[NOOS_NODE_ID],
                              SignalsConst.NOOS_MODEL: this_node.model.pk,
                              SignalsConst.STATUS: StatusConst.NODE_ERROR,
                              SignalsConst.MESSAGE: kwargs[SignalsConst.LOG_MESSAGE]}
    else:
        message_parameters = {SignalsConst.SIMULATION_DEMAND: the_simulation_id,
                              SignalsConst.FORCING_COUPLE: kwargs[SignalsConst.FORCING_COUPLE_ID],
                              SignalsConst.NODE: ENV_DICT[NOOS_NODE_ID],
                              SignalsConst.NOOS_MODEL: this_node.model.pk,
                              SignalsConst.STATUS: kwargs[SignalsConst.LOG_STATUS],
                              SignalsConst.MESSAGE: kwargs[SignalsConst.LOG_MESSAGE]}

    logger.debug("{}, sending message to CENTRAL, {}".format(object_and_method, message_parameters))
    central.add_logging_message(message_parameters, the_user=NOOS_USER)
    logger.debug("{}, message to CENTRAL sent".format(object_and_method))

    logger.info("{}, end of".format(object_and_method))
    return None


@receiver(pre_save, sender=SimulationDemand,
          dispatch_uid="simulation_demand_is_received_gcd1angstgy95wrh118wrz2cy8rut8uw")
def simulation_demand_is_received(sender, instance, **kwargs):
    """
    React to the reception of a simulation demand
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    object_and_method = "Signal.simulation_demand_is_recieved"
    logger.info("{}, start".format(object_and_method))
    logger.info("{} value : {}".format(object_and_method, instance))

    if NODE_ROLE == ENV_DICT[NOOS_ROLE] and "id" not in instance.json_txt.keys():
        raise ValueError("{}, Machine {}, has NODE role and recieves simulationdemand without id".format(
            object_and_method, HOSTNAME))
    if NODE_ROLE == ENV_DICT[NOOS_ROLE] and "id" in instance.json_txt.keys():
        aninstance = None
        try:
            aninstance = SimulationDemand.objects.get(pk=instance.json_txt["id"])
        except ObjectDoesNotExist:
            instance.id = instance.json_txt["id"]

        if aninstance is not None:
            raise ValueError("{} Machine {}, was asked to create a simulation demand which already exists".format(
                object_and_method, HOSTNAME))

        instance.id = instance.json_txt["id"]

    logger.info("{} end".format(object_and_method))


@receiver(post_save, sender=SimulationDemand,
          dispatch_uid="simulation_demand_is_created_gcd1angstgy54wrh118wrz2cy8rut8uw")
def simulation_demand_is_created(sender, instance, created, **kwargs):
    """
    React to the creation of a simulation demand on the database after the save
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        logger.info("Signal.simulation_demand_is_created, initialising")
        simulation_creation_helper(instance)


@receiver(post_save, sender=UploadedFile,
          dispatch_uid="uploadedfile_is_created_gcd1angstgy54wrh118wrz2cy8rut8uw")
def uploadedfile_is_created(sender, instance, created, **kwargs):
    """
    React to the creation of an uploaded file record on the database
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        logger.info("Signal.uploadedfile_is_created, initialising")
        try:
            uploadedfile_creation_helper(instance)
        except FileNotFoundError as exc:
            logger.error("Signal.uploadedfile_is_created, error, \'{}\'".format(exc))
            local_message = LoggingMessage()
            local_message.simulation_demand = instance.simulation
            local_message.node = instance.node
            local_message.forcing_couple = instance.forcing_couple
            local_message.noos_model = instance.noos_model
            local_message.status = StatusConst.RESULT_FILE_ERROR
            local_message.message = "{}".format(exc)
            local_message.save()


@receiver(post_save, sender=LoggingMessage,
          dispatch_uid="logging_message_is_created_gcd1angstgy54wrh118wrz2cy8rut8uw")
def logging_message_is_created(sender, instance, created, **kwargs):
    if created:
        logger.info("Signal: logging_message_is_created, initialising")
        loggingmessages_creation_helper(instance)


@task_success.connect
def success_handler(result=None, sender=None, headers=None, body=None, **kwargs):
    """
    Handler triggerred in case of task success
    :param result:
    :param sender:
    :param headers:
    :param body:
    :param kwargs:
    :return:
    """
    object_and_name = "task.success_handler"
    logger.info("{}, start of".format(object_and_name))
    logger.info("{}, success for {}".format(object_and_name, sender.name))

    if sender.name == 'tasks.mme_processing':
        # message_parameters = {SignalsConst.SIMULATION_DEMAND_ID: simulation_id,
        #                      SignalsConst.NODE_ID: ENV_DICT[NOOS_NODE_ID],
        #                      SignalsConst.NOOS_MODEL_ID: mme_model,
        #                      SignalsConst.STATUS: StatusConst.ANALYSIS_OK,
        #                      SignalsConst.MESSAGE: ""
        #                      }]
        object_and_method = "Signals.mme_processing_success"
        logger.info("{}, start".format(object_and_method))
        logger.debug("{}, result : {}".format(object_and_method, result))

        logger.debug("{}, succes of MME processing happened on central".format(object_and_method))
        node = Node.objects.get(pk=result[SignalsConst.NODE_ID])
        noos_model = NoosModel.objects.get(pk=result[SignalsConst.NOOS_MODEL_ID])
        simulation_demand = SimulationDemand.objects.get(pk=result[SignalsConst.SIMULATION_DEMAND_ID])
        new_message = LoggingMessage(
            node=node,
            simulation_demand=simulation_demand,
            status=result[SignalsConst.STATUS],
            message=result[SignalsConst.MESSAGE],
            noos_model=noos_model
        )
        new_message.save()
        simulation_demand.status = "OK"
        simulation_demand.save()

        logger.debug("{}, end of".format(object_and_method))
        return None
    elif sender.name == 'tasks.upload_processing':
        object_and_method = "Signals.upload_processing_success"
        logger.info("{}, start".format(object_and_method))
        # message_parameters = {SignalsConst.SIMULATION_DEMAND_ID: simulation_demand_id,
        #                       SignalsConst.FORCING_COUPLE_ID: forcing_couple_id,
        #                       SignalsConst.NODE_ID: ENV_DICT[NOOS_NODE_ID],
        #                       SignalsConst.NOOS_MODEL_ID: kwargs[SignalsConst.NOOS_MODEL_ID],
        #                       SignalsConst.STATUS: StatusConst.FORCING_FILE_UPLOADED,
        #                       SignalsConst.MESSAGE: message_txt,
        #                       SignalsConst.LAST_COUPLE: kwargs[SignalsConst.LAST_COUPLE],
        #                       SignalsConst.FILENAME: simulation_demand_archive}
        #                       SignalsConst.NOOS_MODEL_CODE: kwargs[SignalsConst.NOOS_MODEL_CODE],
        #                       SignalsConst.COUPLE_CODE: kwargs[SignalsConst.COUPLE_CODE]

        simulation_demand_id = result[SignalsConst.SIMULATION_DEMAND_ID]
        model_forcing_result_file = "./noosdrift_{}_{}_{}.json".format(simulation_demand_id,
                                                                       result[SignalsConst.NOOS_MODEL_CODE],
                                                                       result[SignalsConst.COUPLE_CODE])

        logger.debug("{}, result : {}".format(object_and_method, result))
        central = Node.objects.get(pk=ENV_DICT[NOOS_CENTRAL_ID])
        the_simulation = SimulationDemand.objects.get(pk=simulation_demand_id)
        this_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
        this_forcing = ForcingCouple.objects.get(pk=result[SignalsConst.FORCING_COUPLE_ID])
        message_status = result[SignalsConst.STATUS]
        message_message = result[SignalsConst.MESSAGE]

        local_message = LoggingMessage()
        local_message.simulation_demand = the_simulation
        local_message.node = this_node
        local_message.forcing_couple = this_forcing
        local_message.noos_model = this_node.model
        local_message.status = message_status
        local_message.message = message_message

        logger.debug("{}, saving message to DB".format(object_and_method))
        local_message.save()
        logger.debug("{}, message to DB saved".format(object_and_method))

        central_msg_dict = {SignalsConst.NODE: this_node.id,
                            SignalsConst.SIMULATION_DEMAND: simulation_demand_id,
                            SignalsConst.STATUS: message_status,
                            SignalsConst.MESSAGE: message_message,
                            SignalsConst.FORCING_COUPLE: this_forcing.id,
                            SignalsConst.NOOS_MODEL: this_node.model.id,
                            }

        os.chdir(NOOS_RESULTS_DIR)
        with open(model_forcing_result_file) as json_structure:

            json_str = json.load(json_structure)
            if json_str is None:
                json_str = "{}"

            uploaded_file_dict = {
                SignalsConst.SIMULATION: simulation_demand_id,
                SignalsConst.NODE: this_node.id,
                SignalsConst.NOOS_MODEL: this_node.model.id,
                SignalsConst.FORCING_COUPLE: this_forcing.id,
                SignalsConst.FILENAME: result[SignalsConst.FILENAME],
                SignalsConst.JSON_TXT: json_str
            }

            logger.debug("{}, sending message file to Central".format(object_and_method))
            central.add_uploadedfile(message_parameters=uploaded_file_dict, the_user=NOOS_USER)
            logger.debug("{}, uploaded message to Central sent".format(object_and_method))

            json_structure.close()

        # replaced
        # logger.debug("{}, sending logging message to Central".format(object_and_method))
        # central.add_logging_message(message_parameters=central_msg_dict, the_user=NOOS_USER)
        # logger.debug("{}, logging message to Central sent ".format(object_and_method))

    logger.debug("{}, end of".format(object_and_name))


@task_failure.connect
def failure_handler(task_id, exception, traceback, sender=None, einfo=None, *args, **kwargs):
    """
    Handler triggerred in case of task faillure
    :param task_id:
    :param exception:
    :param traceback:
    :param sender:
    :param einfo:
    :param args:
    :param kwargs:
    :return:
    """

    object_and_name = "task.failure_handler"
    logger.info("{}, start of".format(object_and_name))
    logger.info("{}, failure for {}".format(object_and_name, sender.name))
    local_message = LoggingMessage()

    if sender.name == 'tasks.node_pre_processing':
        parameters_dict = kwargs["kwargs"]['parameters_dict']
        simulation_id = parameters_dict[SignalsConst.SIMULATION_DEMAND_ID]
        forcing_couple_id = parameters_dict[SignalsConst.FORCING_COUPLE_ID]

        log_prefix = "Signals.node_pre_processing_failure, simulation demand"
        if isinstance(exception, CalledProcessError):
            errmesg = NOOS_ERROR_CODES[exception.returncode][0]
            log_message = "{} {}, ForcingCouple {}, ErrorCode : {}, ErrorMessage : {}".format(log_prefix,
                                                                                              simulation_id,
                                                                                              forcing_couple_id,
                                                                                              exception.returncode,
                                                                                              errmesg)
        elif isinstance(exception, SubprocessError):
            msg_tmp = "{} {}, ForcingCouple {}, SubprocessError : {}"
            log_message = msg_tmp.format(log_prefix, simulation_id, forcing_couple_id, traceback)
        else:
            msg_tmp = "{} {}, ForcingCouple {}, Unknown exception : {}"
            log_message = msg_tmp.format(log_prefix, simulation_id, forcing_couple_id, exception)

        logger.error("BEFORE COMMON LOGGING {}".format(sender.name))
        common_logging(simulation_demand_id=simulation_id, forcing_couple_id=forcing_couple_id,
                       log_status=StatusConst.PREPROCESSING_FAILED, log_message=log_message)
        logger.error("AFTER COMMON LOGGING {}".format(sender.name))

    elif sender.name == 'tasks.local_processing':
        parameters_dict = kwargs["kwargs"]['parameters_dict']
        simulation_id = parameters_dict[SignalsConst.SIMULATION_DEMAND_ID]
        forcing_couple_id = parameters_dict[SignalsConst.FORCING_COUPLE_ID]

        log_prefix = "Signals.local_processing_failure, simulation demand"
        if isinstance(exception, CalledProcessError):
            errmesg = NOOS_ERROR_CODES[exception.returncode][0]
            log_message = "{} {}, ForcingCouple {}, ErrorCode : {}, ErrorMessage : {}".format(log_prefix,
                                                                                              simulation_id,
                                                                                              forcing_couple_id,
                                                                                              exception.returncode,
                                                                                              errmesg)
        elif isinstance(exception, SubprocessError):
            log_message = "{} {}, ForcingCouple {}, SubprocessError : {}".format(log_prefix, simulation_id,
                                                                                 forcing_couple_id, traceback)
        else:
            log_message = "{} {}, ForcingCouple {}, Unknown exception : {}".format(log_prefix,
                                                                                   simulation_id,
                                                                                   forcing_couple_id,
                                                                                   exception)

        logger.error("BEFORE COMMON LOGGING {}".format(sender.name))
        common_logging(simulation_demand_id=simulation_id, forcing_couple_id=forcing_couple_id,
                       log_status=StatusConst.MODEL_FAILED, log_message=log_message)
        logger.error("AFTER COMMON LOGGING {}".format(sender.name))

    elif sender.name == 'tasks.node_post_processing':
        parameters_dict = kwargs["kwargs"]['parameters_dict']
        simulation_id = parameters_dict[SignalsConst.SIMULATION_DEMAND_ID]
        forcing_couple_id = parameters_dict[SignalsConst.FORCING_COUPLE_ID]

        log_prefix = "Signals.node_post_processing_failure, simulation demand"
        if isinstance(exception, CalledProcessError):
            errmesg = NOOS_ERROR_CODES[exception.returncode][0]
            log_message = "{} {}, ForcingCouple {}, ErrorCode : {}, ErrorMessage : {}".format(log_prefix,
                                                                                              simulation_id,
                                                                                              forcing_couple_id,
                                                                                              exception.returncode,
                                                                                              errmesg)
        elif isinstance(exception, SubprocessError):
            log_message = "{} {}, ForcingCouple {}, SubprocessError : {}".format(log_prefix, simulation_id,
                                                                                 forcing_couple_id, traceback)
        else:
            log_message = "{} {}, ForcingCouple {}, Unknown exception : {}".format(log_prefix,
                                                                                   simulation_id,
                                                                                   forcing_couple_id,
                                                                                   exception)

        logger.error("BEFORE COMMON LOGGING {}".format(sender.name))
        common_logging(simulation_demand_id=simulation_id, forcing_couple_id=forcing_couple_id,
                       log_status=StatusConst.POSTPROCESSING_FAILED, log_message=log_message)
        logger.error("AFTER COMMON LOGGING {}".format(sender.name))

    elif sender.name == 'tasks.upload_processing':
        parameters_dict = kwargs["kwargs"]['parameters_dict']
        simulation_id = parameters_dict[SignalsConst.SIMULATION_DEMAND_ID]
        forcing_couple_id = parameters_dict[SignalsConst.FORCING_COUPLE_ID]

        log_prefix = "Signals.upload_processing_failure, simulation demand"
        if isinstance(exception, CalledProcessError):
            log_message = "{} {}, ForcingCouple {}, ErrorCode : {}, ErrorMessage : {}".format(log_prefix,
                                                                                              simulation_id,
                                                                                              forcing_couple_id,
                                                                                              exception.returncode,
                                                                                              exception)
        elif isinstance(exception, SubprocessError):
            log_message = "{} {}, ForcingCouple {}, SubprocessError : {}".format(log_prefix, simulation_id,
                                                                                 forcing_couple_id, traceback)
        else:
            log_message = "{} {}, ForcingCouple {}, Unknown exception : {}".format(log_prefix,
                                                                                   simulation_id,
                                                                                   forcing_couple_id,
                                                                                   exception)

        logger.error("BEFORE COMMON LOGGING {}".format(sender.name))
        common_logging(simulation_demand_id=simulation_id, forcing_couple_id=forcing_couple_id,
                       log_status=StatusConst.UPLOAD_FAILED, log_message=log_message)

        logger.error("AFTER COMMON LOGGING {}".format(sender.name))

    elif sender.name == 'tasks.mme_processing':
        log_prefix = "Signals.mme_processing_failure, simulation demand"
        simulation_id = kwargs["kwargs"][SignalsConst.SIMULATION_DEMAND_ID]
        if isinstance(exception, CalledProcessError):
            log_message = "{} {}, ErrorCode : {}, ErrorMessage : {}".format(log_prefix,
                                                                            simulation_id,
                                                                            exception.returncode,
                                                                            exception)

        elif isinstance(exception, SubprocessError):
            log_message = "{} {},  SubprocessError : {}".format(log_prefix, simulation_id, traceback)
        else:
            log_message = "{} {}, Unknown exception : {}".format(log_prefix, simulation_id, exception)

        logger.error("{}".format(log_message))

    elif sender.name == 'tasks.send_demand_to_node':
        log_prefix = "Signals.send_demand_to_node_failure, simulation demand"
        simulation_id = kwargs["kwargs"][SignalsConst.SIMULATION_DEMAND_ID]
        log_message = "{} {}, ErrorCode : {}, ErrorMessage : {}".format(log_prefix,
                                                                        simulation_id,
                                                                        exception.returncode,
                                                                        exception)
        logger.error("{}".format(log_message))

        local_message.simulation_demand = SimulationDemand.objects.get(pk=simulation_id)
        local_message.node = ENV_DICT[NOOS_NODE_ID],
        local_message.status = StatusConst.SEND_FAILED
        local_message.message = log_message
        logger.debug("{}, saving message in DB".format(log_prefix))
        local_message.save()
        logger.debug("{}, message in DB saved".format(log_prefix))

    else:
        simulation_id = kwargs["kwargs"][SignalsConst.SIMULATION_DEMAND_ID]
        logger.error("{}, exeption : {}".format(sender.name, exception))
        logger.error("{}, traceback : {}".format(sender.name, traceback))

        log_message = "Error for {}, exception : {}, traceback : {}".format(sender.name, exception, traceback)

        local_message.simulation_demand = SimulationDemand.objects.get(pk=simulation_id)
        local_message.node = ENV_DICT[NOOS_NODE_ID],
        local_message.status = StatusConst.UNKNOWN_FAILED
        local_message.message = log_message

        logger.debug("{}, saving message in DB".format(object_and_name))
        local_message.save()
        logger.debug("{}, message in DB saved".format(object_and_name))

    logger.info("{}, end of".format(object_and_name))


@task_prerun.connect
def prerun_handler(sender=None, *args, **kwargs):
    """
    Log message before processing
    :param sender
    :param args:
    :param kwargs:
    :return:
    """

    object_and_name = "task.prerun_handler"
    logger.info("{}, start of".format(object_and_name))
    logger.info("{}, prerun for {}".format(object_and_name, sender.name))
    logger.info("{}, kwargs {}".format(object_and_name, kwargs))

    if sender.name == 'tasks.node_pre_processing':
        parameters_dict = kwargs["kwargs"]['parameters_dict']
        the_simulation_id = parameters_dict[SignalsConst.SIMULATION_DEMAND_ID]
        the_simulation = SimulationDemand.objects.get(pk=the_simulation_id)
        this_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
        this_couple = ForcingCouple.objects.get(pk=parameters_dict[SignalsConst.FORCING_COUPLE_ID])

        txt_message = "Started to execute forcing_couple {} for simulation demand {}".format(this_couple.pk,
                                                                                             the_simulation_id)
        local_message = LoggingMessage()
        local_message.simulation_demand = the_simulation
        local_message.node = this_node
        local_message.forcing_couple = this_couple
        local_message.noos_model = this_node.model
        local_message.status = StatusConst.NETCDF_PROCESSING
        local_message.message = txt_message
        local_message.save()


@task_postrun.connect
def postrun_handler(task, task_id, sender=None, *args, **kwargs):
    """
    Log message before processing
    :param task:
    :param task_id:
    :param sender
    :param args:
    :param kwargs:
    :return:
    """

    object_and_name = "task.postrun_handler"
    logger.info("{}, start of".format(object_and_name))
    logger.info("{}, postrun for {}".format(object_and_name, sender.name))
    logger.info("{}, postrun task info : {}".format(object_and_name, kwargs))

    logger.info("{}, end of".format(object_and_name))


@task_revoked.connect
def revoked_handler(request, terminated, signum, expired, sender=None, **kwargs):
    """
    React to an exception in tasks.local_processing
    :param request:
    :param terminated:
    :param signum:
    :param expired:
    :param sender:
    :param kwargs:
    :return:
    """

    if sender.name == "local_processing":
        simulation_id = request.kwargsrepr[SignalsConst.SIMULATION_DEMAND_ID]
        forcing_couple_id = request.kwargsrepr[SignalsConst.FORCING_COUPLE_ID]
        log_prefix = "Signals.local_processing_revoked, simulation demand"

        if expired:
            log_message = "Model processing timed out for forcing_couple {}, simulation demand {}".format(
                forcing_couple_id, simulation_id)
        elif terminated:
            log_message = "Model processing was terminated for forcing_couple {}, simulation demand {}".format(
                forcing_couple_id, simulation_id)
        else:
            log_message = "{}, Error".format(log_prefix)

        common_logging(simulation_demand_id=simulation_id, forcing_couple_id=forcing_couple_id,
                       log_status=StatusConst.MODEL_REVOKED, log_message=log_message)
