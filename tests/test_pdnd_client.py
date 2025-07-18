
import pytest
from unittest.mock import patch, Mock
from pdnd_client.client import PDNDClient


# Il codice seguente è una suite di test per la classe PDNDClient,
# che verifica il funzionamento dei metodi get_status e post_api.
# Questi test utilizzano la libreria unittest.mock per simulare le risposte delle richieste HTTP
# e verificare che il client gestisca correttamente le risposte, sia in caso di successo che di errore.
# La suite include anche un fixture per inizializzare il client con un token di test e disabilitare la verifica SSL.
@pytest.fixture

# Crea un fixture per inizializzare il PDNDClient con un token di test e la verifica SSL disabilitata.
def client():
    return PDNDClient(token="test-token", verify_ssl=False)

# La suite di test include test per richieste GET e POST riuscite e fallite,
# assicurandosi che il client si comporti come previsto in diverse condizioni.
def test_get_status_success(client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "OK"


    # Simula il metodo requests.get per restituire una risposta predefinita
    with patch("pdnd_client.client.requests.get", return_value=mock_response) as mock_get:
        status_code, text = client.get_status("https://example.com/status")
        mock_get.assert_called_once_with(
            "https://example.com/status",
            headers={"Authorization": "Bearer test-token"},
            verify=False
        )
        assert status_code == 200
        assert text == "OK"

# Test per una richiesta POST riuscita
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

# Test per una richiesta GET fallita
def test_get_status_failure(client):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    with patch("pdnd_client.client.requests.get", return_value=mock_response):
        status_code, text = client.get_status("https://example.com/invalid")
        assert status_code == 404
        assert text == "Not Found"

# Test per una richiesta POST fallita
def test_post_api_failure(client):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    data = {"invalid": "data"}

    with patch("pdnd_client.client.requests.post", return_value=mock_response):
        status_code, text = client.post_api("https://example.com/api", data)
        assert status_code == 400
        assert text == "Bad Request"
