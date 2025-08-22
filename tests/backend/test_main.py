'''
Tests for the API used in the backend.
It covers:
    - Testing the endpoints: root, health, and chat
    - Handling error tests: rate limit, authentication, and connection errors
    - Testing streaming response from the /chat endpoint
'''
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from openai import RateLimitError, AuthenticationError, APIConnectionError
from pydantic import BaseModel
import httpx
from backend.main import app, client_openai
from backend.pydantic_models import ChatRequest, ChatResponse, Message


#create a client for testing
client_app = TestClient(app)

#testing endpoints
def test_root_endpoint():
    response = client_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "The chat app is running"}


def test_health_endpoint():
    response = client_app.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_rate_limit_error(mocker):
    """
    Simulate a RateLimitError from OpenAI API when calling client.responses.create.
    """
    # create mock objects for 'response' and 'body'
    mock_response = MagicMock(status_code=429)
    mock_body = MagicMock(error={"type": "rate_limit_exceeded"})

    mock_rate_limit_error = RateLimitError(
        "Rate limit exceeded",
        response=mock_response,
        body=mock_body
    )

    mocker.patch.object(
        client_openai.responses,
        "create",
        side_effect=mock_rate_limit_error
    )
    
    payload = {
        "messages": [
            {"role": "user", "content": "Test rate limit"}
        ]
    }
    
    response = client_app.post("/chat", json=payload)
    
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded. Try again later."


def test_chat_authentication_error(mocker):
    """
    Simulate an AuthenticationError from OpenAI API when calling client.responses.create.
    """
    # create mock objects for 'response' and 'body'
    mock_response = MagicMock(status_code=401)
    mock_body = MagicMock(error={"type": "invalid_api_key"})

    mock_authentication_error = AuthenticationError(
        message = "Invalid API key",
        response=mock_response,
        body=mock_body
    )

    mocker.patch.object(
        client_openai.responses,
        "create",
        side_effect=mock_authentication_error
    )
    
    payload = {
        "messages": [
            {"role": "user", "content": "Test authentication error"}
        ]
    }
    
    response = client_app.post("/chat", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication failed. Your OpenaAI API key is not valid."

def test_chat_api_connection_error(mocker):
    """
    Simulate an APIConnectionError from the OpenAI API when calling client.responses.create.
    """
    # create mock objects for 'response' and 'body'
    #mock_response = MagicMock(status_code=503)
    mock_request = MagicMock(httpx.post)

    mock_api_connection_error = APIConnectionError(
        message = "API connection error",
        request=mock_request
        #body=mock_body
    )

    mocker.patch.object(
        client_openai.responses,
        "create",
        side_effect=mock_api_connection_error
    )
    
    payload = {
        "messages": [
            {"role": "user", "content": "Test API connection error"}
        ]
    }
    
    response = client_app.post("/chat", json=payload)
    
    assert response.status_code == 503
    assert response.json()["detail"] == "API connection error. Please check your internet connection."

def test_chat_unexpected_error(mocker):
    """
    Test that the /chat endpoint handles an unexpected error and returns a 500 status code.
    """
    mocker.patch.object(
        client_openai.responses,
        "create",
        side_effect=Exception("An unexpected internal error occurred")
    )

    payload = {
        "messages": [
            {"role": "user", "content": "Test unexpected error"}
        ]
    }
    
    response = client_app.post("/chat", json=payload)
    
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json()["detail"]