import datetime
import logging

from apscheduler.events import JobExecutionEvent, JobSubmissionEvent
from pytz import utc

from django_apscheduler.jobstores import register_events
from django_apscheduler.models import DjangoJobExecution
from tests.conftest import job

logging.basicConfig()


def test_delete_old_job_executions(db, scheduler):
    register_events(scheduler)
    scheduler.add_job(job, trigger="interval", seconds=1, id="job_1")
    scheduler.add_job(job, trigger="interval", seconds=1, id="job_2")

    scheduler.start()

    now = datetime.datetime.now(utc)
    one_second_ago = now - datetime.timedelta(seconds=1)  # Simulate

    scheduler._dispatch_event(JobExecutionEvent(4096, "job_1", None, one_second_ago))
    scheduler._dispatch_event(JobExecutionEvent(4096, "job_2", None, now))

    scheduler._dispatch_event(JobSubmissionEvent(32768, "job_1", None, [one_second_ago]))
    scheduler._dispatch_event(JobSubmissionEvent(32768, "job_2", None, [now]))

    assert DjangoJobExecution.objects.count() == 2

    DjangoJobExecution.objects.delete_old_job_executions(1)

    assert DjangoJobExecution.objects.count() == 1
