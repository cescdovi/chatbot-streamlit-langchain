import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import logging
import openai
from openai import OpenAI
from backend.pydantic_models import ChatRequest
from fastapi.responses import StreamingResponse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env en la raíz del proyecto
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada. Por favor, asegúrate de establecerla.")

client_openai = OpenAI(api_key = OPENAI_API_KEY)
    

app = FastAPI(title="Chatbot using Streamlit and Langchain", version="1.0.0")

#configurar CORS
origins = [os.getenv("FRONTEND_URL", "http://localhost:8501")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "The chat app is running"}

@app.get("/health")
def health_check():
    logging.info("Health check endpoint called")
    return {"status": "ok"}


@app.post("/chat")
async def chat(user_message: ChatRequest):
    try:
        logging.info(f"Received request from user: {user_message.messages}")

        response = client_openai.responses.create(
            model="gpt-4.1",
            input = [
                {
                    "role": msg.role, 
                    "content": msg.content
                }
                for msg in user_message.messages
            ],
            stream=True
        )
        async def streaming_generator():
            for event in response:
                if event.type == "response.output_text.delta":
                    yield event.delta
                elif event.type == "response.completed":
                    break
        logging.info("Response from OpenAI API generated succesfully")

        return StreamingResponse(streaming_generator(), media_type="text/plain")


    except openai.RateLimitError as e:
        logging.error(f"RateLimitError: {e}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    
    except openai.AuthenticationError as e:
        logging.error(f"AuthenticationError: {e}")
        raise HTTPException(
            status_code = 401,
            detail="Authentication failed. Your OpenaAI API key is not valid."
        )
    
    except openai.APIConnectionError as e:
        logging.error(f"APIConnectionError: {e}")
        raise HTTPException(
            status_code = 503,
            detail="API connection error. Please check your internet connection."
        )
    
    except Exception as e:
        logging.error(f"An unexpected error occurred during the OpenAI API call: {e}")
        raise HTTPException(
            status_code = 500,
            detail=f"An unexpected error occurred during the OpenAI API call: {e}"
        )
                
if __name__ == "__main__":
    import uvicorn
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
