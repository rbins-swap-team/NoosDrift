from celery import shared_task, chain
from celery.utils.log import get_task_logger
from noos_services.models import Node, LoggingMessage, SimulationDemand, ForcingCouple
from noosDrift.settings import NOOS_USER, BASE_DIR, REQUESTS_DIR, ENV_DICT, NOOS_NODE_ID
import json
import os
import shlex
import subprocess
import tarfile

logger = get_task_logger(__name__)


@shared_task(bind=True, name='tasks.netcdf_processing')
def netcdf_processing(self, *args, **kwargs):
    """
    A method designed to prepare for a forcing to be executed.
    The method must prepare a json file containing the necessary parameters for the forcing to be executed properly
    The method also informs the central that the forcing is being processed
    Is linked to signals
      * prerun_handler
      * failure_handler

    :param self:
    :param args:
    :param kwargs:
    :return:
    """
    object_and_name = "Tasks netcdf_processing"
    logger.info("{}, start of".format(object_and_name))
    res_path1 = os.path.join(REQUESTS_DIR, str(kwargs["simulation_demand_id"]))
    res_path2 = os.path.join(res_path1, kwargs["couple_code"])

    os.chdir(res_path2)

    data = subprocess.run('sleep 20', shell=True, check=True, timeout=3600, universal_newlines=True)
    data.check_returncode()
    logger.info("{}, SUCCESS, end of".format(object_and_name))
    return None


@shared_task(bind=True, name='tasks.local_processing')
def local_processing(self, *args, **kwargs):
    """
    This method will really spawn the process running the model with the adequate forcing
    Is linked to signals
      * revoked_handler
      * failure_handler
    :param self:
    :param args:
    :param kwargs:
    :return:
    """
    name_and_method = "tasks local_processing"
    logger.info("{}, start of".format(name_and_method))

    res_path1 = os.path.join(REQUESTS_DIR, str(kwargs["simulation_demand_id"]))
    res_path2 = os.path.join(res_path1, kwargs["couple_code"])
    save_dir = os.getcwd()

    os.chdir(res_path2)

    command_line = 'sleep 5'
    data = subprocess.run(command_line, shell=True, check=True, timeout=3600, universal_newlines=True)
    data.check_returncode()

    os.chdir(save_dir)
    logger.info("{}, SUCCESS, end of")
    return None


@shared_task(bind=True, name='tasks.create_init_rp')
def log_init_message(self, *args, **kwargs):
    object_and_method = "Tasks.create_init_rp"
    logger.info("{}, start of".format(object_and_method))
    logger.info("{}, length args : {}".format(object_and_method, len(args)))
    logger.info("{}, length kwargs : {}".format(object_and_method, len(kwargs)))
    node_id = kwargs["node_id"]
    destination_node = Node.objects.get(pk=node_id)
    noos_model = destination_node.model
    simulation_demand_id = kwargs["simulation_demand_pk"]
    simulation_demand = SimulationDemand.objects.get(pk=simulation_demand_id)
    logger.info("{}, logging message {}".format(object_and_method, kwargs["message"]))
    rp = LoggingMessage(simulation_demand=simulation_demand, node=destination_node, status="INIT-SIMULATION",
                        noos_model=noos_model, message=kwargs["message"])
    rp.save(force_insert=True)
    logger.info("{}, end of".format(object_and_method))
    return None


@shared_task(bind=True, name='tasks.send_demand_to_node')
def send_demand_to_node(self, *args, **kwargs):
    """
    This is the Celery task that will send a simulation demand to a Node
    :param self:
    :param kwargs:
    :return:
    """

    destination_node_id = kwargs["node_id"]
    destination_node = Node.objects.get(pk=destination_node_id)
    destination_node.add_simulation_demand(kwargs["thejsontxt"], NOOS_USER)
    return None


