import os
import tweepy
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv

# Load le fichier env
load_dotenv()

# Tu touche pas sauf a la channel id 
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = 1334531649156681738  # Met l'id du channel dc
TWITTER_USERS = ["PRXPVNE", "sim011111"]  # Nos deux bg/blg
cached_tweets = {}

# Lance Le Bot Discord
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Lance Le Bot Twitter
twitter_client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

def get_latest_tweets(username: str, count: int = 5):
    """OULALAAL JE FETCH LES TWEETS"""
    try:
        # Get l'user id
        user = twitter_client.get_user(username=username, user_fields=["id"])
        if user.data is None:
            print(f"User {username} c qui ce trdballe.")
            return []

        user_id = user.data.id

        # Prend les tweets
        tweets = twitter_client.get_users_tweets(id=user_id, max_results=count, tweet_fields=["id"])
        return [f"https://twitter.com/{username}/status/{tweet.id}" for tweet in tweets.data] if tweets.data else []
    except tweepy.errors.TweepyException as e:
        print(f"Force a wat ya une erreur je sais pas c quoi {username}: {e}")
        return []

def get_new_tweets(username):
    """OULALA JE PREND LES NOUVEAUX TWEETS"""
    global cached_tweets
    latest_tweets = get_latest_tweets(username)

    # clc le cache
    new_tweets = [tweet for tweet in latest_tweets if tweet not in cached_tweets.get(username, [])]
    cached_tweets[username] = latest_tweets

    return new_tweets

@bot.event
async def on_ready():
    """Salut"""
    print(f"je suis co en tant que {bot.user}")

    # fetch le channel discord
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        print(f"mais kestume chie le channel {DISCORD_CHANNEL_ID} il existe pas.")
        return

    for user in TWITTER_USERS:
        cached_tweets[user] = get_latest_tweets(user)
        await asyncio.sleep(5)  # fuck le rate limt

    # Prend les nouveaux tweets
    while True:
        for user in TWITTER_USERS:
            new_tweets = get_new_tweets(user)

            # Send new tweets to Discord
            if new_tweets:
                await channel.send(f"Guettez ca les kho {user}:")
                for link in new_tweets:
                    await channel.send(link)

        # Peite pause
        await asyncio.sleep(300)  # Check toutes les 5 mins
