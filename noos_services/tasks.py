import json
import os
import subprocess
import tarfile

from background_task import background
from celery import shared_task, chain
from celery.utils.log import get_task_logger

from noosDrift.settings import BASE_DIR, ENV_DICT, NOOS_MME_MODEL, NOOS_NODE_ID, NOOS_MME_CMD, NOOS_NODE_MODEL_CMD, \
    NOOS_NODE_PREPROCESSING_CMD, NOOS_MAPS_CMD, NOOS_NODE_POSTPROCESSING_CMD, NOOS_RESULTS_DIR, NOOS_USER
from noos_services.models import ForcingCouple, LoggingMessage, Node, NoosModel, SimulationDemand
from noos_services.ns_const import MemorySimulationDemand, SignalsConst, StatusConst, OtherConst

logger = get_task_logger(__name__)


@background(schedule=1020)  # 1020 is 17 minutes
def check_demand(simulation_id):
    """
    Executed on Central. This method creates a task scheduled to be executed in 17 minutes (default).
    The task checks if an MME analysis has been performed (presence of START_ANALYSIS message) for a particular demand
    (simulation_id).
    If not so, the method will instantiate a LoggingMessage which will trigger the MME analysis for this demand using
    all responses transmitted by the nodes at this point.
      - Analysis is triggered when the LoggingMessage instance is saved
      - No Analysis will be triggered if it has already been started (presence of START_ANALYSIS message)
    :param simulation_id: The id of the simulation demand to be checked
    :return:
    """
    name_and_method = "Tasks.check_demand"
    logger.info("{}, start of".format(name_and_method))
    logger.info("{}, waiting for demand {}".format(name_and_method, simulation_id))
    the_simulation = SimulationDemand.objects.get(pk=simulation_id)
    messages = LoggingMessage.objects.filter(simulation_demand=the_simulation, status=StatusConst.START_ANALYSIS)
    central_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
    mme_model = NoosModel.objects.get(pk=ENV_DICT[NOOS_MME_MODEL])

    if len(messages) == 0:
        new_log_message = LoggingMessage(
            node=central_node,
            simulation_demand=the_simulation,
            noos_model=mme_model,
            status=StatusConst.START_ANALYSIS,
            message=StatusConst.START_ANALYSIS
        )
        new_log_message.save()

    logger.info("{}, end of".format(name_and_method))


@shared_task(bind=True, name='tasks.node_copy_maps')
def node_copy_maps(self, *args, **kwargs):
    """
    A method designed to copy maps for viewer.
    :param self:
    :param args:
    :param kwargs:
    :return:
    """
    object_and_name = "Tasks node_copy_maps"
    logger.info("{}, start of".format(object_and_name))
    parameters_dict = kwargs['parameters_dict']
    res_path1 = os.path.join(NOOS_RESULTS_DIR, parameters_dict[SignalsConst.JSON_FILE])
    command_line = NOOS_MAPS_CMD.copy()
    command_line.append(res_path1)
    data = subprocess.run(command_line, shell=False, check=True, timeout=3600, universal_newlines=True)
    data.check_returncode()
    logger.info("{}, SUCCESS, end of".format(object_and_name))
    return None


@shared_task(bind=True, name='tasks.node_pre_processing')
def node_pre_processing(self, *args, **kwargs):
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
    object_and_name = "Tasks node_pre_processing"
    logger.info("{}, start of".format(object_and_name))
    parameters_dict = kwargs['parameters_dict']
    res_path1 = os.path.join(NOOS_RESULTS_DIR, parameters_dict[SignalsConst.JSON_FILE])
    command_line = NOOS_NODE_PREPROCESSING_CMD.copy()
    command_line.append(res_path1)
    data = subprocess.run(command_line, shell=False, check=True, timeout=3600, universal_newlines=True)
    logger.error("preproc error {}".format(data.stderr))
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
    logger.info("{}, kwargs: {}".format(name_and_method, kwargs))
    parameters_dict = kwargs['parameters_dict']
    logger.info("{}, SignalsConst.JSON_FILE: {}".format(name_and_method, parameters_dict[SignalsConst.JSON_FILE]))

    res_path1 = os.path.join(NOOS_RESULTS_DIR, parameters_dict[SignalsConst.JSON_FILE])
    command_line = NOOS_NODE_MODEL_CMD.copy()
    command_line.append(res_path1)
    data = subprocess.run(command_line, shell=False, check=True, timeout=3600, universal_newlines=True)
    data.check_returncode()
    logger.info("{}, SUCCESS, end of".format(name_and_method))
    return None


