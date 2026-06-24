# config/settings.py
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from pathlib import Path
import os

class Settings(BaseSettings):
    # LM Studio Configuration
    LMSTUDIO_BASE_URL: str = "http://192.168.153.1:1234"
    MODEL_ID: str = "deepseek-r1-distill-qwen-7b"

    # Vector Database
    VECTOR_DB_TYPE: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"

    # Pinecone Configuration (optional)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: Optional[str] = "fpna-agent"

    # File Paths
    BASE_DIR: str = "./"
    DATA_DIR: str = "./data"
    UPLOAD_DIR: str = "./data/uploads"
    REPORTS_DIR: str = "./data/reports"
    SAMPLE_DATA_FILE: str = "./data/sample_financial_data.json"

    # Financial Thresholds
    VARIANCE_THRESHOLD: float = 0.10
    SIGNIFICANT_AMOUNT: float = 10000.0
    MIN_VARIANCE_FOR_INVESTIGATION: float = 0.05  # 5% minimum
    
    # Agent Settings (from .env)
    MAX_RETRIEVAL_DOCS: int = 5
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 4096
    REQUEST_TIMEOUT: int = 120
    MAX_RETRIES: int = 2
    
    # Workflow Settings
    ENABLE_PARALLEL_PROCESSING: bool = True
    MAX_CONCURRENT_INVESTIGATIONS: int = 3
    SAVE_REPORTS: bool = True
    GENERATE_BUDGET_PROPOSALS: bool = True
    
    # Display Settings
    MAX_DISPLAY_VARIANCES: int = 5
    MAX_DISPLAY_RECOMMENDATIONS: int = 5
    MAX_DISPLAY_PROPOSALS: int = 5
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./data/fpa_system.log"
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_CONSOLE_LOGGING: bool = True
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "text-embedding-nomic-embed-text-v1.5"
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Budget Proposal Settings
    BUDGET_ADJUSTMENT_OVERSEND_FACTOR: float = 0.8  # 80% of overspend
    BUDGET_ADJUSTMENT_UNDERSPEND_FACTOR: float = 0.6  # 60% of underspend
    MIN_PROPOSAL_AMOUNT: float = 1000.0
    
    # System Settings
    DEBUG_MODE: bool = False
    ENABLE_CACHE: bool = True
    CACHE_DIR: str = "./data/cache"
    
    # ✅ Pydantic v2 configuration
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Changed from "allow" to "ignore" for cleaner validation
        validate_default=True
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            Path(self.DATA_DIR),
            Path(self.UPLOAD_DIR),
            Path(self.REPORTS_DIR),
            Path(self.CHROMA_PERSIST_DIR).parent if self.CHROMA_PERSIST_DIR else None,
            Path(self.CACHE_DIR) if hasattr(self, 'CACHE_DIR') else None,
        ]
        
        for dir_path in directories:
            if dir_path and not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"📁 Created directory: {dir_path}")
                except Exception as e:
                    print(f"⚠️  Could not create directory {dir_path}: {e}")
    
    @property
    def data_dir_path(self) -> Path:
        """Get DATA_DIR as Path object"""
        return Path(self.DATA_DIR)
    
    @property
    def upload_dir_path(self) -> Path:
        """Get UPLOAD_DIR as Path object"""
        return Path(self.UPLOAD_DIR)
    
    @property
    def reports_dir_path(self) -> Path:
        """Get REPORTS_DIR as Path object"""
        return Path(self.REPORTS_DIR)
    
    @property
    def chroma_persist_dir_path(self) -> Path:
        """Get CHROMA_PERSIST_DIR as Path object"""
        return Path(self.CHROMA_PERSIST_DIR)
    
    @property
    def sample_data_file_path(self) -> Path:
        """Get SAMPLE_DATA_FILE as Path object"""
        return Path(self.SAMPLE_DATA_FILE)
    
    @property
    def cache_dir_path(self) -> Path:
        """Get CACHE_DIR as Path object"""
        return Path(self.CACHE_DIR)
    
    @property
    def log_file_path(self) -> Path:
        """Get LOG_FILE as Path object"""
        return Path(self.LOG_FILE)
    
    def validate_settings(self) -> dict:
        """Validate all settings and return status"""
        validation_results = {
            "directories": [],
            "connections": [],
            "settings": []
        }
        
        # Check directories
        dirs_to_check = [
            ("DATA_DIR", self.DATA_DIR),
            ("UPLOAD_DIR", self.UPLOAD_DIR),
            ("REPORTS_DIR", self.REPORTS_DIR),
            ("CHROMA_PERSIST_DIR", self.CHROMA_PERSIST_DIR),
        ]
        
        for name, path in dirs_to_check:
            dir_path = Path(path)
            if dir_path.exists():
                validation_results["directories"].append(f"✓ {name}: {path} (exists)")
            else:
                validation_results["directories"].append(f"⚠️ {name}: {path} (will be created)")
        
        # Check settings values
        if self.MAX_TOKENS > 2048:
            validation_results["settings"].append(f"⚠️ MAX_TOKENS: {self.MAX_TOKENS} (high, may cause slow responses)")
        else:
            validation_results["settings"].append(f"✓ MAX_TOKENS: {self.MAX_TOKENS}")
            
        if self.REQUEST_TIMEOUT > 180:
            validation_results["settings"].append(f"⚠️ REQUEST_TIMEOUT: {self.REQUEST_TIMEOUT}s (long timeout)")
        else:
            validation_results["settings"].append(f"✓ REQUEST_TIMEOUT: {self.REQUEST_TIMEOUT}s")
            
        if self.VARIANCE_THRESHOLD > 0.2:
            validation_results["settings"].append(f"⚠️ VARIANCE_THRESHOLD: {self.VARIANCE_THRESHOLD*100}% (high threshold)")
        else:
            validation_results["settings"].append(f"✓ VARIANCE_THRESHOLD: {self.VARIANCE_THRESHOLD*100}%")
        
        # Check LM Studio URL format
        if not self.LMSTUDIO_BASE_URL.startswith(('http://', 'https://')):
            validation_results["connections"].append(f"❌ LM_STUDIO_URL: Invalid format")
        else:
            validation_results["connections"].append(f"✓ LM_STUDIO_URL: {self.LMSTUDIO_BASE_URL}")
        
        return validation_results
    
    def get_agent_config(self) -> dict:
        """Get configuration for agents"""
        return {
            "temperature": self.TEMPERATURE,
            "max_tokens": self.MAX_TOKENS,
            "timeout": self.REQUEST_TIMEOUT,
            "max_retries": self.MAX_RETRIES,
        }
    
    def get_rag_config(self) -> dict:
        """Get configuration for RAG system"""
        return {
            "chunk_size": self.CHUNK_SIZE,
            "chunk_overlap": self.CHUNK_OVERLAP,
            "embedding_model": self.EMBEDDING_MODEL,
            "similarity_threshold": self.SIMILARITY_THRESHOLD,
            "max_retrieval_docs": self.MAX_RETRIEVAL_DOCS,
        }
    
    def get_budget_config(self) -> dict:
        """Get configuration for budget proposals"""
        return {
            "overspend_factor": self.BUDGET_ADJUSTMENT_OVERSEND_FACTOR,
            "underspend_factor": self.BUDGET_ADJUSTMENT_UNDERSPEND_FACTOR,
            "min_proposal_amount": self.MIN_PROPOSAL_AMOUNT,
            "significant_amount": self.SIGNIFICANT_AMOUNT,
        }

# Global settings instance
settings = Settings()

