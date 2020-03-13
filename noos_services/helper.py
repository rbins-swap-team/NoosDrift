import datetime as dt
import json
import logging
import os
import pytz
import re
import tarfile
import zipfile

from noos_services.tasks import check_demand
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMessage
from django.db.models import Count
from django.template.loader import render_to_string
from noosDrift.settings import ENV_DICT, CENTRAL_DOMAIN, MEDIA_DIR, MEDIA_URL, NOOS_FTPDIR, NOOS_MME_ID, NOOS_NODE_ID, \
    NOOS_MME_MODEL, MAIL_ADMIN_NOOSDRIFT, NOOS_RESULTS_DIR, NOOS_USER, ODIN_MAILANSWERACCOUNT
from noos_services import tasks
from noos_services.models import Forcing, ForcingCouple, LoggingMessage, Node, NoosModel, SimulationCloud, \
    SimulationDemand, SimulationElement, SimulationMetadata, UploadedFile
from noos_services.ns_const import JsonMmeElementsConst, JsonSimulationElementsConst, MemorySimulationDemand, \
    OtherConst, StatusConst, SignalsConst
logger = logging.getLogger(__name__)


class Helper:

    @staticmethod
    def simulations_list():
        object_and_method = "Helper.simulations_list"
        # logger.info("{}, start".format(object_and_method))
        init_messages = LoggingMessage.objects.values('simulation_demand').filter(
            status=StatusConst.INIT_SIMULATION, simulation_demand__archived=False).annotate(
            Count('simulation_demand'))
        # logger.debug("{}, messages : {}".format(object_and_method, init_messages))
        all_sims_dict = {}
        for a_message in init_messages:
            simulation_id = a_message['simulation_demand']

            count_err_messages = LoggingMessage.objects.filter(simulation_demand=simulation_id).filter(
                status__in=[StatusConst.NODE_ERROR, StatusConst.RESULT_FILE_ERROR]).count()
            count_uploaded_messages = LoggingMessage.objects.filter(simulation_demand=simulation_id).filter(
                status=StatusConst.FORCING_FILE_UPLOADED).count()
            count_end_messages = LoggingMessage.objects.filter(simulation_demand=simulation_id).filter(
                status=StatusConst.NODE_END_PROCESSING).count()

            try:
                asimulation = SimulationDemand.active_objects.get(pk=simulation_id)
                simdict = {}
                simdict.update({MemorySimulationDemand.USERNAME: asimulation.user.username})
                json_txt = asimulation.json_txt
                simdict.update({MemorySimulationDemand.TAGS: ", ".join(
                    json_txt[MemorySimulationDemand.SIMULATION_DESCRIPTION][MemorySimulationDemand.TAGS])})
                simdict.update({MemorySimulationDemand.ID: asimulation.id})
                simdict.update({MemorySimulationDemand.TITLE: json_txt[MemorySimulationDemand.SIMULATION_DESCRIPTION][
                    MemorySimulationDemand.TITLE]})
                simdict.update({MemorySimulationDemand.STATUS: asimulation.status})
                simdict.update({MemorySimulationDemand.CREATED_TIME: asimulation.created_time})
                simdict.update({MemorySimulationDemand.PROTECTED: asimulation.protected})
                simdict.update({MemorySimulationDemand.ERROR_MESSAGES: count_err_messages})
                simdict.update({MemorySimulationDemand.END_PROCESS: count_end_messages})
                simdict.update({MemorySimulationDemand.UPLOAD_MESSAGES: count_uploaded_messages})

                if asimulation.status == StatusConst.OK:
                    the_url = Helper.get_zip_url(simulation_id)
                    if the_url:
                        simdict.update({MemorySimulationDemand.ZIP_URL: the_url})

                all_sims_dict[simulation_id] = simdict
            except ObjectDoesNotExist:
                logger.info("{}, simulation {} does not exist or is archived".format(object_and_method, simulation_id))

        all_ids = all_sims_dict.keys()
        sorted_ids = sorted(all_ids)
        # logger.debug("{}, sorted list : {}".format(object_and_method, sorted_ids))
        sorted_ids.sort(reverse=True)
        # logger.debug("{}, sorted reversed : {}".format(object_and_method, sorted_ids))
        sims_list = []
        for an_id in sorted_ids:
            # logger.debug("{}, adding sim : {}".format(object_and_method, an_id))
            sims_list.append(all_sims_dict[an_id])

        # logger.debug("{}, list : {}".format(object_and_method, sims_list))
        # logger.info("{}, end".format(object_and_method))
        return sims_list

    @staticmethod
    def get_zip_url(simulation_id):
        name_and_method = "Helper.get_zip_url"
        # logger.info("{}, start".format(name_and_method))
        # logger.info("{}, for {}".format(name_and_method, simulation_id))
        compiled_re = re.compile("^simulation-{}-.+zip$".format(simulation_id))
        onlyfiles = [f for f in os.listdir(MEDIA_DIR) if os.path.isfile(os.path.join(
            MEDIA_DIR, f))]
        # logger.info("{}, onlyfiles : {}".format(name_and_method, onlyfiles))
        # logger.info("{}, len(onlyfiles) : {}".format(name_and_method, len(onlyfiles)))
        # logger.info("{}, MEDIA_URL : {}".format(name_and_method, MEDIA_URL))
        if onlyfiles is None or len(onlyfiles) == 0:
            # logger.info("{}, end 01".format(name_and_method))
            return None

        onlyfiles.sort()
        for name in onlyfiles:
            if compiled_re.match(name):
                the_url = MEDIA_URL + name
                # logger.info("{}, the_url : {}".format(name_and_method, the_url))
                # logger.info("{}, end 02".format(name_and_method))
                return the_url

        # logger.info("{}, end 03".format(name_and_method))
        return None

    @staticmethod
    def node_simulation_demand_help(instance):
        """
        Helper static method, processes Simulation Demand on Node.
        :param instance: A SimultationDemand instance
        :return:
        """

        object_name = "Helper"
        object_and_method = "Helper.node_simulation_demand_help"

        # logger.info("{}: request_is_created on node, all is done".format(object_name))
        # logger.info("{}: Propagation {} received, start tasks".format(object_and_method, instance.id))
        # logger.info("{}: checking presence of results dir : {}".format(object_and_method, NOOS_RESULTS_DIR))

        if not os.path.isdir(NOOS_RESULTS_DIR):
            try:
                os.mkdir(NOOS_RESULTS_DIR)
            except OSError as exc:
                logger.error("{}, not able to create directory : {}, error {}".format(object_name, NOOS_RESULTS_DIR,
                                                                                      exc.strerror))
                raise

        job = tasks.Job()
        job.job(simulation_demand=instance)

    @staticmethod
    def end_of_line(log_instance):
        """
        Method to be executed at the end of a series of actions
        The point is to have something to end a list of calls cleanly
        :param:
        :return:
        """
        object_and_method = "Helper.end_of_line"
        logger.info("{}, start".format(object_and_method))
        logger.info("{}, End of line for demand {}".format(object_and_method, log_instance.simulation_demand.id))
        logger.info("{}, end".format(object_and_method))

    @staticmethod
    def bogus_method(simulation_demand):
        """
        Method to simulate a "sucessfull upload" answer from nodes
        This method must be called from a Django terminal to trigger a post-processing signal
        :param simulation_demand: simulation_demand.id
        :return:
        """
        object_and_method = "Helper.bogus_method"
        logger.info("{}, start".format(object_and_method))
        simulation_demand_id = simulation_demand.id
        logging_messages = LoggingMessage.objects.filter(simulation_demand=simulation_demand,
                                                         status=StatusConst.INIT_SIMULATION)
        # logger.debug("{}, Number of INIT messages : ".format(object_and_method, len(logging_messages)))
        for a_message in logging_messages:
            a_model = a_message.noos_model
            couples_list = ForcingCouple.objects.filter(noos_model=a_model, is_active=True)
            # logger.debug("{}, Number of ForcingCouples : {}".format(object_and_method, len(couples_list)))
            for a_couple in couples_list:
                simulation_demand_archive = "noosdrift_{}_{}_{}.tgz".format(simulation_demand_id,
                                                                            a_message.noos_model.code,
                                                                            a_couple.couple_code())

                this_node = a_message.node
                this_forcing = ForcingCouple.objects.get(pk=a_couple.id)

                # logger.debug("{}, sending uploaded file message to Central".format(object_and_method))

                json_str = "{}"

                uploaded_file = UploadedFile(
                    simulation=simulation_demand,
                    node=this_node,
                    noos_model=this_node.model,
                    forcing_couple=this_forcing,
                    filename=simulation_demand_archive,
                    json_txt=json_str
                )
                uploaded_file.save()

                # logger.debug("{}, uploaded file signal to Central sent".format(object_and_method))

        logger.info("{}, end of".format(object_and_method))

    @staticmethod
    def import_analysis_method(simulation_id):
        """
        Method to import analysis results if run directly in shell.
        Trigger the import by sending "ANALYSIS_OK" logging message

        :param simulation_id: simulation_demand.id
        :return:
        """
        object_and_method = "Helper.import_analysis_method"
        logger.info("{}, start".format(object_and_method))

        # logger.debug("{}, succes of MME processing happened on central".format(object_and_method))
        node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
        noos_model = NoosModel.objects.get(pk=ENV_DICT[NOOS_MME_MODEL])
        simulation_demand = SimulationDemand.objects.get(pk=simulation_id)

        message_parameters = {SignalsConst.SIMULATION_DEMAND_ID: simulation_id,
                              SignalsConst.NODE_ID: ENV_DICT[NOOS_NODE_ID],
                              SignalsConst.NOOS_MODEL_ID: ENV_DICT[NOOS_MME_MODEL],
                              SignalsConst.STATUS: StatusConst.ANALYSIS_OK,
                              SignalsConst.MESSAGE: ""
                              }

        new_message = LoggingMessage(
            node=node,
            simulation_demand=simulation_demand,
            status=StatusConst.ANALYSIS_OK,
            message=message_parameters,
            noos_model=noos_model
        )
        new_message.save()

        simulation_demand.status = "OK"
        simulation_demand.save()

        logger.info("{}, end of".format(object_and_method))

    @staticmethod
    def central_dispatching_help(simulation_demand):
        """
        Helper static method. This method is used to propagate a simulation_demand from the Central to the Nodes
           - Log the fact a simulation demand comes from the user
           - Send the simulation demand to all Nodes
        :param simulation_demand: Instance of Simulation demand object
        :return:
        """
        object_and_method_name = "Helper.central_dispatching_help"
        logger.info("{}, start of".format(object_and_method_name))
        job = tasks.Job()
        job.demand_init_job(simulation_demand=simulation_demand)
        check_demand(simulation_demand.id)
        logger.info("{}, end of".format(object_and_method_name))

    @staticmethod
    def central_uploadedfile_help(instance):
        """
        Helper static method executed on Central Node.
        Triggered by Signals after new record has been inserted in the UploadedFile table.
        This method finds the archive file that has been copied and extracts it another directory where it will be
        processed by the MME Analysis process.
        The method then creates a new instance of LoggingMessage signalling the presence of the data file uploaded by
        the Node. Creating this instance triggers the processing of the data. See reaction to new LoggingMessage
        :param instance: a UploadedFile instance
        :return:
        """
        the_class = "Helper"
        the_method = "central_uploadedfile_help"
        logger.info("{}.{}, start of".format(the_class, the_method))

        # NOOS_FTPDIR A directory part of an (s)ftp server
        # logger.debug("{}.{}, Checking request dir".format(the_class, the_method))
        if not os.path.isdir(NOOS_FTPDIR):
            err_mess = "{}, {}, path {}, does not exists".format(the_class, the_method, NOOS_FTPDIR)
            logger.error(err_mess)
            raise FileNotFoundError(err_mess)
        # logger.debug("{}.{}, request dir OK".format(the_class, the_method))

        filename_noext = instance.filename[:-4]  # the file is an archive ending in '.tgz'

        nc_filename = "{}.nc".format(filename_noext)  # the name of the file to extract
        json_filename = "{}.json".format(filename_noext)  # the name of the file to extract

        sim_file_path = os.path.join(NOOS_FTPDIR, instance.filename)  # full path to the archive on the file system

        # logger.debug("{}.{}, Checking file : {}".format(the_class, the_method, sim_file_path))
        if not os.path.isfile(sim_file_path):
            err_mess = "{}, {}, path {}, does not exists".format(the_class, the_method, sim_file_path)
            logger.error(err_mess)
            raise FileNotFoundError(err_mess)
        # logger.debug("{}.{}, {} OK".format(the_class, the_method, sim_file_path))

        save_dir = os.getcwd()
        # NOOS_RESULTS_DIR A directory part of the MME Analysis machine
        os.chdir(NOOS_RESULTS_DIR)
        dest_dir = os.path.join(NOOS_RESULTS_DIR, str(instance.simulation.id))  # this will be the directory for the
        # results of demand (simulation_id)
        parameters_dir = os.path.join(dest_dir, OtherConst.PARAMETERS_DIR_NAME)  # this will be a subfolder where the
        # simulation parameters  will be stored
        json_file_path = os.path.join(parameters_dir, json_filename)  # this is the name of the model parameter file

        logger.debug("{}.{} Saved work dir : {}".format(the_class, the_method, save_dir))
        logger.debug("{}.{} Current dir (results) : {}".format(the_class, the_method, os.getcwd()))
        logger.debug("{}.{} dest_dir : {}".format(the_class, the_method, dest_dir))
        logger.debug("{}.{} parameters_dir : {}".format(the_class, the_method, parameters_dir))
        logger.debug("{}.{} json_file_path : {}".format(the_class, the_method, json_file_path))

        os.chdir(dest_dir)  # changing to result dir of the demand
        logger.debug("{}.{} Current dir (results) : {}".format(the_class, the_method, os.getcwd()))
        archive_file = tarfile.open(sim_file_path, mode="r:gz")  # opening an archive file object for the archive
        extrnc = archive_file.extractfile(nc_filename)  # finding file ".*nc$" object in the archive
        logger.debug("{}.{} archive_file : {}".format(the_class, the_method, archive_file))
        logger.debug("{}.{} extrnc : {}".format(the_class, the_method, extrnc))
        dest_file = open(nc_filename, 'wb')  # creating a destination file object on the filesystem for the ".*nc$" file
        # of the archive
        for lines in extrnc:
            dest_file.write(lines)  # writing data to the destination file object

        dest_file.close()
        os.chmod(nc_filename, 0o775)
        extrnc.close()

        extrjson = archive_file.extractfile(json_filename)  # finding file ".*json$" object in the archive
        dest_file = open(json_file_path, 'wb')  # creating a destination file object on the filesystem for the
        # ".*json$" file of the archive
        for lines in extrjson:
            dest_file.write(lines)  # writing data to the destination file object

        dest_file.close()
        os.chmod(json_file_path, 0o775)
        extrjson.close()
        archive_file.close()

        os.chdir(save_dir)

        name_data = filename_noext.split('_')
        sim_id = name_data[1]
        model_id = NoosModel.objects.get(code=name_data[2])
        node_id = Node.objects.get(model_id=model_id)
        forcing1_id = Forcing.objects.get(code=name_data[3])
        forcing2_id = Forcing.objects.get(code=name_data[4])
        forcing_couple_id = ForcingCouple.objects.get(noos_model_id=model_id,
                                                      oceanical_id=forcing1_id,
                                                      meteorological_id=forcing2_id)

        message = "Simulation demand results uploaded for demand {}, forcing_couple {}".format(sim_id,
                                                                                               forcing_couple_id)

        log = LoggingMessage(simulation_demand=instance.simulation,
                             node=node_id,
                             status=StatusConst.FORCING_FILE_UPLOADED,
                             noos_model=model_id,
                             forcing_couple=forcing_couple_id,
                             message=message)
        log.save()

        logger.info("{}.{}, end of".format(the_class, the_method))
        return None

    @staticmethod
    def ready_for_analysis(log_instance):
        """
        Inner method on Central to check the FORCING_FILE_UPLOADED messages for a simulation demand.
        The output is wether all active nodes have sent a FORCING_FILE_UPLOADED or a NODE_ERROR message for a
        particular demand.
        :param log_instance:
        :return: a list of booleans with [is the demand being analysed?, have all nodes answered?,
        do all nodes answer with an error?]
        """
        object_and_method = "Helper.check_all_end_responses"
        logger.info("{}, start of".format(object_and_method))
        being_analysed = False
        all_answered = True
        all_errors = True
        analysis_message = LoggingMessage.objects.filter(simulation_demand=log_instance.simulation_demand,
                                                         status__in=[StatusConst.START_ANALYSIS])

        if len(analysis_message) != 0:
            being_analysed = True
            return [being_analysed, all_answered, all_errors]

        active_couples = ForcingCouple.objects.filter(is_active=True)
        logger.info("{}, before loop".format(object_and_method))
        for acouple in active_couples:
            node_answer = LoggingMessage.objects.filter(simulation_demand=log_instance.simulation_demand,
                                                        status__in=[StatusConst.FORCING_FILE_UPLOADED,
                                                                    StatusConst.NODE_ERROR],
                                                        forcing_couple=acouple)
            if len(node_answer) == 0:
                all_answered = False
            else:
                if node_answer[0].status == StatusConst.FORCING_FILE_UPLOADED:
                    all_errors = False

        logger.info("{}, after loop, all_answered {}, all_errors {}".format(object_and_method, all_answered,
                                                                            all_errors))
        logger.info("{}, end of".format(object_and_method))
        return [being_analysed, all_answered, all_errors]

    @staticmethod
    def node_message_on_central_help(log_instance):
        """
        On Central, the content of reaction to messages "File uploaded or FORCING_ERROR" from a node
        The method checks all answers from the nodes to the demand have arrived.
        If all nodes have answered a LoggingMessage object with "START ANALYSIS" as status is instantiated and saved.
        Saving the LoggingMessage triggers the analysis
        :param log_instance:
        :return:
        """
        object_and_method = "Helper.node_message_on_central_help"
        logger.info("{}, start of".format(object_and_method))

        all_node_responses = Helper.ready_for_analysis(log_instance)

        # If all responses have arrived and at least one of them is not an error
        if all_node_responses[0] is False and all_node_responses[1] is True and all_node_responses[2] is False:
            if ENV_DICT[NOOS_MME_ID] != ENV_DICT[NOOS_NODE_ID]:
                message_parameters = {
                    SignalsConst.SIMULATION_DEMAND: log_instance.simulation_demand.id,
                    SignalsConst.NODE: log_instance.node.id,
                    SignalsConst.NOOS_MODEL: log_instance.noos_model.id,
                    SignalsConst.STATUS: StatusConst.START_ANALYSIS,
                    SignalsConst.MESSAGE: StatusConst.START_ANALYSIS}
                mme_node = Node.objects.get(pk=ENV_DICT[NOOS_MME_ID])
                mme_node.add_logging_message(message_parameters, NOOS_USER)
            else:
                central_node = Node.objects.get(pk=ENV_DICT[NOOS_NODE_ID])
                mme_model = NoosModel.objects.get(pk=ENV_DICT[NOOS_MME_MODEL])
                new_log_message = LoggingMessage(
                    node=central_node,
                    simulation_demand=log_instance.simulation_demand,
                    noos_model=mme_model,
                    status=StatusConst.START_ANALYSIS,
                    message=StatusConst.START_ANALYSIS
                )
                new_log_message.save()

        if all_node_responses[0] is False and all_node_responses[1] is True and all_node_responses[2] is True:
            logger.info("{}, All Nodes have answered with errors".format(object_and_method))

        if all_node_responses[0] is True:
            logger.info("{}, Demand {} is already being analysed".format(object_and_method,
                                                                         log_instance.simulation_demand.id))

        logger.info("{}, end of".format(object_and_method))
        return

    @staticmethod
    def logging_messages_help(instance):
        """
        Helper static method.
        Logging procedure on the Central system.
        Reacts to messages [END_PROCESSING, ANALYSIS_OK, ANALYSIS_ERROR, START_ANALYSIS]
        """
        the_class = "Helper"
        the_method = "logging_messages_help"
        logger.info("{}.{}, start of".format(the_class, the_method))
        logger.info("{}.{}, status : {}".format(the_class, the_method, instance.status))
        special_messages = {StatusConst.NODE_ERROR: Helper.node_message_on_central_help,
                            StatusConst.FORCING_FILE_UPLOADED: Helper.node_message_on_central_help,
                            StatusConst.START_ANALYSIS: Helper.start_analysis_messages,
                            # StatusConst.START_ANALYSIS: Helper.end_of_line,
                            # StatusConst.ANALYSIS_ERROR: Helper.analysis_error_messages,
                            StatusConst.ANALYSIS_OK: Helper.analysis_ok_messages}
        if instance.status in special_messages.keys():
            special_messages[instance.status](instance)

        logger.info("{}.{}, end of".format(the_class, the_method))

    @staticmethod
    def couple_code_for_simulation_name(simulation_name):
        object_and_method = "Helper.couple_code_for_simulation_name"
        logger.info("{}, start of".format(object_and_method))
        logger.info("{}, simulation_name : {}".format(object_and_method, simulation_name))
        name_elements = simulation_name.split("_")
        if name_elements is None:
            raise ValueError
        logger.info("{}, name_elements : {}".format(object_and_method, name_elements))

        if len(name_elements) != 3:
            raise ValueError

        noos_model = NoosModel.objects.get(code=name_elements[0])
        if noos_model is None:
            raise ValueError

        model_id = noos_model.id
        current_forcing = Forcing.objects.get(code=name_elements[1])
        if current_forcing is None:
            raise ValueError
        wind_forcing = Forcing.objects.get(code=name_elements[2])
        if wind_forcing is None:
            raise ValueError
        logger.info("{}, looking for ForcingCouple using".format(object_and_method))

        the_couple = ForcingCouple.objects.get(noos_model=noos_model, oceanical=current_forcing,
                                               meteorological=wind_forcing)
        couple_id = the_couple.id
        noos_node = noos_model.nodes.first()

        logger.info("{}, mode_id : {}, couple_id {}".format(object_and_method, model_id, couple_id))
        logger.info("{}, end of".format(object_and_method))
        return [noos_node, noos_model, the_couple, "{}_{}".format(model_id, couple_id)]

    @staticmethod
    def max_time_min_time(max_time, min_time, new_time):
        if max_time is None and min_time is None:
            return [new_time, new_time]

        if new_time > max_time:
            max_time = new_time
        if new_time < min_time:
            min_time = new_time

        return [max_time, min_time]

    @staticmethod
    def slurp_one_json_mme_output(file_dir, filename, log_message):
        """
        Slurps one JSON MME file into the database. The JSON MME file is output data to display model results and
        analysis results. Called from analysis_ok_message. It will put each element (ellipse and
        multipoint cloud) of model analysis in a DB record and make one more record for the trajectory of the analysis.
        :param file_dir:
        :param filename:
        :param log_message:
        :return:
        """
        object_and_method = "Helper.slurp_one_json_mme_output"
        logger.info("{}, start of".format(object_and_method))

        json_str = None
        simulation = log_message.simulation_demand

        demand_results_dir = os.path.join(NOOS_RESULTS_DIR, str(log_message.simulation_demand.id))
        demand_parameters_dir = os.path.join(demand_results_dir, OtherConst.PARAMETERS_DIR_NAME)

        onlyfiles = [f for f in os.listdir(demand_parameters_dir) if os.path.isfile(
            os.path.join(demand_parameters_dir, f))]

        strname_re = '^noosdrift_\\d+_.*\\.json$'.format(log_message.simulation_demand.id)
        strextract_re = '^noosdrift_\\d+_(.*)\\.json$'.format(log_message.simulation_demand.id)
        jsonname_re = re.compile(strname_re)
        extract_re = re.compile(strextract_re)
        init_parameters = {}
        for name in onlyfiles:
            if jsonname_re.match(name):
                res_extract = extract_re.match(name)
                params_file = os.path.join(demand_parameters_dir, name)
                params_json = None
                with open(params_file) as json_structure:
                    params_json = json.load(json_structure)
                    json_structure.close()

                if params_json["simulation_result"]["status_code"] == 0:
                    init_parameters[res_extract[1]] = params_json

        # logger.info("{}, opening JSON file {}/{}".format(object_and_method, file_dir, filename))
        a_file = os.path.join(file_dir, filename)
        with open(a_file) as json_structure:
            json_str = json.load(json_structure)
            json_structure.close()

        # logger.info("{}, JSON data in memory".format(object_and_method))

        raw_simulations = json_str[JsonMmeElementsConst.SIMULATIONS]
        mme_coverage = json_str[JsonMmeElementsConst.COVERAGE]
        bbx_center = [mme_coverage[JsonMmeElementsConst.CENTERLAT], mme_coverage[JsonMmeElementsConst.CENTERLON]]
        bbx_coords = [
            [mme_coverage[JsonMmeElementsConst.LATMAX], mme_coverage[JsonMmeElementsConst.LONMAX]],
            [mme_coverage[JsonMmeElementsConst.LATMIN], mme_coverage[JsonMmeElementsConst.LONMIN]]
        ]

        noosdrift_simulations = {}
        for key, value in raw_simulations.items():
            simulation_data = Helper.couple_code_for_simulation_name(value)
            noosdrift_simulations[key] = {"node": simulation_data[0], "model": simulation_data[1],
                                          "forcing_couple": simulation_data[2], "couple_code": simulation_data[3],
                                          "trajectory": [], "simulation_name": value}

        # logger.debug("{}, writing features in DB".format(object_and_method))
        if JsonMmeElementsConst.FEATURES not in json_str:
            raise ValueError

        document_idx = 0
        min_time = None
        max_time = None
        sorted_ellipse_names = []
        for a_feature in json_str[JsonMmeElementsConst.FEATURES]:

            json_document_ellipses = {}
            json_document_super_ellipse = a_feature[JsonMmeElementsConst.SUPER_ELLIPSE]

            json_document_super_ellipse[JsonMmeElementsConst.SEMMAJAXIS] = json_document_super_ellipse[
                JsonMmeElementsConst.SEMMAJAXIS]

            json_document_super_ellipse[JsonMmeElementsConst.SEMMINAXIS] = json_document_super_ellipse[
                JsonMmeElementsConst.SEMMINAXIS]

            json_document_super_ellipse[JsonMmeElementsConst.ANGLE] = json_document_super_ellipse[
                JsonMmeElementsConst.ANGLE]

            json_document_clusters = []
            json_document = {JsonSimulationElementsConst.SUPER_ELLIPSE: json_document_super_ellipse,
                             JsonSimulationElementsConst.ELLIPSES: json_document_ellipses,
                             JsonSimulationElementsConst.STEP: document_idx,
                             JsonSimulationElementsConst.TIMESTAMP: a_feature[JsonMmeElementsConst.TIME],
                             JsonSimulationElementsConst.CLUSTERS: json_document_clusters}

            date_time_obj = dt.datetime.strptime(a_feature[JsonMmeElementsConst.TIME],
                                                 MemorySimulationDemand.TIMESTAMPFORMAT)
            utc_obj = pytz.utc.localize(date_time_obj)
            max_time, min_time = Helper.max_time_min_time(max_time, min_time, utc_obj)

            ellipses_dict = a_feature[JsonMmeElementsConst.ELLIPSES]

            ellipses_name_list_to_sort = []
            for ellipse_key, an_ellipse in ellipses_dict.items():
                simulation_forkey = noosdrift_simulations[ellipse_key]
                ellipses_name_list_to_sort.append(simulation_forkey[OtherConst.SIMULATION_NAME])
                new_feature = {}

                new_feature[JsonSimulationElementsConst.LAT] = an_ellipse[JsonMmeElementsConst.CENTERLAT]
                new_feature[JsonSimulationElementsConst.LNG] = an_ellipse[JsonMmeElementsConst.CENTERLON]

                new_feature[JsonSimulationElementsConst.SEMMAJAXIS] = an_ellipse[JsonMmeElementsConst.SEMMAJAXIS]

                new_feature[JsonSimulationElementsConst.SEMMINAXIS] = an_ellipse[JsonMmeElementsConst.SEMMINAXIS]

                new_feature[JsonSimulationElementsConst.ANGLE] = an_ellipse[JsonMmeElementsConst.ANGLE]

                new_feature[JsonSimulationElementsConst.COUPLE_CODE] = simulation_forkey[
                    JsonSimulationElementsConst.COUPLE_CODE]
                json_document_ellipses[simulation_forkey[OtherConst.SIMULATION_NAME]] = new_feature

                if new_feature[JsonSimulationElementsConst.LAT] is not None:
                    simulation_forkey[OtherConst.TRAJECTORY].append([new_feature[JsonSimulationElementsConst.LAT],
                                                                     new_feature[JsonSimulationElementsConst.LNG]])

            sorted_ellipse_names = sorted(ellipses_name_list_to_sort)

            for cluster_key, a_cluster in a_feature[JsonMmeElementsConst.CLUSTERS].items():
                cluster_data = {}
                mme_file_member_ellipses = a_cluster[JsonMmeElementsConst.MEMBERS]
                member_ellipses = {}
                cluster_data[JsonSimulationElementsConst.MEMBER_ELLIPSES] = member_ellipses
                mme_ellipse_distances = a_cluster[JsonMmeElementsConst.DISTANCE_FROM_CLUSTER_CENTRE]
                idx_member = 0
                for raw_ellipse_key in mme_file_member_ellipses:
                    simulation_forkey = noosdrift_simulations["{}".format(raw_ellipse_key)]
                    simulation_name = simulation_forkey[OtherConst.SIMULATION_NAME]
                    member_ellipses[simulation_name] = {
                        JsonSimulationElementsConst.DISTANCE_FROM_CLUSTER_CENTER: mme_ellipse_distances[idx_member]}
                    idx_member = idx_member + 1

                cluster_data[JsonSimulationElementsConst.LAT] = a_cluster[JsonMmeElementsConst.CENTERLAT]
                cluster_data[JsonSimulationElementsConst.LNG] = a_cluster[JsonMmeElementsConst.CENTERLON]
                cluster_data[JsonSimulationElementsConst.RADIUS] = a_cluster[JsonMmeElementsConst.LONGEST_ELLIPSIS_AXIS]
                cluster_data[JsonSimulationElementsConst.DISTANCE_STD] = a_cluster[JsonMmeElementsConst.DISTANCE_STD]
                cluster_data[JsonSimulationElementsConst.MEMBER_ELLIPSES] = member_ellipses
                json_document_clusters.append(cluster_data)

            simulation_element = SimulationElement(
                simulation=simulation,
                timestamp=utc_obj,
                idx=document_idx,
                json_data=json_document
            )

            simulation_element.save()
            document_idx = document_idx + 1

        metadata_struct = {OtherConst.BBOX_CENTER: bbx_center, OtherConst.BBOX_COORDS: bbx_coords,
                           OtherConst.TOT_STEPS: document_idx}

        trajectory_dict = {}
        for simulation_key, simulation_forkey in noosdrift_simulations.items():
            trajectory_dict[simulation_forkey[OtherConst.SIMULATION_NAME]] = {OtherConst.COORDINATES: simulation_forkey[
                OtherConst.TRAJECTORY]}

        metadata_struct[OtherConst.SIMULATION_ID] = log_message.simulation_demand.id
        metadata_struct[OtherConst.SIMULATION_NAMES] = sorted_ellipse_names
        metadata_struct[OtherConst.TRAJECTORIES] = trajectory_dict
        metadata_struct[OtherConst.START_TIME] = dt.datetime.strftime(min_time, MemorySimulationDemand.TIMESTAMPFORMAT)
        metadata_struct[OtherConst.END_TIME] = dt.datetime.strftime(max_time, MemorySimulationDemand.TIMESTAMPFORMAT)
        metadata_struct[OtherConst.INIT_PARAMETERS] = init_parameters

        metadata_element = SimulationMetadata(
            simulation=simulation,
            metadata=metadata_struct
        )
        metadata_element.save()

        the_simulation = SimulationDemand.objects.get(pk=log_message.simulation_demand.id)
        the_simulation.status = StatusConst.OK
        the_simulation.save()

        logger.info("{}, end of".format(object_and_method))
        return

    @staticmethod
    def slurp_one_geojson_node_output(file_dir, filename, log_message):
        """
        Slurps one GEOJSON file into the database. The GEOJSON file is output data to display model results.
        Called from analysis_ok_message. It will put each multipoint cloud of in a DB record.
        :param file_dir:
        :param filename:
        :param log_message:
        :return:
        """
        object_and_method = "Helper.slurp_one_geojson_node_output"
        logger.info("{}, start of".format(object_and_method))
        json_str = {}
        simulation = log_message.simulation_demand

        # logger.debug("{}, opening JSON file {}/{}".format(object_and_method, file_dir, filename))
        a_file = os.path.join(file_dir, filename)
        with open(a_file) as json_structure:
            json_str = json.load(json_structure)
            json_structure.close()

        # logger.debug("{}, JSON data in memory".format(object_and_method))
        idx = 0

        if JsonMmeElementsConst.PROPERTIES not in json_str:
            raise ValueError

        properties_dict = json_str[JsonMmeElementsConst.PROPERTIES]

        if JsonMmeElementsConst.MODELNAME not in properties_dict:
            raise ValueError
        noos_model_code = properties_dict[JsonMmeElementsConst.MODELNAME]

        if JsonMmeElementsConst.WIND_FORCING not in properties_dict:
            raise ValueError
        if JsonMmeElementsConst.OCEAN_FORCING not in properties_dict:
            raise ValueError

        the_model = NoosModel.objects.get(code=noos_model_code)
        if the_model.id != ENV_DICT[NOOS_MME_MODEL]:
            the_node = Node.objects.get(model=the_model.id, is_active=True)
        else:
            the_node = Node.objects.get(pk=ENV_DICT[NOOS_MME_ID])

        the_forcing_couple = None
        if noos_model_code != OtherConst.MME_CODE:
            wind_forcing_code = properties_dict[JsonMmeElementsConst.WIND_FORCING]
            ocean_forcing_code = properties_dict[JsonMmeElementsConst.OCEAN_FORCING]

            the_ocean_forcing = Forcing.objects.get(code=ocean_forcing_code)
            the_wind_forcing = Forcing.objects.get(code=wind_forcing_code)

            if the_ocean_forcing is None or the_wind_forcing is None or the_model is None:
                raise ValueError

            the_forcing_couple = ForcingCouple.objects.get(oceanical=the_ocean_forcing, meteorological=the_wind_forcing,
                                                           noos_model=the_model)
        else:
            the_forcing_couple = ForcingCouple.objects.get(pk=OtherConst.MME_FORCING_COUPLE_ID)

        # logger.debug("{}, writing features in DB".format(object_and_method))
        if "features" not in json_str:
            raise ValueError

        for a_feature in json_str["features"]:
            # logger.debug("{}, preparing feature {}".format(object_and_method, idx))
            date_time_obj = dt.datetime.strptime(a_feature["time"], MemorySimulationDemand.TIMESTAMPFORMAT)
            utc_obj = pytz.utc.localize(date_time_obj)
            geometry_feature = a_feature[JsonSimulationElementsConst.GEOMETRY]
            # logger.debug("{}, utc_value : {}".format(object_and_method, utc_obj))
            simulation_cloud = SimulationCloud(
                node=the_node,
                simulation=simulation,
                noos_model=the_model,
                forcing_couple=the_forcing_couple,
                timestamp=utc_obj,
                idx=idx,
                cloud_data=geometry_feature
            )
            # logger.debug("{}, saving for simulation_demand : {}, node : {}, the model : {},  idx {}".format(
            #    object_and_method, simulation.id, the_node.id, the_model.id, idx))

            simulation_cloud.save()

            # logger.debug("{}, feature {} saved".format(object_and_method, idx))
            idx = idx + 1

        logger.info("{}, end of".format(object_and_method))
        return

    @staticmethod
    def analysis_error_messages(instance):
        """
        Executed on Central. Called from logging_messages_help.
        :param instance:
        :return:
        """
        object_and_method = "Helper.analysis_error_messages"
        logger.info("{}, start of".format(object_and_method))
        logger.error("{}, the error message".format(instance))
        logger.info("{}, end of".format(object_and_method))

    @staticmethod
    def analysis_ok_messages(instance):
        """
        Executed on Central. Called from logging_messages_help. This method slurps the results of MME processing into
        the database. After that, all MME results are archived into a zip file in the MEDIA directory
        :param instance: A LoggingMessage object
        :return:
        """
        object_and_method = "Helper.analysis_ok_messages"
        logger.info("{}, start of".format(object_and_method))

        mme_output_dir = os.path.join(
            os.path.join(NOOS_RESULTS_DIR, str(instance.simulation_demand.id)), OtherConst.MME_OUTPUT)
        mme_filename = "noosdrift_" + str(instance.simulation_demand.id) + ".json"
        Helper.slurp_one_json_mme_output(file_dir=mme_output_dir, filename=mme_filename, log_message=instance)

        compiled_re = re.compile("^noosdrift_\\d+_.+\\.json$".format(instance.simulation_demand.id))
        onlyfiles = [f for f in os.listdir(mme_output_dir) if os.path.isfile(os.path.join(mme_output_dir, f))]

        for name in onlyfiles:
            if compiled_re.match(name):
                # print("root:{}, file:{}".format(root, name))
                logger.info("{}, Trying to process file {}/{}".format(object_and_method, mme_output_dir, name))
                Helper.slurp_one_geojson_node_output(file_dir=mme_output_dir, filename=name, log_message=instance)

        os.chdir(MEDIA_DIR)
        other_str_time = instance.simulation_demand.created_time.strftime("%Y%m%d-%H%M")
        strtime = dt.datetime.now().strftime("%Y%m%d-%H%M")
        demand_dir = str(instance.simulation_demand.id)
        archive_file_path = os.path.join(MEDIA_DIR, "simulation-{}-{}.zip".format(str(instance.simulation_demand.id),
                                                                                  other_str_time))
        if os.path.exists(archive_file_path):
            os.remove(archive_file_path)

        with zipfile.ZipFile(archive_file_path, "x") as my_zip:
            os.chdir(NOOS_RESULTS_DIR)
            for root, a_dir, files in os.walk(demand_dir):
                my_zip.write(root)
                for a_file in files:
                    my_zip.write(os.path.join(root, a_file))

        message_user = render_to_string('noos_services/simulation_completed.html', {
                'domain': CENTRAL_DOMAIN,
                'theid': instance.simulation_demand.pk
        })

        if not instance.simulation_demand.user.email == MAIL_ADMIN_NOOSDRIFT:
            email = EmailMessage(
                subject="Simulation Completed",
                body=message_user,
                from_email=ODIN_MAILANSWERACCOUNT,
                to=[instance.simulation_demand.user.email],
                cc=[MAIL_ADMIN_NOOSDRIFT],
                reply_to=['noreply@naturalsciences.be']
            )
        else:
            email = EmailMessage(
                subject="Simulation Completed",
                body=message_user,
                from_email=ODIN_MAILANSWERACCOUNT,
                to=[instance.simulation_demand.user.email],
                reply_to=['noreply@naturalsciences.be']
            )

        email.send(fail_silently=True)
        # send_mail("Simulation Completed", message_user, ODIN_MAILANSWERACCOUNT,
        # [instance.simulation_demand.user.email, MAIL_ADMIN_NOOSDRIFT])

        logger.info("{}, end of".format(object_and_method))
        return 0

    @staticmethod
    def start_analysis_messages(instance):
        """
        Executed on the Central NODE.
        Called from node_logging_messages_help, which has been triggered by the writing of a "START ANALYSIS" message
        in the DB.
        This method should start the MME
        :param instance: A LoggingMessage object
        :return:
        """
        object_and_method = "Helper.start_analysis_messages"
        logger.info("{}, start of".format(object_and_method))

        job = tasks.Job()
        job.execute_mme(simulation_demand=instance.simulation_demand)
        logger.info("{}, end of".format(object_and_method))
        return None

    @staticmethod
    def node_logging_messages_help(instance):
        """
        Helper static method.
        Logs messages on the NODE.
        Reacts to START_ANALYSIS message
        """
        object_and_method = "Helper.node_logging_messages_help"
        logger.info("{}, start of".format(object_and_method))
        logger.info("{}, status : {}".format(object_and_method, instance.status))
        if instance.status == StatusConst.START_ANALYSIS:
            Helper.start_analysis_messages(instance)
        logger.info("{}, end of".format(object_and_method))
