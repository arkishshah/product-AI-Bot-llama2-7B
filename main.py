import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.pydantic_models import ChatRequest, ChatResponse
from utils.chat_handler import ChatHandler
from utils.product_recommender import ProductRecommender
from config import DATA_PATH
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    recommender = ProductRecommender(DATA_PATH)
    chat_handler = ChatHandler(recommender)
except Exception as e:
    print(f"Error initializing components: {str(e)}")
    raise

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return chat_handler.handle_chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)
