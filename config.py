import os

# Default LLM configuration
LLM_MODEL = "qwen2.5:3b"
LLM_TEMPERATURE = 0.0

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DATABASE_DIR, "memory.db")

# Ensure required directories exist
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