@shared_task(bind=True, name='tasks.upload_processing')
def upload_processing(self, *args, **kwargs):
    """
    Executes on Node. Uploads Forcing results to Central and sends LoggingMessage to Central
    Is linked to signals
     * failure_handler
     * success_handler
    :param self:
    :param kwargs:
    :return:
    """

    # TODO Change the way archive is built to limit directory levels

    name_and_method = "tasks upload_processing"
    logger.info("{}, start of".format(name_and_method))
    save_dir = os.getcwd()

    logger.info("{}, args contains : {}".format(name_and_method, args))
    logger.info("{}, kwargs contains : {}".format(name_and_method, kwargs))
    simulation_demand_id = str(kwargs["simulation_demand_id"])
    os.chdir(REQUESTS_DIR)
    res_path1 = "{}".format(simulation_demand_id)
    simulation_demand_archive = "sim:{}-mod:{}-for:{}.tgz".format(simulation_demand_id, kwargs["noos_model_code"],
                                                                  kwargs["couple_code"])

    the_archive = tarfile.open(name=simulation_demand_archive, mode='x:gz')
    the_archive.add(res_path1)
    the_archive.close()
    archive_path = the_archive.name
    os.chdir(save_dir)

    command_line = 'python {}/noos_services/tasks/upload.py -i {}'.format(BASE_DIR, archive_path)
    command_line_to_run = shlex.split(command_line)
    data = subprocess.run(command_line_to_run, shell=False, check=True, timeout=3600, universal_newlines=True)

    message_txt = "Simulation demand results uploaded for demand {}, forcing_couple {}".format(
        kwargs["simulation_demand_id"], kwargs["forcing_couple_id"])
    message_parameters = {"simulation_demand_id": kwargs["simulation_demand_id"],
                          "forcing_couple_id": kwargs["forcing_couple_id"],
                          "node_id": ENV_DICT[NOOS_NODE_ID],
                          "noos_model_id": kwargs["noos_model_id"],
                          "status": "FORCING-FILE-UPLOADED",
                          "message": message_txt,
                          "filename": simulation_demand_archive}

    logger.info("{}, end of".format(name_and_method))

    return message_parameters


