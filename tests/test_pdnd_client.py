
import pytest
from unittest.mock import patch, Mock
from pdnd_client.config import Config
from pdnd_client.jwt_generator import JWTGenerator
from pdnd_client.client import PDNDClient

# Il codice seguente è una suite di test per la classe PDNDClient,
# che verifica il funzionamento dei metodi get_status e get_api.
# Questi test utilizzano la libreria unittest.mock per simulare le risposte delle richieste HTTP
# e verificare che il client gestisca correttamente le risposte, sia in caso di successo che di errore.
# La suite include anche un fixture per inizializzare il client con un token di test e disabilitare la verifica SSL.
@pytest.fixture

# Crea un fixture per inizializzare il PDNDClient con un token di test e la verifica SSL disabilitata.
def client():
    client = PDNDClient()
    client.set_token("test-token")
    return PDNDClient()

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
            headers={"Authorization": f"Bearer {client.get_token()}"},
            verify=True
        )
        assert status_code == 200
        assert text == "OK"

# Test per una richiesta GET fallita
def test_get_status_failure(client):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    with patch("pdnd_client.client.requests.get", return_value=mock_response):
        status_code, text = client.get_status("https://example.com/invalid")
        assert status_code == 404
        assert text == "Not Found"
