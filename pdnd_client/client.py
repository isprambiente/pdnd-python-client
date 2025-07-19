# La classe PDNDClient è responsabile dell'invio di richieste HTTP all'API PDND.
# Utilizza il JWT generato per l'autenticazione e può gestire sia richieste GET che POST.
# Lo script include anche opzioni per il debug e la verifica SSL,
# consentendo agli utenti di visualizzare output dettagliati e controllare la validazione del certificato SSL.
# La funzione parse_filters viene utilizzata per convertire una stringa di query in un dizionario,
# che può essere passato come parametro nelle richieste API.

import requests
import os
import json
import time
from datetime import datetime
from urllib.parse import urlencode

# La classe PDNDClient viene inizializzata con un token JWT e un'opzione per verificare i certificati SSL.
# Fornisce metodi per effettuare richieste GET e POST verso URL specificati.
class PDNDClient:
    def __init__(self):
        self.verify_ssl = True
        self.api_url = None
        self.status_url = None
        self.filters = {}
        self.debug = False
        self.token = ""
        self.token_file = "tmp/pdnd_token.json"
        self.token_exp = None  # Token expiration time, if applicable

    # Questo metodo recupera l'URL dell'API, che può essere sovrascritto dall'utente.
    def get_api_url(self) -> str:
        return self.api_url if hasattr(self, 'api_url') else None

    # Questo metodo imposta l'URL dell'API per le richieste successive.
    def set_api_url(self, api_url) -> bool:
        self.api_url = api_url
        return True

    # Imposta i filtri da utilizzare nelle richieste API.
    # Se viene fornita una stringa, la converte in un dizionario.
    def set_filters(self, filters) -> bool:
        if isinstance(filters, str):
            # Analizza la stringa nel formato "chiave1=val1&chiave2=val2"
            self.filters = dict(pair.split("=", 1) for pair in filters.split("&") if "=" in pair)
        elif isinstance(filters, dict):
            self.filters = filters
        else:
            raise ValueError("I filtri devono essere una stringa o un dizionario.")
        return True

    # Questo metodo imposta la modalità di debug, che controlla se stampare un output dettagliato.
    def set_debug(self, debug) -> bool:
        self.debug = debug
        return True

    # Questo metodo imposta il tempo di scadenza per il token.
    # Può essere una stringa nel formato "YYYY-MM-DD HH:MM:SS" oppure un oggetto datetime.
    # Se non viene fornito, il valore predefinito è None.
    def set_expiration(self, exp) -> bool:
        self.token_exp = exp
        return True

    # Questo metodo imposta l'URL di stato per le richieste GET.
    def set_status_url(self, status_url) -> bool:
        self.status_url = status_url
        return True

    def set_token(self, token) -> bool:
        self.token = token
        return True

    def set_token_file(self, token_file) -> bool:
        self.token_file = token_file
        return True

    def set_verify_ssl(self, verify_ssl) -> bool:
        self.verify_ssl = verify_ssl
        return True

    def get_api(self, token: str) -> [int, str]:
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

    # Questo metodo esegue una richiesta GET all'URL specificato e restituisce il codice di stato e il testo della risposta
    def get_status(self, url)  -> [int, str]:
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers, verify=self.verify_ssl)
        return response.status_code, response.text

    def get_token(self) -> str:
        return self.token

    def is_token_valid(self, exp) -> bool:
        if not self.token_exp and not exp:
            return False
        exp = exp or self.token_exp
        exp = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") if isinstance(exp, str) else exp
        if not isinstance(exp, datetime):
            raise ValueError("L'exp deve essere una stringa o un oggetto datetime")
        return time.time() < exp.timestamp()

    def load_token(self, file: str = None) -> [str, str]:
        file = file or self.token_file  # Usa il file passato o quello di default

        if not os.path.exists(file):
            return [None, None]

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return [None, None]

        if not data or "token" not in data or "exp" not in data:
            return [None, None]

        self.token = data["token"]
        self.token_exp = data["exp"]
        return data["token"], data["exp"]


    def save_token(self, token: str, exp: str, file: str = None) -> bool:
        if not token:
            raise ValueError("Il token non può essere vuoto")
        if not exp:
            raise ValueError("L'exp non può essere vuoto")
        if not isinstance(token, str):
            raise ValueError("Il token deve essere una stringa")
        if not isinstance(exp, str) and not isinstance(exp, datetime):
            raise ValueError("L'exp deve essere una stringa o un oggetto datetime")

        file = file or self.token_file  # Usa il file passato o quello di default
        exp = exp or self.token_exp  # Usa l'exp passato o quello corrente
        if not isinstance(exp, str):
            raise ValueError("L'exp deve essere una stringa nel formato 'YYYY-MM-DD HH:MM:SS'")
        try:
            datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")  # Verifica che l'exp sia nel formato corretto
        except ValueError:
            raise ValueError("L'exp deve essere una stringa nel formato 'YYYY-MM-DD HH:MM:SS'")

        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))

        data = {
            "token": token,
            "exp": exp
        }
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        self.token = token
        self.token_exp = exp
        return True
