# reddit-keyword-alert

A personal, **non-commercial**, **read-only** script that tells me when a post
in a few subreddits I already read mentions something I care about.

## What it does

Every hour it:

1. Reads the newest posts (title and text) in a short list of subreddits.
2. Checks them against a short list of keywords I choose.
3. Sends me a private notification (Telegram, or my terminal) with the post
   title and link for each new match.

I then open the post on Reddit myself if I want to read or reply.

## What it does not do

- It **does not post, comment, vote or send messages** through the API.
- It **does not store post content or usernames**. The only thing saved is
  the IDs of posts it has already notified me about, so I don't get
  duplicates (capped at 2,000 IDs).
- It **does not share, sell or publish** any Reddit data, and the data is
  **not used to train AI** models.
- It is **not used for any business**. It has no ads, no paid features and
  no users other than me.

## API usage

- Runs as a Reddit **script app** under my own account.
- One listing request per subreddit per run: with 3 subreddits and hourly
  runs, that is about **72 requests a day**, far below the 100 requests per
  minute limit.
- Sends a descriptive user agent:
  `script:reddit-keyword-alert:v0.1 (by /u/<username>)`.

## Why not Devvit

Devvit apps run inside Reddit and are installed on a subreddit by its
moderators. This tool isn't a subreddit app, I am not a moderator of the
subreddits it reads, and it has to notify me outside Reddit from a script on
my own computer. That needs read access to the Data API from a personal
script app.

## Setup

Requires Python 3.11+.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config.example.toml config.toml   # then edit subreddits and keywords
```

Set credentials as environment variables (never commit them):

```bash
export REDDIT_CLIENT_ID=...
export REDDIT_CLIENT_SECRET=...
export REDDIT_PASSWORD=...
# Optional, for Telegram notifications instead of terminal output:
export TELEGRAM_BOT_TOKEN=...
export TELEGRAM_CHAT_ID=...
```

Run once:

```bash
.venv/bin/python alert.py
```

Run hourly with cron:

```
0 * * * * cd /path/to/reddit-keyword-alert && .venv/bin/python alert.py
```

## Status

Waiting for Reddit Data API approval under the
[Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy).
The script is not run against the API until access is approved.

## License

MIT
