from noosDrift.settings import NOOS_USER, NOOS_NODE_ID, NOOS_CENTRAL, NOOS_ROLE, ENV_DICT, CENTRAL_ROLE, NODE_ROLE, \
    NOOS_ERROR_CODES
from noos_services.helper import Helper
from django.db.models.signals import post_save, pre_save
from celery.signals import task_failure, task_success, task_prerun, task_revoked
from noos_services.models import Node, SimulationDemand, LoggingMessage, ForcingCouple, UploadedFile
from django.dispatch import receiver
import logging
import json
from subprocess import SubprocessError, CalledProcessError

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
    assert ENV_DICT[NOOS_ROLE] in [NODE_ROLE, CENTRAL_ROLE], "Signals.py, Node role not \"Node\" or \"Central\""


def common_logging(**kwargs):
    """
    This will contain all the commonalities in logging messages
    :param kwargs:
    :return:
    """
    object_and_method = "Signals.common_logging"
    logger.info("{}, start".format(object_and_method))
    logger.debug("{}, kwargs : {}".format(object_and_method, kwargs))

    the_simulation_id = kwargs["simulation_demand_id"]
    central = Node.objects.get(hostname=ENV_DICT[NOOS_CENTRAL])
    the_simulation = SimulationDemand.objects.get(pk=the_simulation_id)
    this_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
    this_couple = ForcingCouple.objects.get(pk=kwargs["forcing_couple_id"])

    local_message = LoggingMessage()
    local_message.simulation_demand = the_simulation
    local_message.node = this_node
    local_message.forcing_couple = this_couple
    local_message.noos_model = this_node.model
    local_message.status = kwargs["log_status"]
    local_message.message = kwargs["log_message"]

    message_parameters = {"simulation_demand": the_simulation_id,
                          "forcing_couple": kwargs["forcing_couple_id"],
                          "node": ENV_DICT[NOOS_NODE_ID],
                          "noos_model": this_node.model.pk,
                          "status": kwargs["status"],
                          "message": kwargs["central_message"]}

    logger.debug("{}, saving message in DB, {}".format(object_and_method, message_parameters))
    local_message.save()
    logger.debug("{}, message in DB saved".format(object_and_method))

    logger.debug("{}, sending message to CENTRAL, {}".format(object_and_method, message_parameters))
    central.add_logging_message(message_parameters, the_user=NOOS_USER)
    logger.debug("{}, message to CENTRAL sent".format(object_and_method))

    logger.info("{}, end of".format(object_and_method))
    return None


@receiver(pre_save, sender=SimulationDemand,
          dispatch_uid="simulation_demand_is_received_gcd1angstgy95wrh118wrz2cy8rut8uw")
def simulation_demand_is_received(sender, instance, **kwargs):
    logger.info("Signal.simulation_demand_is_recieved")
    json_dict = json.loads(instance.json_txt)
    if 'id' in json_dict:
        instance.id = json_dict['id']


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
    React to the creation of a simulation demand on the database after the save
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        logger.info("Signal.simulation_demand_is_created, initialising")
        try:
            uploadedfile_creation_helper(instance)
        except FileNotFoundError as exc:
            local_message = LoggingMessage()
            local_message.simulation_demand = instance.simulation
            local_message.node = instance.node
            local_message.forcing_couple = instance.forcing_couple
            local_message.noos_model = instance.noos_model
            local_message.status = "RESULT FILE ERROR"
            local_message.message = exc.strerror
            local_message.save()


@receiver(post_save, sender=LoggingMessage,
          dispatch_uid="logging_message_is_created_gcd1angstgy54wrh118wrz2cy8rut8uw")
def logging_message_is_created(sender, instance, created, **kwargs):
    if created:
        logger.info("Signal: logging_message_is_created, initialising")
        loggingmessages_creation_helper(instance)


