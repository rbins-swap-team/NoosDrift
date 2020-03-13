from django.apps import AppConfig

import time
from datetime import datetime as dt, timezone, timedelta


class NoosServicesConfig(AppConfig):
    name = 'noos_services'

    def ready(self):
        # Don't remove imports
        import noos_services.signals
        from background_task.tasks import Task
        from noos_services.tasks import archive_old_demands
        from background_task.models import Task as ModelTask

        res_time = time.strptime(time.strftime("%Y-%m-%d 01:00:00"), "%Y-%m-%d %H:%M:%S")
        one_day = timedelta(days=1)
        res_time_stamp = dt.fromtimestamp(time.mktime(res_time), timezone.utc)
        next_time_stamp = res_time_stamp + one_day
        existing_tasks = ModelTask.objects.filter(task_name="noos_services.tasks.archive_old_demands",
                                                  run_at=next_time_stamp, attempts=0)
        if len(existing_tasks) == 0:
            archive_old_demands(schedule=next_time_stamp, repeat=Task.DAILY)
