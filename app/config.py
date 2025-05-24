import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from pathlib import Path
import os
from pydantic_settings import BaseSettings,SettingsConfigDict

load_dotenv()



def set_logging():
    logger = logging.getLogger('randomuser')
    logger.setLevel(logging.DEBUG)

    # Создаем папку для логов, если её нет
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Настройка формата
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Логгер для FastAPI
    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.DEBUG)
    
    # Консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG) 
    logger.addHandler(console_handler)
    
    # Файловый вывод (с ротацией)
    file_handler = RotatingFileHandler(
        filename="logs/app.log",
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

   
    
    return logger
class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file= 'randomuser.env',
        env_file_encoding= 'utf-8'
    )




settings = Settings()
logger = set_logging()

def get_db_url():
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")