@shared_task(bind=True, name='tasks.node_post_processing')
def node_post_processing(self, *args, **kwargs):
    """
    A method to call for a postprocessing operation that creates netCDF files and places them in the adequate directory
    :param self:
    :param args:
    :param kwargs:
    :return:
    """
    object_and_name = "Tasks node_post_processing"
    logger.info("{}, start of".format(object_and_name))
    parameters_dict = kwargs['parameters_dict']
    res_path1 = os.path.join(NOOS_RESULTS_DIR, parameters_dict[SignalsConst.JSON_FILE])
    command_line = NOOS_NODE_POSTPROCESSING_CMD.copy()
    command_line.append(res_path1)
    data = subprocess.run(command_line, shell=False, check=True, timeout=3600, universal_newlines=True)
    data.check_returncode()
    logger.info("{}, SUCCESS, end of".format(object_and_name))
    return None


@shared_task(bind=True, name='tasks.mme_processing')
def mme_processing(self, *args, **kwargs):
    """
    Runs on MME Node. This method will really spawn the analysis of the data sent by the nodes
    Is linked to signals
      * failure_handler
      * revoked_handler
      * success_handler
    Signal success_handler will trigger loading the results of the MME Analysis into the DB using an "ANALYSIS OK"
    message
    :param self:
    :param args:
    :param kwargs:
    :return:
    """
    name_and_method = "Tasks.tasks mme_processing"
    logger.info("{}, start of".format(name_and_method))
    simulation_id = kwargs[SignalsConst.SIMULATION_DEMAND_ID]
    inputfolder = os.path.join(NOOS_RESULTS_DIR, format(simulation_id))
    mme_model = ENV_DICT[NOOS_MME_MODEL]
    logger.info("{}, mme_model {}".format(name_and_method, mme_model))
    command_line = NOOS_MME_CMD.copy()
    command_line.append(inputfolder)
    logger.info("{}, will try this {}".format(name_and_method, " ".join(command_line)))

    data = subprocess.run(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, check=True,
                          timeout=3600, universal_newlines=True)
    data.check_returncode()

    message_parameters = {SignalsConst.SIMULATION_DEMAND_ID: simulation_id,
                          SignalsConst.NODE_ID: ENV_DICT[NOOS_NODE_ID],
                          SignalsConst.NOOS_MODEL_ID: mme_model,
                          SignalsConst.STATUS: StatusConst.ANALYSIS_OK,
                          SignalsConst.MESSAGE: ""
                          }
    logger.info("{}, end of OK".format(name_and_method))
    return message_parameters


@shared_task(bind=True, name='tasks.create_init_rp')
def create_init_rp(self, *args, **kwargs):
    object_and_method = "Tasks.create_init_rp"
    logger.info("{}, start of".format(object_and_method))
    # logger.info("{}, length args : {}".format(object_and_method, len(args)))
    # logger.info("{}, length kwargs : {}".format(object_and_method, len(kwargs)))
    # logger.info("{}, kwargs : {}".format(object_and_method, kwargs))
    node_id = kwargs["node_id"]
    destination_node = Node.objects.get(pk=node_id)
    noos_model = destination_node.model
    simulation_demand_id = kwargs[SignalsConst.SIMULATION_DEMAND_ID]
    simulation_demand = SimulationDemand.objects.get(pk=simulation_demand_id)
    logger.info("{}, logging message {}".format(object_and_method, kwargs[SignalsConst.MESSAGE]))
    rp = LoggingMessage(simulation_demand=simulation_demand, node=destination_node,
                        status=StatusConst.INIT_SIMULATION, noos_model=noos_model,
                        message=kwargs[SignalsConst.MESSAGE])
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
    object_and_method = "Tasks.send_demand_to_node"
    logger.info("{}, start of".format(object_and_method))

    destination_node_id = kwargs[SignalsConst.NODE_ID]
    destination_node = Node.objects.get(pk=destination_node_id)
    logger.info("{}, kwargs : {}".format(object_and_method, kwargs))
    destination_node.add_simulation_demand(kwargs[SignalsConst.THEJSONTXT], NOOS_USER)
    logger.info("{}, end of".format(object_and_method))
    return None


