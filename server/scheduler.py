from apscheduler.schedulers.background import BackgroundScheduler
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
from .testsuite import run_tests
from .storage import list_test_schedules

sched = BackgroundScheduler()

def refresh_jobs():
    sched.remove_all_jobs()
    for r in list_test_schedules():
        if not r.enabled:
            continue
        hh, mm = map(int, r.time_hhmm.split(':'))
        sched.add_job(run_tests, 'cron', hour=hh, minute=mm, timezone=ZoneInfo(r.tz), id=f"test@{r.time_hhmm}")

def start_scheduler():
    if not sched.running:
        sched.start()
    refresh_jobs()
