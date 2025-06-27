from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.reddit_api.reddit_client import RedditClient
from backend.openrouter.models import LlamaScout, MistralNemo
from backend.logging_config import get_config
from dotenv import load_dotenv
import time
import os
import yaml
import logging

class MissingEnvFileError(Exception):
    pass

class MissingConfigFileError(Exception):
    pass

if not os.path.exists("config/.env"):
    raise MissingEnvFileError("The .env file was not found!")

if not os.path.exists("config/config.yaml"):
    raise MissingConfigFileError("The config.yaml file was not found!")

load_dotenv()
get_config()

def get_available_sentiment_model() -> LlamaScout | MistralNemo | None:
    llama = LlamaScout()
    mistral = MistralNemo()

    if llama.test_sentiment_model():
        logging.info("Using meta-llama/llama-4-scout:free")
        return llama
    elif mistral.test_sentiment_model():
        logging.info("Using mistralai/mistral-nemo:free")
        return mistral
    else:
        logging.error("No available sentiment model found!")
        return None

def pipeline():
    main_model = get_available_sentiment_model()
    if main_model is None:
        return
    main_model.pipeline()

def main():
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)

    subreddits = cfg["subreddits"]
    post_limit = cfg["post_limit"]

    cron_post = CronTrigger(**cfg["cron_post"])
    cron_sentiment = CronTrigger(**cfg["cron_sentiment"])

    reddit = RedditClient.from_env()

    scheduler = BackgroundScheduler()
    for subreddit in subreddits:
        scheduler.add_job(reddit.get_new_posts, cron_post, args=[subreddit, post_limit])
        logging.info(f"Scheduled job 'get_new_posts' for subreddit r/{subreddit}")

    scheduler.add_job(pipeline, cron_sentiment)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("\nProgram terminated by user")

if __name__ == "__main__":
    main()
