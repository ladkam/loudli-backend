from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from rssUpdater import rssRefresher
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(rssRefresher.update_rss, 'interval', seconds=1)
    scheduler.start()