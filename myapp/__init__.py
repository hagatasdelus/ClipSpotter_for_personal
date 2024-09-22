import os

from dotenv import load_dotenv

load_dotenv(override=True)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]
ACCESS_TOKEN = os.environ["DISCORD_ACCESS_TOKEN"]
