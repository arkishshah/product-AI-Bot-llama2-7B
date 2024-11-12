import os
from dotenv import load_dotenv
import torch  # Added this import

load_dotenv()

MODEL_CONFIG = {
    "model_path": os.getenv("MODEL_PATH", "./llm_models/llama-2-7b-chat.ggmlv3.q4_0.bin"),
    "max_length": 512,
    "temperature": 0.7,
    "top_p": 0.9,
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}

DATA_PATH = os.getenv("DATA_PATH", "./data/sephora_products.csv")

# Add some useful constants
SUPPORTED_SKIN_TYPES = ['dry', 'oily', 'combination', 'sensitive', 'normal']
MAX_RESPONSE_LENGTH = 1024
DEFAULT_TOP_K = 3

# Model paths and configurations
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'

# API configurations
API_HOST = "127.0.0.1"
API_PORT = 3000