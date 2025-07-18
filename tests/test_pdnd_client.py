
import pytest
from unittest.mock import patch, Mock
from pdnd_client.client import PDNDClient

# The following code is a test suite for the PDNDClient class,
# which tests the functionality of the get_status and post_api methods.
@pytest.fixture
# Create a fixture to initialize the PDNDClient with a test token and SSL verification disabled.
def client():
    return PDNDClient(token="test-token", verify_ssl=False)

# The test suite includes tests for successful and failed GET and POST requests,
# ensuring that the client behaves as expected under different conditions.
def test_get_status_success(client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "OK"

    # Mock the requests.get method to return a predefined response
    with patch("pdnd_client.client.requests.get", return_value=mock_response) as mock_get:
        status_code, text = client.get_status("https://example.com/status")
        mock_get.assert_called_once_with(
            "https://example.com/status",
            headers={"Authorization": "Bearer test-token"},
            verify=False
        )
        assert status_code == 200
        assert text == "OK"

# Test for successful POST request
def test_post_api_success(client):
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.text = "Created"
    data = {"key": "value"}

    with patch("pdnd_client.client.requests.post", return_value=mock_response) as mock_post:
        status_code, text = client.post_api("https://example.com/api", data)
        mock_post.assert_called_once_with(
            "https://example.com/api",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            json=data,
            verify=False
        )
        assert status_code == 201
        assert text == "Created"

# Test for failed GET request
def test_get_status_failure(client):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    with patch("pdnd_client.client.requests.get", return_value=mock_response):
        status_code, text = client.get_status("https://example.com/invalid")
        assert status_code == 404
        assert text == "Not Found"

# Test for failed POST request
def test_post_api_failure(client):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    data = {"invalid": "data"}

    with patch("pdnd_client.client.requests.post", return_value=mock_response):
        status_code, text = client.post_api("https://example.com/api", data)
        assert status_code == 400
        assert text == "Bad Request"
