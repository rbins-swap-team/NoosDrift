import datetime as dt
import logging
import os
import re
import shutil

from noos_services.models import SimulationDemand
from noosDrift.settings import MEDIA_DIR, NOOS_RESULTS_DIR

logger = logging.getLogger(__name__)


class ArchiveHelper:

    @staticmethod
    def archive_simulations():
        """
        Executed on Central.
        - Sets the "archived" property to TRUE for all simulation demands older than 15 days and where property
        "protected" is FALSE
        - Deletes the demand results for these demands in NOOS_RESULTS_DIR
        - Deletes the archived zip files for these demands in MEDIA_DIR
        :return:
        """

        name_and_method = "archivehelper.archive_simulations"
        logger.info("{}, start".format(name_and_method))
        fifteen_days = dt.timedelta(days=15)
        when_am_i = dt.datetime.utcnow()
        fifteen_days_ago = when_am_i - fifteen_days

        active_demands = SimulationDemand.active_objects.filter(created_time__lt=fifteen_days_ago, protected=False)
        for a_demand in active_demands:
            a_demand.archived = True
            a_demand.save()
            # logger.info("{}, database updated".format(name_and_method))
            to_delete = os.path.join(NOOS_RESULTS_DIR, str(a_demand.id))
            # logger.info("{}, Directory to delete : {}".format(name_and_method, to_delete))
            if os.path.exists(to_delete) and os.path.isdir(to_delete):
                shutil.rmtree(to_delete)
            else:
                logger.info("{}, Directory : {}, does not exist or is no dir".format(name_and_method, to_delete))

            # This part deletes the archive files prepared by helper.analysis_ok_messages
            arch_file_search_re = re.compile("^simulation-{}-.*zip$".format(a_demand.id))
            # logger.info("{}, Looking for files to delete".format(name_and_method))
            for root, a_dir, files in os.walk(MEDIA_DIR):
                for a_file_name in files:
                    if arch_file_search_re.match(a_file_name):
                        to_delete = os.path.join(root, a_file_name)
                        # logger.info("{}, file to delete, {}".format(name_and_method, a_file_name))
                        os.remove(to_delete)

        logger.info("{}, end".format(name_and_method))