class Job:
    """
    A class meant to execute Jobs, which group several Celery tasks at a time
    """

    @staticmethod
    def job(simulation_demand):
        """
        A method designed to execute a simulation demand using a list of couples of forcings.
        For each couple of forcings that must be used by the model, the method will save the simulation demand file in
        the right directory and call for the next steps as Celery tasks.
        :param simulation_demand: The object containing the details of the forcing
        :return:
        """

        object_name_and_method = "Job.job"
        logger.info("{}, start of".format(object_name_and_method))
        this_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
        noos_model_id = this_node.model.pk

        logger.info("{}, simulation_demand.json_txt:{}".format(object_name_and_method, simulation_demand.json_txt))
        forcing_couples = ForcingCouple.objects.filter(noos_model=noos_model_id).filter(is_active=True)
        noos_model_code = this_node.model.code
        simulation_demand_id = simulation_demand.pk

        # Get path to output directory of this request
        res_path1 = os.path.join(REQUESTS_DIR, str(simulation_demand_id))

        for aforcing_couple in forcing_couples:
            couple_code = aforcing_couple.couple_code()
            forcing_couple_id = aforcing_couple.pk

            # Create the output directory for this forcing couple
            res_path2 = os.path.join(res_path1, couple_code)
            try:
                os.mkdir(res_path2)
            except FileExistsError as exc:
                logger.error(
                    "{}, Strange ??? directory {} already exists ???".format(object_name_and_method, res_path2))
            except OSError as exc:
                logger.error(
                    "{}, not able to create directory, {}, error : {}".format(object_name_and_method, res_path2,
                                                                              exc.strerror))
                raise

            # Adding the couple of forcings in the json input file
            json_obj = json.loads(simulation_demand.json_txt)
            json_obj["model_set_up"]["ocean_forcing"] = aforcing_couple.oceanical.code
            json_obj["model_set_up"]["wind_forcing"] = aforcing_couple.meteorological.code
            new_json_str = json.dumps(json_obj)

            file_path = os.path.join(res_path2, "{}.json".format(simulation_demand_id))
            parameters_file = open(file_path, 'w')
            parameters_file.write(new_json_str)
            parameters_file.close()
            # OK, input file should be ready

            the_message = "Started to execute forcing_couple {} for simulation demand {}".format(couple_code,
                                                                                                 simulation_demand.pk)
            rp = LoggingMessage(simulation_demand=simulation_demand, node=this_node, status="FORCING-PROCESSING",
                                noos_model=this_node.model, message=the_message)
            rp.save(force_insert=True)

            netcdf_processing_dict = {"simulation_demand_id": simulation_demand_id, "couple_code": couple_code,
                                      "forcing_couple_id": forcing_couple_id, "immutable": True}
            net_cdf_task = netcdf_processing.signature(kwargs=netcdf_processing_dict)

            local_processing_dict = {"simulation_demand_id": simulation_demand_id, "couple_code": couple_code,
                                     "forcing_couple_id": forcing_couple_id, "noos_model_id": noos_model_id,
                                     "immutable": True}
            local_task = local_processing.signature(kwargs=local_processing_dict)

            upload_processing_dict = {"simulation_demand_id": simulation_demand_id,"couple_code": couple_code,
                                      "forcing_couple_id": forcing_couple_id, "noos_model_id": noos_model_id,
                                      "noos_model_code": noos_model_code, "log_message": "", "immutable": True}
            upload_task = upload_processing.signature(kwargs=upload_processing_dict)
            chain_local = chain(net_cdf_task, local_task, upload_task)
            chain_local()

        logger.info("{}, end of".format(object_name_and_method))
        return 0

    @staticmethod
    def demand_init_job(simulation_demand):
        """
        Method that will create a list of Celery tasks and then chain this list to send all Nodes a Simulation Demand

        :param simulation_demand: The Simulation Demand
        :return:
        """
        objectandmethod = "Job.demand_init_job"
        logger.info("{}, start of".format(objectandmethod))

        message_tmp = "{} Sending Simulation demand {} to node {}:{}"

        # the json_txt of the simulation demand which has no "id" yet
        # I convert this into a dict object
        simulation_demand_dict = json.loads(simulation_demand.json_txt)

        the_nodes = Node.objects.filter(is_active=True)

        result_simulation_demand_dict = {}

        # Here I get back the id of the simulation demand and I put it into the object I want to send
        simulation_demand_dict["id"] = simulation_demand.id

        # The object has to be transformed back into text(json) and added as a "json_txt" property to the object
        # I want to send
        simulation_demand_as_json_with_id = json.dumps(simulation_demand_dict, separators=(',', ':'))
        result_simulation_demand_dict["json_txt"] = simulation_demand_as_json_with_id
        result_simulation_demand_json = json.dumps(result_simulation_demand_dict, separators=(',', ':'))

        logger.info("{}, json text {}".format(objectandmethod, result_simulation_demand_json))

        task_list = []
        for destination_node in the_nodes:
            noos_model = destination_node.model.code
            noos_model_pk = destination_node.model.pk
            message_to_log = message_tmp.format(objectandmethod, simulation_demand.pk, noos_model, noos_model_pk)
            # logger.info("{}, message_to_log : {}".format(objectandmethod, message_to_log))
            # logger.info("{}, message_to_log {}".format(objectandmethod, result_simulation_demand_json))
            # Logging the simulation demand
            the_message_dict = {"node_id": destination_node.pk,
                                "simulation_demand_pk": simulation_demand.pk,
                                "message": message_to_log,
                                "immutable": True}
            the_simulation_demand_dict = {"thejsontxt": result_simulation_demand_json,
                                          "node_id": destination_node.pk,
                                          "immutable": True}
            task_list.append(log_init_message.signature(kwargs=the_message_dict))
            task_list.append(send_demand_to_node.signature(kwargs=the_simulation_demand_dict))

        chain_local = chain(task_list)
        logger.info("{}, end of".format(objectandmethod))

        # Define tasks
        chain_local()

        return 0
