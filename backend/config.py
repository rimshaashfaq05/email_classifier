# """Configuration module for email classifier."""

# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# class Config:
#     """Application configuration."""
    
#     # OpenAI Configuration
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
#     TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
#     MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
#     # Application Settings
#     LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
#     BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    
#     # Email Categories
#     EMAIL_CATEGORIES = [
#         "invoice/bill",
#         "shipping/order", 
#         "calendar_invite",
#         "newsletter",
#         "other"
#     ]
    
#     # File paths
#     DATA_DIR = "data"
#     DELIVERABLES_DIR = "deliverables"
#     TEMP_DIR = "data/temp"
    
#     @classmethod
#     def validate(cls):
#         """Validate required configuration."""
#         if not cls.OPENAI_API_KEY:
#             raise ValueError("OPENAI_API_KEY is required")
        
#         # Create directories if they don't exist
#         for dir_path in [cls.DATA_DIR, cls.DELIVERABLES_DIR, cls.TEMP_DIR]:
#             os.makedirs(dir_path, exist_ok=True)

"""Configuration module for email classifier."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Model Configuration
    MODEL_TYPE = os.getenv("MODEL_TYPE", "huggingface")  
    HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")
    
    # Compatibility placeholders
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "free_model")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not_needed")
    
    # Processing settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    
    # Application Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # 📌 Updated Email Categories
    EMAIL_CATEGORIES = [
        "banking",        # JazzCash, iBanking, payment alerts
        "ecommerce",      # Daraz, Amazon, shopping orders/shipping
        "education",      # University emails, admission, registration
        "job_alert",      # Indeed, Rozee, LinkedIn
        "notifications",  # Google alerts, security warnings
        "newsletter",     # Promotions, updates
        # old ones (for compatibility)
        "invoice/bill",
        "shipping/order",
        "calendar_invite"
        "other"           # Fallback
    ]
    
    # File paths
    DATA_DIR = "data"
    DELIVERABLES_DIR = "deliverables"
    TEMP_DIR = "data/temp"
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        print(f"Using {cls.MODEL_TYPE} models locally")
        print(f"HuggingFace model: {cls.HF_MODEL_NAME}")
        
        for dir_path in [cls.DATA_DIR, cls.DELIVERABLES_DIR, cls.TEMP_DIR]:
            os.makedirs(dir_path, exist_ok=True)
