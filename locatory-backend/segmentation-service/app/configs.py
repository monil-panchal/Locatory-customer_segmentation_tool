from typing import Optional
from pydantic import BaseSettings, Field, BaseModel
from dotenv import load_dotenv

load_dotenv()

# class APIConfig(BaseModel):
#     """Application configurations."""


class GlobalConfig(BaseSettings):
    app_name: str = "Segmentation API"

    # define global variables with the Field class
    API_ENV: str = Field(env="API_ENV")

    USERNAME: str = None
    PASSWORD: str = None
    SECRET_KEY: str = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = None
    LOG_PATH: str = None
    MONGODB_URL: str = None
    MONGODB_PORT: int = None
    MONGODB_DATABASE_NAME: str = None
    MONGODB_USERNAME: str = None
    MONGODB_PASSWORD: str = None

    class Config:
        env_file: str = ".env"


class DevConfig(GlobalConfig):
    """Development configurations."""

    # Additional Dev related variables

    class Config:
        env_prefix: str = "DEV_"


class ProdConfig(GlobalConfig):
    """Production configurations."""

    # Additional Prod related variables

    class Config:
        env_prefix: str = "PROD_"


class FactoryConfig:
    """Returns a config instance dependending on the ENV_STATE variable."""

    def __init__(self, api_env: str):
        self.api_env = api_env

    def __call__(self):
        if self.api_env == "dev":
            return DevConfig()

        elif self.api_env == "prod":
            return ProdConfig()


cfg = FactoryConfig(GlobalConfig().API_ENV)()
