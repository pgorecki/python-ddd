from typing import cast
import os
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret


env_filename = os.getenv("ENV_FILENAME", ".env")

config = Config(env_filename)

DEBUG = config("DEBUG", cast=bool, default=False)
APP_NAME = "Online Auctions API"
DATABASE_URL = config(
    "DATABASE_URL", default="postgresql://postgres:password@localhost:5432/postgres"
)

# SECRET_KEY = config("SECRET_KEY", cast=Secret, default="secret")
# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="*")
