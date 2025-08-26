import streamlit as st
import os
import logging
from typing import List, Dict
import httpx
from pathlib import Path
from dotenv import load_dotenv


#configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# load environment variables from .env file in the root of the project
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

#backend URL 
BACKEND_URL = os.getenv("BACKEND_URL")

# configuring timeouts
HEALTH_CHECK_TIMEOUT = 10
QUERY_TIMEOUT = 60

def check_api_health() -> bool:
    """Verifica si la API backend está accesible y saludable."""
    try:
        logger.info(f"Checking backend health at {BACKEND_URL}/health")

        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/health", timeout=5)
            response.raise_for_status() 
            
        logger.info("Backend API is healthy.")
        return True
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred during health check: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during health check: {e}")
        return False


def send_message_to_backend(user_message: List[Dict[str, str]], backend_url: str = BACKEND_URL,client: httpx.Client = None):
    """
    Sends a message to the backend API and yields the response in a streaming manner.
    """
    if client is None:
        client = httpx.Client() 

    try:
        logger.info("Sending message to backend...")
        with client.stream(
            method="POST", 
            url=f"{backend_url}/chat", 
            json={"messages": user_message},
            timeout=10 
        ) as response:
            logger.info(f"REQUEST URL: {response.url}")
            logger.info(f"RESPONSE STATUS: {response.status_code}")
            logger.info(f"RESPONSE HEADERS: {response.headers}")

            response.raise_for_status()

            
            logger.info("\n--- Init of the stream ---\n")
            # iterate over the response chunks
            for chunk in response.iter_bytes():
                decoded_chunk = chunk.decode("utf-8")
                yield decoded_chunk
            logger.info("\n--- End of the stream ---")

    except httpx.TimeoutException:
        logger.error("Request to backend timed out.")
        yield "Error: The request to the backend timed out."
    except httpx.ConnectError:
        logger.error("Connection error occurred while connecting to the backend.")
        yield "Error: Could not connect to the backend service."
    except httpx.HTTPStatusError as e:
        logger.error(f"API error: HTTP {e.response.status_code}")
        yield f"Error: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        yield f"Error: An unexpected error occurred: {e}"

#Title and configuration of the page
st.set_page_config(
    page_title="Chatbot using Streamlit, FastAPI and Langchain",
)

st.title("Chatbot using Streamlit, FastAPI and Langchain")
st.header("About")
st.markdown(
    """
    This is a chatbot powered by an agent that uses a **Graph RAG** approach.

    The agent answers your questions by querying a **graph database** containing structured information about Valencian heritage. 
    This data was extracted directly from the audio of the videos in the following YouTube playlist:
    [Arxiu Valencià del Disseny](https://www.youtube.com/playlist?list=PL6wN5YWAm7K9kZauivJqV4QtOeohng0HW).
    """
)


#init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#show conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#box for user input
if prompt :=st.chat_input(
    placeholder = "Type your message here"
):
    #display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)
    
    #add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # display AI message
    with st.chat_message("assistant"):
        response = st.write_stream(send_message_to_backend(st.session_state.messages))

    #add AI message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})