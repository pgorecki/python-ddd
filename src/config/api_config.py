from pydantic import Field
from pydantic_settings import BaseSettings

# env_filename = os.getenv("ENV_FILENAME", ".env")


class ApiConfig(BaseSettings):
    """
    All API Settings are here
    """

    APP_NAME: str = "Online Auctions API"
    DEBUG: bool = Field(default=True)
    DATABASE_ECHO: bool = Field(default=True)
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/postgres",
    )
    LOGGER_NAME: str = "api"


# SECRET_KEY = config("SECRET_KEY", cast=Secret, default="secret")
# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="*")
