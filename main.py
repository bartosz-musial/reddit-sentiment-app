from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from reddit_api.reddit_client import RedditClient
from openrouter.llama_4_scout import LlamaScout
import time
import os

class MissingEnvFileError(Exception):
    pass

if not os.path.exists(".env"):
    raise MissingEnvFileError("The .env file was not found!")

def main():
    reddit = RedditClient.from_env()
    llama = LlamaScout()
    scheduler = BackgroundScheduler()
    trigger_for_post = CronTrigger(hour="0-23", minute="0,30")
    trigger_for_sentiment = CronTrigger(hour="0-23", minute="15,45")
    scheduler.add_job(reddit.get_new_posts, trigger_for_post, args=["bitcoin", 5])
    scheduler.add_job(llama.pipeline, trigger_for_sentiment)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("\nProgram terminated by user")

if __name__ == "__main__":
    main()
