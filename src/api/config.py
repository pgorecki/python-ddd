from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
# SECRET_KEY = config("SECRET_KEY", cast=Secret, default="secret")
# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="*")
