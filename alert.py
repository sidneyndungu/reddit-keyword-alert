"""Personal, read-only Reddit keyword alert.

Reads the newest posts in a few subreddits, checks titles and text against a
keyword list, and sends a private notification for each new match.

It never posts, comments, votes or sends messages through the Reddit API.
The only thing it stores is the IDs of posts it has already notified about.
"""

import argparse
import json
import os
import sys
import tomllib
import urllib.parse
import urllib.request
from pathlib import Path

import praw

USER_AGENT_TEMPLATE = "script:reddit-keyword-alert:v0.1 (by /u/{username})"
SEEN_LIMIT = 2000  # keep the seen-IDs file small


def load_config(path):
    with open(path, "rb") as f:
        config = tomllib.load(f)
    config["keywords"] = [k.lower() for k in config["keywords"]]
    return config


def reddit_client(username):
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        username=username,
        password=os.environ["REDDIT_PASSWORD"],
        user_agent=USER_AGENT_TEMPLATE.format(username=username),
        check_for_async=False,
    )


def load_seen(path):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return []


def save_seen(path, seen):
    Path(path).write_text(json.dumps(seen[-SEEN_LIMIT:]))


def matching_keywords(post, keywords):
    text = f"{post.title}\n{post.selftext}".lower()
    return [k for k in keywords if k in text]


def notify(message):
    """Send to Telegram when configured, otherwise print to the terminal."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        print(message, end="\n\n")
        return

    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    urllib.request.urlopen(url, data=data, timeout=15)


def run(config):
    reddit = reddit_client(config["reddit_username"])
    seen = load_seen(config["seen_file"])
    seen_set = set(seen)

    for name in config["subreddits"]:
        for post in reddit.subreddit(name).new(limit=config["posts_per_subreddit"]):
            if post.id in seen_set:
                continue
            seen.append(post.id)
            seen_set.add(post.id)

            hits = matching_keywords(post, config["keywords"])
            if hits:
                notify(
                    f"r/{name}: {post.title}\n"
                    f"Matched: {', '.join(hits)}\n"
                    f"https://www.reddit.com{post.permalink}"
                )

    save_seen(config["seen_file"], seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default="config.toml")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        sys.exit(f"No {args.config} found. Copy config.example.toml to config.toml first.")

    run(config)


if __name__ == "__main__":
    main()
