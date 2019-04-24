import logging
import os
import tarfile

from noosDrift.settings import REQUESTS_DIR
from noos_services import tasks

logger = logging.getLogger(__name__)


class Helper:

    @staticmethod
    def node_simulation_demand_help(instance):
        """
        Helper static method, processes Simulation Demand on Node.
        :param instance: A SimultationDemand instance
        :return:
        """
    
        object_name = "Helper"
        object_and_method = "Helper.node_simulation_demand_help"
    
        logger.info("{}: request_is_created on node, all is done".format(object_name))
        logger.info("{}: Propagation {} received, start tasks".format(object_and_method, instance.id))
        logger.info("{}: creating directory tree".format(object_and_method))
    
        if not os.path.isdir(REQUESTS_DIR):
            try:
                os.mkdir(REQUESTS_DIR)
            except OSError as exc:
                logger.error("{}, not able to create directory : {}, error {}".format(object_name, REQUESTS_DIR,
                                                                                      exc.strerror))
                raise
    
        this_demand_dir = os.path.join(REQUESTS_DIR, str(instance.id))
        try:
            os.mkdir(this_demand_dir)
        except FileExistsError as exc:
            logger.error("{}, OK {} already exists".format(object_name, this_demand_dir))
        except OSError as exc:
            logger.error("{}, not able to create directory : {}, error : {}".format(object_name, this_demand_dir,
                                                                                    exc.strerror))
            raise
    
        job = tasks.Job()
        job.job(simulation_demand=instance)

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

    @staticmethod
    def central_uploadedfile_help(instance):
        """
        Helper static method. Used  in Signals after new record has been inserted in the UploadedFile table
        :param instance: a UploadedFile instance
        :return:
        """
        the_class = "Helper"
        the_method = "central_uploadedfile_help"
    
        if not os.path.isdir(REQUESTS_DIR):
            err_mess = "{}, {}, path {}, does not exists".format(the_class, the_method, REQUESTS_DIR)
            logger.error(err_mess)
            raise FileNotFoundError(err_mess)
    
        # simulation_demand_archive = "sim:{}-mod:{}-for:{}.tgz".format(simulation_demand_id, kwargs["noos_model_code"],
        #                                                              kwargs["couple_code"])
    
        archive_name = instance.filename
        split_one = archive_name.split('-')
        archive_name_dict = {}
        for fsel in split_one:
            split_two = fsel.split(':')
            archive_name_dict[split_two[0]] = split_two[1]
    
        sim_file_path = os.path.join(REQUESTS_DIR, archive_name)
        # sim_file_path = os.path.join("/home/noosdrift_scp/results", archive_name)
        res_path1 = os.path.join(REQUESTS_DIR, archive_name_dict['sim'])
        res_path2 = os.path.join(res_path1, archive_name_dict['mod'])
    
        if not os.path.isfile(sim_file_path):
            err_mess = "{}, {}, path {}, does not exists".format(the_class, the_method, sim_file_path)
            logger.error(err_mess)
            raise FileNotFoundError(err_mess)
    
        if not os.path.isdir(res_path1):
            os.mkdir(res_path1)
    
        if not os.path.isdir(res_path2):
            os.mkdir(res_path2)
    
        save_dir = os.getcwd()
        os.chdir(res_path2)
        archive_file = tarfile.open(sim_file_path, mode="r:gz")
        archive_file.extractall()
        archive_file.close()
        os.chdir(save_dir)
    
        return None

    @staticmethod
    def logging_messages_help(instance):
        """
        Helper static method. Just logs messages on the central
        """
        the_class = "Helper"
        the_method = "logging_messages_help"
        logger.info("{}.{}, start of".format(the_class, the_method))
        logger.info("{}.{}, status : {}".format(the_class, the_method, instance.status))
        logger.info("{}.{}, end of".format(the_class, the_method))

    @staticmethod
    def node_logging_messages_help(instance):
        """
        Helper static method. Just logs messages on the node
        """
        object_and_method = "Helper.node_logging_messages_help"
        logger.info("{}, start of".format(object_and_method))
        logger.info("{}, status : {}".format(object_and_method, instance.status))
        logger.info("{}, end of".format(object_and_method))
