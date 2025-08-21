"""Application configuration management"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Google GenAI (API Key) Configuration
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    location: str = Field(default="us-central1", env="LOCATION")
    gemini_model: str = Field(default="gemini-2.0-flash-exp", env="GEMINI_MODEL")
    embedding_model: str = Field(default="models/text-embedding-004", env="EMBEDDING_MODEL")
    
    # Application Configuration
    app_name: str = Field(default="Mini Asistente Q&A", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # File Upload Configuration
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions_str: str = Field(default="pdf,txt", env="ALLOWED_EXTENSIONS")
    max_files: int = Field(default=10, env="MAX_FILES")
    
    # Vector Store Configuration
    vector_store_path: str = Field(default="./data/vectors", env="VECTOR_STORE_PATH")
    documents_path: str = Field(default="./data/documents", env="DOCUMENTS_PATH")
    
    # Server Configuration
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    backend_url: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    
    # Text Processing Configuration
    chunk_size: int = Field(default=4000, env="CHUNK_SIZE")  # ~1024 tokens as recommended by Pinecone
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Search Configuration
    search_limit: int = Field(default=5, env="SEARCH_LIMIT")
    similarity_threshold: float = Field(default=0.4, env="SIMILARITY_THRESHOLD")  # Balanced between precision and recall
    
    # LLM Configuration
    max_tokens: int = Field(default=2048, env="MAX_TOKENS")
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def allowed_extensions(self) -> List[str]:
        """Convert allowed_extensions_str to list"""
        return [ext.strip() for ext in self.allowed_extensions_str.split(",")]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()
