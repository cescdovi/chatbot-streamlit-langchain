'''
Tests for the Pydantic models used in the backend.
It covers:
    - Basic validation tests
    - Invalid data handling tests
    - Default values tests
'''
import pytest
from pydantic import ValidationError
from backend.pydantic_models import ChatRequest, ChatResponse, Message

# Test para el modelo Message
def test_message_model():
    message = Message(role="user", content="Hello, how are you?")
    assert message.role == "user"
    assert message.content == "Hello, how are you?"


def test_message_model_raises_error_for_invalid_data():
    with pytest.raises(ValidationError):
        Message(role=123, content="Contenido de prueba")


def test_message_model_raises_error_for_missing_fields():
    with pytest.raises(ValidationError):
        Message(role="user")  # Falta el campo 'content'


# Test para el modelo ChatRequest
def test_chat_request_model_with_default_values():
    messages = [Message(role="user", content="Test with default values")]
    chat_request = ChatRequest(messages=messages)
    
    assert chat_request.messages == messages
    assert chat_request.model == "gpt-3.5-turbo"
    assert chat_request.temperature == 0.7
    assert chat_request.max_tokens == 1000


def test_chat_request_model_with_provided_values():
    messages = [Message(role="assistant", content="This is a testing response")]
    chat_request = ChatRequest(
        messages=messages,
        model="gpt-4",
        temperature=0.5,
        max_tokens=150
    )
    assert chat_request.messages[0].role == "assistant"
    assert chat_request.messages[0].content == "This is a testing response"
    assert chat_request.temperature == 0.5
    assert chat_request.max_tokens == 150


def test_chat_request_model_raises_error_for_missing_messages():
    with pytest.raises(ValidationError):
        ChatRequest()

def test_chat_response_model_is_valid():
    response = ChatResponse(
        response = "This is a test response",
        usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    )
    assert response.response == "This is a test response"
    assert response.usage == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}