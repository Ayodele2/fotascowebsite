from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL:str|None
    API_KEY:str
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    
    
settings = Settings()