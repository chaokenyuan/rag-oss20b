import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str = "bolt://10.211.55.5:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    
    # GPT-OSS-20B Configuration
    model_name: str = "gpt-oss-20b"
    model_path: Optional[str] = None  # Path to local model if available
    api_key: Optional[str] = None     # API key if using hosted service
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # Agent Configuration
    max_context_length: int = 4096
    code_analysis_depth: int = 3
    
    # Java Development Configuration
    java_home: Optional[str] = None
    maven_home: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()