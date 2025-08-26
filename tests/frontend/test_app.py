import pytest
import httpx
from pytest_httpx import HTTPXMock
from frontend.app import check_api_health, send_message_to_backend
from pathlib import Path
import os
from dotenv import load_dotenv
import respx
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

@pytest.fixture
def backend_url():
    url = os.getenv("BACKEND_URL")
    if not url:
        pytest.fail("The BACKEND_URL environment variable is not set.")
    return url

def test_check_api_health_success(httpx_mock, backend_url):
    """Simulate API availability """

    httpx_mock.add_response(url=f"{backend_url}/health", status_code=200)
    
    assert check_api_health() is True

def test_check_api_health_failure(httpx_mock, backend_url):
    """Simulate an API error with status code 500."""
   
    httpx_mock.add_response(url=f"{backend_url}/health", status_code=500)
    
    assert check_api_health() is False

def test_send_message_to_backend_stream_success(httpx_mock: HTTPXMock, backend_url):
    """Simulate that a stream message is processed correctly."""
    response_content = [b"chunk1", b"chunk2", b"chunk3"]
    
    httpx_mock.add_response(
        method="POST",
        url=f"{backend_url}/chat",
        status_code=200,
        headers={"Content-Type": "text/plain; charset=utf-8"},
        #stream=iter(response_content),
        content = response_content
    )
    chunks = list(send_message_to_backend([{"role": "user", "content": "Hola"}], backend_url=backend_url))
    assert chunks == ["chunk1", "chunk2", "chunk3"]

@respx.mock
def test_stream_ok(backend_url):
    """Simulate that a stream message is processed correctly."""
    route = respx.post(f"{backend_url}/chat").mock(
        return_value=httpx.Response(
            200,
            content=[b"hola ", b"mundo", b" en ", b"streaming"],
            headers={"Content-Type": "text/plain; charset=utf-8"},
        )
    )

    chunks = list(send_message_to_backend([{"role": "user", "content": "hi"}]))
    assert route.called
    assert "".join(chunks) == "hola mundo en streaming"