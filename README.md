# Sephora Product Recommendation Chatbot

## Overview
This project implements an AI-powered chatbot that provides personalized beauty product recommendations using the Sephora product dataset. The system combines natural language processing with advanced filtering and ingredient analysis to deliver accurate, context-aware product suggestions.

## Features
- 🤖 Natural language query processing
- 🔍 Smart product filtering based on:
  - Skin type
  - Price range
  - Ingredients preferences
  - Product concerns
- 🧪 Ingredient analysis including:
  - Potentially harmful ingredients detection
  - Common allergens identification
  - Key benefits analysis
- 📊 Product comparison capabilities
- 💬 Conversational interface
- 🔄 Real-time recommendations
- 🎯 Semantic search using advanced embeddings

## Technical Requirements
- Python 3.9.x (3.9.7 recommended)
- pip 21.3.x or higher
- 6GB+ free disk space for model storage
- 8GB+ RAM recommended
- CUDA-compatible GPU (optional, for faster processing)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/arkishshah/product-AI-Bot-llama2-7B.git
cd product-AI-Bot-llama2-7B
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Unix/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download the LLM model**
```bash
# Create models directory
mkdir llm_models
cd llm_models

# Download the quantized model (about 4GB)
# Windows PowerShell:
Invoke-WebRequest -Uri "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_0.bin" -OutFile "llama-2-7b-chat.ggmlv3.q4_0.bin"

# Unix/MacOS:
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_0.bin
```

5. **Setup environment variables**
Create a `.env` file in the root directory:
```env
MODEL_PATH=./llm_models/llama-2-7b-chat.ggmlv3.q4_0.bin
DATA_PATH=./data/sephora_products.csv
```

6. **Prepare your data**
Place your Sephora product dataset in `data/sephora_products.csv`

## Project Structure
```
product-AI-Bot-llama2-7B/
├── .env                # Environment variables
├── config.py          # Configuration settings
├── main.py            # FastAPI application
├── requirements.txt   # Project dependencies
├── models/           # Data models
│   ├── __init__.py
│   └── pydantic_models.py
├── utils/            # Utility functions
│   ├── __init__.py
│   ├── chat_handler.py
│   ├── ingredient_analyzer.py
│   ├── product_comparer.py
│   └── product_recommender.py
├── data/             # Data directory
│   └── sephora_products.csv
└── llm_models/       # LLM model directory
    └── llama-2-7b-chat.ggmlv3.q4_0.bin
```

## Running the Application

1. **Start the backend server**
```bash
uvicorn main:app --reload --port 3000
```

2. **Access the API**
- Swagger UI: http://localhost:3000/docs
- API endpoint: http://localhost:3000/chat

## Usage Examples

1. **Basic product query**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I need a moisturizer for dry skin under $50"
    }
  ]
}
```

2. **Query with specific filters**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Show me face serums for sensitive skin"
    }
  ],
  "filters": {
    "price_range": [0, 100],
    "skin_type": "sensitive"
  },
  "excluded_ingredients": ["fragrance", "alcohol"]
}
```

## Common Issues & Troubleshooting

1. **Port already in use**
```bash
# Try different port
uvicorn main:app --reload --port 8080
```

2. **Memory issues**
- Ensure you have at least 8GB RAM available
- Close other memory-intensive applications
- Consider using the CPU-only version if GPU memory is limited

3. **Model loading issues**
- Verify model path in .env file
- Ensure model file is downloaded completely
- Check file permissions

## Contributing
Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.