@task_success.connect
def success_handler(result=None, sender=None, headers=None, body=None, **kwargs):
    object_and_name = "task.success_handler"
    logger.info("{}, start of".format(object_and_name))
    logger.info("{}, success for {}".format(object_and_name, sender.name))
    if sender.name == 'tasks.upload_processing':
        object_and_method = "Signals.upload_processing_success"
        logger.info("{}, start".format(object_and_method))
        logger.debug("{}, result : {}".format(object_and_method, result))
        central = Node.objects.get(hostname=ENV_DICT[NOOS_CENTRAL])

        the_simulation_id = result["simulation_demand_id"]
        the_simulation = SimulationDemand.objects.get(pk=the_simulation_id)
        this_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
        this_forcing = ForcingCouple.objects.get(pk=result["forcing_couple_id"])

        local_message = LoggingMessage()
        local_message.simulation_demand = the_simulation
        local_message.node = this_node
        local_message.forcing_couple = this_forcing
        local_message.noos_model = this_node.model
        local_message.status = result["status"]
        local_message.message = result["message"]

        logger.debug("{}, saving message to DB".format(object_and_method))
        local_message.save()
        logger.debug("{}, message to DB saved".format(object_and_method))

        central_msg_dict = {"node": ENV_DICT[NOOS_NODE_ID],
                            "simulation_demand": result["simulation_demand_id"],
                            "status": result["status"],
                            "message": result["message"],
                            "forcing_couple": result["forcing_couple_id"],
                            "noos_model": result["noos_model_id"],
                            }

        logger.debug("{}, sending logging message to Central".format(object_and_method))
        central.add_logging_message(message_parameters=central_msg_dict, the_user=NOOS_USER)
        logger.debug("{}, logging message to Central sent ".format(object_and_method))

        uploaded_file_dict = {
            "simulation": result["simulation_demand_id"],
            "node": result["node_id"],
            "noos_model": result["noos_model_id"],
            "forcing_couple": result["forcing_couple_id"],
            "filename": result["filename"],
            "json_txt": "{}"
        }

        logger.debug("{}, sending uploaded message to Central".format(object_and_method))
        central.add_uploadedfile(message_parameters=uploaded_file_dict, the_user=NOOS_USER)
        logger.debug("{}, uploaded message to Central sent".format(object_and_method))
        logger.info("{}, end of".format(object_and_method))

    return None


@task_failure.connect
def failure_handler(task_id, exception, traceback, sender=None, einfo=None, *args, **kwargs):
    object_and_name = "task.failure_handler"
    logger.info("{}, start of".format(object_and_name))
    logger.info("{}, failure for {}".format(object_and_name, sender.name))
    if sender.name == 'tasks.netcdf_processing':
        simulation_id = kwargs["simulation_demand_id"]
        forcing_couple_id = kwargs["forcing_couple_id"]

        if type(exception) is SubprocessError:
            log_message = "Signals.netcdf_failure, simulation demand {}, forcing {}, SubprocessError : {}".format(
                simulation_id, forcing_couple_id, traceback)
        elif type(exception) is CalledProcessError:
            log_message = "Signals.netcdf_failure, simulation demand {}, forcing {}, CalledProcessError : {}".format(
                simulation_id, forcing_couple_id, exception.returncode)
        else:
            log_message = "Signals.netcdf_failure, simulation demand {}, forcing {}, Unknown exception : {}".format(
                simulation_id, forcing_couple_id, exception)

        central_message = "Netcdf failed for forcing {}, simulation demand {}".format(forcing_couple_id, simulation_id)

        common_logging(simulation_demand_id=simulation_id, forcing_id=forcing_couple_id, log_status="NETCDF-FAILED",
                       log_message=log_message, central_status="FORCING-ERROR", central_message=central_message)
    elif sender.name == 'tasks.local_processing':
        simulation_id = kwargs["simulation_demand_id"]
        forcing_couple_id = kwargs["forcing_couple_id"]

        log_prefix = "Signals.local_processing_failure, simulation demand"
        if type(exception) is SubprocessError:
            log_message = "{} {}, forcing_couple {}, SubprocessError : {}".format(log_prefix, simulation_id,
                                                                                  forcing_couple_id, traceback)
        elif type(exception) is CalledProcessError:
            log_message = "{} {}, forcing {}, CalledProcessError : {}".format(log_prefix, simulation_id,
                                                                              forcing_couple_id,
                                                                              exception.returncode)
            errmesg = NOOS_ERROR_CODES[exception.returncode]
            message_parameters = {"simulation_demand": str(kwargs["simulation_demand_id"]),
                                  "forcing_couple": kwargs["forcing_couple_id"],
                                  "node": ENV_DICT[NOOS_NODE_ID],
                                  "noos_model": kwargs["noos_model_id"],
                                  "status": "FORCING-ERROR",
                                  "message": errmesg}
            central = Node.objects.get(hostname=ENV_DICT[NOOS_CENTRAL])
            central.add_logging_message(message_parameters, the_user=NOOS_USER)
        else:
            log_message = "{} {}, forcing {}, Unknown exception : {}".format(log_prefix, simulation_id,
                                                                             forcing_couple_id,
                                                                             exception)

        central_message = "Model processing failed for forcing_couple {}, simulation demand {}".format(
            forcing_couple_id,
            simulation_id)

        common_logging(simulation_demand_id=simulation_id, forcing_id=forcing_couple_id, log_status="MODEL-FAILED",
                       log_message=log_message, central_status="FORCING-ERROR", central_message=central_message)
    elif sender.name == 'tasks.upload_processing':
        if type(exception) is SubprocessError:
            logger.error("Signals.upload_processing_failure, SubprocessError : {}".format(traceback))
        elif type(exception) is CalledProcessError:
            logger.error("Signals.upload_processing_failure, CalledProcessError : {}".format(exception.returncode))
    else:
        logger.info("{}, WTF, unknown task name ???".format(object_and_name))

    logger.info("{}, end of".format(object_and_name))
    return None


