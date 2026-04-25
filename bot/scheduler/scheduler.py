from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()

scheduler.configure(job_defaults={
        'coalesce': False,
        'max_instances': 1,
        'misfire_grace_time': 60
    })