import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    deepgram_api_key: str = ""
    gemini_api_key: str = ""
    elevenlabs_api_key: str = ""
    
    # Database
    mongodb_url: str = "mongodb://localhost:27017/doctalk"
    database_name: str = "doctalk_ai"
    
    # Server Configuration
    host: str = "localhost"
    port: int = 8000
    debug: bool = True
    
    # CORS Settings
    allowed_origins: str = "http://localhost:3000"
    
    # Voice Settings
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    deepgram_model: str = "nova-2"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings() 