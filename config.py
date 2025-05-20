# File: config.py
import ssl

import aiomysql
import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional
from ssl import SSLContext, create_default_context

# Setup logger
logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int =  os.getenv('DB_PORT')
    DB_USER: str = os.getenv('DB_USER')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')
    DB_NAME: str = os.getenv('DB_NAME')
    # ssl_mode: str = Field("require", env="DB_SSL_MODE")
    DB_POOL_MIN: int = os.getenv('DB_POOL_MIN')
    DB_POOL_MAX: int = os.getenv('DB_POOL_MAX')
    timeout: int = 30

    class Config:
        extra = 'ignore'  # Tambahkan ini

class JWTSettings(BaseSettings):
    secret: str = os.getenv('JWT_SECRET')
    algorithm: str = os.getenv('JWT_ALGORITHM')
    expire_minutes: int = os.getenv('JWT_EXPIRE_MINUTES')
    issuer: str = "library-app"

    class Config:
        extra = 'ignore'

class AppSettings(BaseSettings):
    env: str = "production"
    DEBUG: bool = True
    log_level: str = "INFO"
    log_file: str = "app.log"
    max_log_size: int =10

    class Config:
        extra = 'ignore'

class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    app: AppSettings = AppSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        extra = 'ignore'  # Tambahkan ini

def get_ssl_context(ssl_mode: str) -> Optional[SSLContext]:
    if ssl_mode == "require":
        ctx = create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


async def get_db_pool():
    settings = Settings()

    ssl_ctx = None
    # if settings.is_production:
    #     ssl_ctx = get_ssl_context(settings.database.DB_SSL_MODE)

    pool = await aiomysql.create_pool(
        host=settings.database.DB_HOST,
        port=settings.database.DB_PORT,
        user=settings.database.DB_USER,
        password=settings.database.DB_PASSWORD,
        db=settings.database.DB_NAME,
        minsize=settings.database.DB_POOL_MIN,
        maxsize=settings.database.DB_POOL_MAX,
        autocommit=True,
        echo=False,
        ssl=None,
        init_command=(
            "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';"
            "SET time_zone='+00:00';"
        ),
        cursorclass=aiomysql.DictCursor
    )

    logger.info(
        f"Database connection pool created (size {settings.database.DB_POOL_MIN}-{settings.database.DB_POOL_MAX})")
    return pool


# Sync connection pool untuk operasi non-async (opsional)
def get_sync_db_config():
    settings = Settings()
    return {
        "host": settings.database.DB_HOST,
        "port": settings.database.DB_PORT,
        "user": settings.database.DB_USER,
        "password": settings.database.DB_PASSWORD,
        "database": settings.database.DB_NAME
        # "ssl": get_ssl_context(settings.database.DB_SSL_MODE)
    }


# Inisialisasi settings saat modul dimuat
settings = Settings()