@shared_task(bind=True, name='tasks.upload_processing')
def upload_processing(self, *args, **kwargs):
    """
    Executes on Node. Uploads Forcing results to Central and sends LoggingMessage to Central
    Is linked to signals which will send messages back to the central
     * failure_handler
     * success_handler
    :param self:
    :param kwargs:
    :return:
    """

    name_and_method = "tasks upload_processing"
    logger.info("{}, start of".format(name_and_method))
    save_dir = os.getcwd()
    parameters_dict = kwargs['parameters_dict']
    logger.info("{}, args contains : {}".format(name_and_method, args))
    logger.info("{}, kwargs contains : {}".format(name_and_method, kwargs))
    simulation_demand_id = parameters_dict[SignalsConst.SIMULATION_DEMAND_ID]
    nc_file = "noosdrift_{}_{}_{}.nc".format(simulation_demand_id, parameters_dict[
        SignalsConst.NOOS_MODEL_CODE], parameters_dict[SignalsConst.COUPLE_CODE])
    # To get the result dir, subtract the extention

    forcing_couple_id = parameters_dict[SignalsConst.FORCING_COUPLE_ID]
    os.chdir(NOOS_RESULTS_DIR)
    simulation_demand_archive = "noosdrift_{}_{}_{}.tgz".format(simulation_demand_id, parameters_dict[
        SignalsConst.NOOS_MODEL_CODE], parameters_dict[SignalsConst.COUPLE_CODE])

    the_archive = tarfile.open(name=simulation_demand_archive, mode='x:gz')
    the_archive.add(parameters_dict[SignalsConst.JSON_FILE])
    the_archive.add(nc_file)
    the_archive.close()
    os.chdir(save_dir)
    archive_path = os.path.join(NOOS_RESULTS_DIR, simulation_demand_archive)

    command_line = ["python", "{}/noos_services/tasks/upload.py".format(BASE_DIR), "-i", "{}".format(archive_path)]

    try:
        # subprocess.run(command_line_to_run, shell=False, check=True, timeout=3600, universal_newlines=True)
        data = subprocess.run(command_line, shell=False, check=True, timeout=3600, universal_newlines=True)
        logger.info("{}, args: {}".format(name_and_method, data.args))
        logger.info("{}, stdout: {}".format(name_and_method, data.stdout))
        logger.info("{}, stderr: {}".format(name_and_method, data.stderr))
        logger.info("{}, returncode: {}".format(name_and_method, data.returncode))
        data.check_returncode()
    except subprocess.SubprocessError as e:
        logger.error("{}, {}, end of".format(name_and_method, e))
        raise e

    message_txt = "Simulation demand results uploaded for demand {}, forcing_couple {}".format(
        simulation_demand_id, forcing_couple_id)
    message_parameters = {SignalsConst.SIMULATION_DEMAND_ID: simulation_demand_id,
                          SignalsConst.FORCING_COUPLE_ID: forcing_couple_id,
                          SignalsConst.NODE_ID: ENV_DICT[NOOS_NODE_ID],
                          SignalsConst.NOOS_MODEL_ID: parameters_dict[SignalsConst.NOOS_MODEL_ID],
                          SignalsConst.STATUS: StatusConst.FORCING_FILE_UPLOADED,
                          SignalsConst.MESSAGE: message_txt,
                          SignalsConst.FILENAME: simulation_demand_archive,
                          SignalsConst.NOOS_MODEL_CODE: parameters_dict[SignalsConst.NOOS_MODEL_CODE],
                          SignalsConst.COUPLE_CODE: parameters_dict[SignalsConst.COUPLE_CODE]
                          }

    logger.info("{}, message parameters, {}".format(name_and_method, message_parameters))
    logger.info("{}, end of".format(name_and_method))

    return message_parameters


@shared_task(bind=True, name='tasks.ending_simulation')
def ending_simulation(self, *args, **kwargs):
    logger.info("END")


