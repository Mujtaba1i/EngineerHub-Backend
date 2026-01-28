import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv()

db_URI = os.getenv('DATABASE_URL')
secret = os.getenv('JWT_SECRET')



class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL', '')
    JWT_SECRET: str = os.getenv('JWT_SECRET', '')
    
    # Azure Blob Storage
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'engineerhubstorage')
    AZURE_STORAGE_ACCOUNT_KEY: str = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', '')
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'notes')
    AZURE_STORAGE_SAS_TOKEN: str = os.getenv('AZURE_STORAGE_SAS_TOKEN', '')
    
    
    model_config = ConfigDict(
        env_file=".env",
        extra='ignore'
    )

def get_settings() -> Settings:
    return Settings()