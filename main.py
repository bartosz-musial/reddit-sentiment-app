from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from reddit_api.reddit_client import RedditClient
import time

def main():
    reddit = RedditClient.from_env()
    scheduler = BackgroundScheduler()
    trigger_for_post = CronTrigger(hour="0-23", minute="0,30")
    scheduler.add_job(reddit.get_new_posts, trigger_for_post, args=["bitcoin", 5])
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("\nProgram terminated by user")

if __name__ == "__main__":
    main()