class Job:
    """
    A class meant to execute Jobs, which group several Celery tasks at a time
    """

    @staticmethod
    def generate_strategy(parameters_dict):
        node_id = ENV_DICT[NOOS_NODE_ID]
        all_strategies = {
            2: Job.four_steps_strategy,  # The Belgian Node
            3: Job.two_steps_strategy,  # The French Node
            4: Job.two_steps_strategy  # The Norwegian Node
        }
        initiated_strategy = all_strategies[node_id](parameters_dict)
        return initiated_strategy

    @staticmethod
    def four_steps_strategy(parameters_dict):
        name_and_method = "Job.four_steps_strategy"
        logger.info("{}, start".format(name_and_method))

        # Prepare signature of copy_maps
        copy_maps_task = node_copy_maps.si(parameters_dict=parameters_dict)

        # Prepare signature of pre-processing
        pre_processing_task = node_pre_processing.si(parameters_dict=parameters_dict)

        # Prepare signature of local processing
        local_task = local_processing.si(parameters_dict=parameters_dict)

        # Prepare signature of pre-processing
        post_processing_task = node_post_processing.si(parameters_dict=parameters_dict)

        # Prepare signature of upload processing
        upload_task = upload_processing.si(parameters_dict=parameters_dict)

        logger.info("{}, end".format(name_and_method))
        return [copy_maps_task, pre_processing_task, local_task, post_processing_task, upload_task]

    @staticmethod
    def two_steps_strategy(parameters_dict):
        name_and_method = "Job.two_steps_strategy"
        logger.info("{}, start".format(name_and_method))

        # Prepare signature of local processing
        local_task = local_processing.si(parameters_dict=parameters_dict)

        # Prepare signature of upload processing
        upload_task = upload_processing.si(parameters_dict=parameters_dict)

        logger.info("{}, end".format(name_and_method))
        return [local_task, upload_task]

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

        for aforcing_couple in forcing_couples:
            couple_code = aforcing_couple.couple_code()
            requ_dirname = "noosdrift_{}_{}_{}".format(simulation_demand_id, noos_model_code, couple_code)
            json_filename = "{}.json".format(requ_dirname)

            res_path2 = os.path.join(NOOS_RESULTS_DIR, json_filename)

            forcing_couple_id = aforcing_couple.pk

            # Adding the couple of forcings in the json input file
            json_obj = simulation_demand.json_txt
            json_obj[MemorySimulationDemand.SIMULATION_DESCRIPTION][
                MemorySimulationDemand.REQUEST_ID] = simulation_demand_id
            json_obj[MemorySimulationDemand.MODEL_SETUP][
                MemorySimulationDemand.OCEAN_FORCING] = aforcing_couple.oceanical.code
            json_obj[MemorySimulationDemand.MODEL_SETUP][
                MemorySimulationDemand.WIND_FORCING] = aforcing_couple.meteorological.code
            json_obj[MemorySimulationDemand.MODEL_SETUP][
                MemorySimulationDemand.MODEL] = noos_model_code
            new_json_str = json.dumps(json_obj)

            try:
                parameters_file = open(res_path2, 'w')
                parameters_file.write(new_json_str)
                parameters_file.close()
            except FileExistsError:
                logger.error(
                    "{}, Strange ??? file {} already exists ???".format(object_name_and_method, res_path2))
            except OSError as exc:
                logger.error(
                    "{}, not able to create file, {}, error : {}".format(object_name_and_method, res_path2,
                                                                         exc.strerror))
                raise exc

            os.chmod(res_path2, 0o664)

            # OK, input file should be ready

            the_message = "Started to execute forcing_couple {} for simulation demand {}".format(couple_code,
                                                                                                 simulation_demand.pk)
            rp = LoggingMessage(simulation_demand=simulation_demand, node=this_node,
                                status=StatusConst.FORCING_PROCESSING, noos_model=this_node.model,
                                message=the_message)
            rp.save(force_insert=True)

            parameters_dict = {SignalsConst.SIMULATION_DEMAND_ID: simulation_demand_id,
                               SignalsConst.COUPLE_CODE: couple_code,
                               SignalsConst.FORCING_COUPLE_ID: forcing_couple_id,
                               SignalsConst.NOOS_MODEL_ID: noos_model_id,
                               SignalsConst.NOOS_MODEL_CODE: noos_model_code,
                               SignalsConst.LOG_MESSAGE: "",
                               SignalsConst.JSON_FILE: json_filename,
                               SignalsConst.IMMUTABLE: True}

            task_list = Job.generate_strategy(parameters_dict)
            chain_local = chain(task_list)
            chain_local()

        logger.info("{}, end of".format(object_name_and_method))
        return 0

    @staticmethod
    def execute_mme(simulation_demand):
        """
        Runs on MME Node (probably same as RBINS-Node) This method will start a job to call the MME analysis module
        :param simulation_demand: A SimulationDemand object
        :return:
        """

        object_name_and_method = "Job.execute_mme"
        logger.info("{}, start of".format(object_name_and_method))

        mme_processing_dict = {SignalsConst.SIMULATION_DEMAND_ID: simulation_demand.id, SignalsConst.IMMUTABLE: True}
        mme_task = mme_processing.signature(kwargs=mme_processing_dict)
        chain_local = chain(mme_task)
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

        # The json_txt of the simulation demand which has no "id" yet
        simulation_demand_json_level1 = simulation_demand.json_txt

        the_nodes = Node.objects.filter(is_active=True)

        result_simulation_demand_json = dict()

        # Here I get back the id of the simulation demand and I put it into the object I want to send
        simulation_demand_json_level1["id"] = simulation_demand.id

        result_simulation_demand_json["json_txt"] = simulation_demand_json_level1

        logger.info("{}, json text {}".format(objectandmethod, simulation_demand_json_level1))

        task_list = []
        for destination_node in the_nodes:
            noos_model = destination_node.model.code
            noos_model_pk = destination_node.model.pk
            message_to_log = message_tmp.format(objectandmethod, simulation_demand.pk, noos_model, noos_model_pk)
            # logger.info("{}, message_to_log : {}".format(objectandmethod, message_to_log))
            # logger.info("{}, message_to_log {}".format(objectandmethod, result_simulation_demand_json))
            # Logging the simulation demand
            the_message_dict = {SignalsConst.NODE_ID: destination_node.pk,
                                SignalsConst.SIMULATION_DEMAND_ID: simulation_demand.pk,
                                SignalsConst.MESSAGE: message_to_log,
                                SignalsConst.IMMUTABLE: True}
            the_simulation_demand_dict = {SignalsConst.THEJSONTXT: result_simulation_demand_json,
                                          SignalsConst.NODE_ID: destination_node.pk,
                                          SignalsConst.IMMUTABLE: True}

            task_list.append(create_init_rp.signature(kwargs=the_message_dict))
            task_list.append(send_demand_to_node.signature(kwargs=the_simulation_demand_dict))

        if task_list:
            demand_result_dir = os.path.join(NOOS_RESULTS_DIR, str(simulation_demand.pk))
            try:
                os.mkdir(demand_result_dir)
                os.chmod(demand_result_dir, 0o775)
            except FileExistsError:
                logger.error(
                    "{}, Strange ??? dir {} already exists ???".format(objectandmethod, demand_result_dir))
            except OSError as exc:
                logger.error(
                    "{}, not able to create directory, {}, error : {}".format(objectandmethod, demand_result_dir,
                                                                              exc.strerror))
                raise

            demand_mme_output_dir = os.path.join(demand_result_dir, OtherConst.MME_OUTPUT)
            try:
                os.mkdir(demand_mme_output_dir)
                os.chmod(demand_mme_output_dir, 0o775)
            except FileExistsError:
                logger.error(
                    "{}, Strange ??? dir {} already exists ???".format(objectandmethod, demand_mme_output_dir))
            except OSError as exc:
                logger.error(
                    "{}, not able to create directory, {}, error : {}".format(objectandmethod, demand_mme_output_dir,
                                                                              exc.strerror))
                raise

            parameters_dir = os.path.join(demand_result_dir, OtherConst.PARAMETERS_DIR_NAME)
            try:
                os.mkdir(parameters_dir)
                os.chmod(parameters_dir, 0o775)
            except FileExistsError:
                logger.error(
                    "{}, Strange ??? dir {} already exists ???".format(objectandmethod, parameters_dir))
            except OSError as exc:
                logger.error(
                    "{}, not able to create directory, {}, error : {}".format(objectandmethod, parameters_dir,
                                                                              exc.strerror))
                raise

            chain_local = chain(task_list)
            logger.info("{}, end of".format(objectandmethod))

            # Define tasks
            chain_local()
        else:
            logger.info("No destination node -> End of propagation")

        return 0