@task_prerun.connect
def prerun_handler(sender=None, *args, **kwargs):
    """
    Log message before processing
    :param sender
    :param args:
    :param kwargs:
    :return:
    """
    thekwargs = kwargs["kwargs"]
    # dickeys = kwargs["kwargs"].keys()
    # logger.info("##############Keys in kwargs")
    # for dkey in dickeys:
    #    logger.info("{}".format(dkey))
    # logger.info("##############END of Keys in kwargs")

    object_and_name = "task.prerun_handler"
    logger.info("{}, start of".format(object_and_name))
    logger.info("{}, prerun for {}".format(object_and_name, sender.name))
    if sender.name == 'tasks.netcdf_processing':
        the_simulation_id = thekwargs["simulation_demand_id"]
        the_simulation = SimulationDemand.objects.get(pk=the_simulation_id)
        this_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
        this_couple = ForcingCouple.objects.get(pk=thekwargs["forcing_couple_id"])

        txt_message = "Started to execute forcing_couple {} for simulation demand {}".format(this_couple.pk,
                                                                                             the_simulation_id)
        local_message = LoggingMessage()
        local_message.simulation_demand = the_simulation
        local_message.node = this_node
        local_message.forcing_couple = this_couple
        local_message.noos_model = this_node.model
        local_message.status = "FORCING-PROCESSING"
        local_message.message = txt_message

        local_message.save()


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
        simulation_id = request.kwargsrepr["simulation_demand_id"]
        forcing_couple_id = request.kwargsrepr["forcing_couple_id"]
        log_prefix = "Signals.local_processing_revoked, simulation demand"

        if expired:
            log_message = "{} {}, forcing_couple {} has timed out".format(log_prefix, simulation_id, forcing_couple_id)
            central_message = "Model processing timed out for forcing_couple {}, simulation demand {}".format(
                forcing_couple_id, simulation_id)
        elif terminated:
            log_message = "{} {}, forcing_couple {} was terminated".format(log_prefix, simulation_id, forcing_couple_id)
            central_message = "Model processing was terminated for forcing_couple {}, simulation demand {}".format(
                forcing_couple_id, simulation_id)
        else:
            log_message = "{}, Error".format(log_prefix)
            central_message = "{}, Error".format(log_prefix)

        common_logging(simulation_demand_id=simulation_id, forcing_id=forcing_couple_id, log_status="MODEL-REVOKED",
                       log_message=log_message, central_status="FORCING-ERROR", central_message=central_message)
