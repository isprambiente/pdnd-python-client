# The PDNDClient class is responsible for making HTTP requests to the PDND API.
# It uses the generated JWT for authentication and can handle both GET and POST requests.
# The script also includes options for debugging and SSL verification,
# allowing users to see detailed output and control SSL certificate validation.
# The parse_filters function is used to convert a query string into a dictionary,
# which can be passed as parameters in API requests.eneration, and API interactions.

import requests
import os
import json
import time
from datetime import datetime
from urllib.parse import urlencode

# The PDNDClient class is initialized with a JWT token and an option to verify SSL certificates.
# It provides methods to make GET and POST requests to specified URLs.
class PDNDClient:
    def __init__(self):
        self.verify_ssl = True
        self.api_url = None
        self.status_url = None
        self.filters = {}
        self.debug = False
        self.token = ""
        self.token_file = "pdnd_token.json"
        self.token_exp = None  # Token expiration time, if applicable

    # This method retrieves the API URL, which can be overridden by the user.
    def get_api_url(self):
        return self.api_url if hasattr(self, 'api_url') else None

    # This method sets the API URL for subsequent requests.
    def set_api_url(self, api_url):
        self.api_url = api_url

    # This method sets the filters to be used in API requests.
    def set_filters(self, filters):
        self.filters = filters

    # This method sets the debug mode, which controls whether detailed output is printed.
    def set_debug(self, debug):
        self.debug = debug

    def set_expiration(self, exp):
        self.token_exp = exp

    # This method sets the status URL for GET requests.
    def set_status_url(self, status_url):
        self.status_url = status_url

    def set_token(self, token):
        self.token = token

    def set_token_file(self, token_file):
        self.token_file = token_file

    def set_verify_ssl(self, verify_ssl):
        self.verify_ssl = verify_ssl

    def get_api(self, token: str):
        url = self.api_url if hasattr(self, 'api_url') and self.api_url else self.get_api_url()

        # Aggiunta dei filtri come query string
        if hasattr(self, 'filters') and self.filters:
            query = urlencode(self.filters, doseq=True)
            separator = '&' if '?' in url else '?'
            url += separator + query

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "*/*"
        }

        try:
            response = requests.get(url, headers=headers, verify=self.verify_ssl)
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Errore nella chiamata API: {e}")

        status_code = response.status_code
        body = response.text

        if not response.ok:
            raise Exception(f"❌ Errore nella chiamata API: {response.text}")

        if self.debug:
            try:
                decoded = response.json()
                body = json.dumps(decoded, indent=2, ensure_ascii=False)
            except Exception:
                pass  # Se non è JSON, lascia il body così com'è

        return status_code, body

    # This method performs a GET request to the specified URL and returns the status code and response text.
    def get_status(self, url):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers, verify=self.verify_ssl)
        return response.status_code, response.text

    def is_token_valid(self, exp) -> bool:
        if not self.token_exp and not exp:
            return False
        exp = exp or self.token_exp
        exp = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") if isinstance(exp, str) else exp
        if not isinstance(exp, datetime):
            raise ValueError("L'exp deve essere una stringa o un oggetto datetime")
        return time.time() < exp.timestamp()

    def load_token(self, file: str = None):
        file = file or self.token_file  # Usa il file passato o quello di default

        if not os.path.exists(file):
            return None

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

        if not data or "token" not in data or "exp" not in data:
            return None

        self.token_exp = data["exp"]
        return data["token"], data["exp"]


    def save_token(self, token: str, exp: str, file: str = None):
        file = file or self.token_file  # Usa il file passato o quello di default
        exp = exp or self.token_exp  # Usa l'exp passato o quello corrente
        data = {
            "token": token,
            "exp": exp
        }
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)





