import os

from dotenv import load_dotenv

load_dotenv()


def read_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")


DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ITS_MOE_DISCORD_ID = os.environ["ITS_MOE_DISCORD_ID"]

DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ["DB_NAME"]
DB_DSN = f"mysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

CF_API_KEY = os.environ["CF_API_KEY"]
CF_ZONE_ID = os.environ["CF_ZONE_ID"]

DEBUG_MODE = read_bool(os.environ["DEBUG_MODE"])

VERSION = "1.0.0"
