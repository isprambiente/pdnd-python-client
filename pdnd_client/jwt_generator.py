# pdnd_client/jwt_generator.py

import time
import json
import base64
import requests
import jwt  # PyJWT
import secrets
import os
from datetime import datetime, timezone
from jwt import exceptions as jwt_exceptions

# Questa classe è responsabile della generazione di un token JWT basato sulla configurazione fornita.
# Utilizza la libreria PyJWT per creare e firmare il token con una chiave privata.
# Il token include claim come issuer, subject, audience e tempo di scadenza.
# La classe legge la chiave privata da un file specificato nella configurazione,
# e utilizza l'algoritmo RS256 per firmare il token.
# Il token generato può essere utilizzato per autenticare le richieste API al servizio PDND.
class JWTGenerator:
    def __init__(self, config):
        self.config = config
        self.debug = config.get("debug", False)
        self.client_id = config.get("clientId")
        self.endpoint = config.get("endpoint")
        self.env = config.get("env", "produzione")
        self.privKeyPath = config.get("privKeyPath")
        self.issuer = self.config.get("issuer")
        self.clientId = self.config.get("clientId")
        self.kid = self.config.get("kid")
        self.purposeId = self.config.get("purposeId")
        self.token_exp = None
        self.endpoint = "https://auth.interop.pagopa.it/token.oauth2"
        self.aud = "auth.interop.pagopa.it/client-assertion"


    def set_debug(self, debug) -> bool:
        self.debug = debug
        return True

    def set_env(self, env: "produzione") -> bool:
        self.env = env
        if self.env == "collaudo":
            self.endpoint = "https://auth.uat.interop.pagopa.it/token.oauth2"
            self.aud = "auth.uat.interop.pagopa.it/client-assertion"
        return True

    def request_token(self) -> [str, int]:
        if not self.client_id:
            raise ValueError("Client ID non specificato nella configurazione.")
        if not self.privKeyPath:
            raise ValueError("Percorso della chiave privata non specificato nella configurazione.")
        if not os.path.exists(self.privKeyPath):
            raise FileNotFoundError(f"File della chiave privata non trovato: {self.privKeyPath}")
        if not self.endpoint:
            raise ValueError("Endpoint non specificato nella configurazione.")
        if not self.issuer:
            raise ValueError("Issuer non specificato nella configurazione.")
        if not self.clientId:
            raise ValueError("Client ID non specificato nella configurazione.")
        if not self.kid:
            raise ValueError("KID non specificato nella configurazione.")
        if not self.purposeId:
            raise ValueError("Purpose ID non specificato nella configurazione.")

        with open(self.privKeyPath, "rb") as key_file:
            private_key = key_file.read()

        issued_at = int(time.time())
        expiration_time = issued_at + (43200 * 60)  # 30 giorni
        jti = secrets.token_hex(16)
        access_token = None

        payload = {
            "iss": self.issuer,
            "sub": self.clientId,
            "aud": self.aud,
            "purposeId": self.purposeId,
            "jti": jti,
            "iat": issued_at,
            "exp": expiration_time
        }

        headers = {
            "kid": self.kid,
            "alg": "RS256",
            "typ": "JWT"
        }

        try:
            client_assertion = jwt.encode(
                payload,
                private_key,
                algorithm="RS256",
                headers=headers
            )
        except jwt_exceptions.PyJWTError as e:
            raise Exception(f"❌ Errore durante la generazione del client_assertion JWT:\n{str(e)}")

        if self.debug:
            print(f"\n✅ Enviroment: {self.env}")
            print("\n✅ Client assertion generato con successo.")
            print(f"\n📄 JWT (client_assertion):\n{client_assertion}")

        data = {
            "client_id": self.client_id,
            "client_assertion": client_assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "grant_type": "client_credentials"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(self.endpoint, data=data, headers=headers)
            response.raise_for_status()  # Solleva eccezione per codici HTTP 4xx/5xx
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore nella richiesta POST: {e}")
            return None

        if response.status_code == 200:
            json_response = response.json()
            access_token = json_response.get("access_token")

            if access_token:
                try:
                    payload_part = access_token.split('.')[1]
                    padded = payload_part + '=' * (-len(payload_part) % 4)
                    decoded_payload = json.loads(base64.urlsafe_b64decode(padded))
                    self.token_exp = decoded_payload.get("exp")
                except Exception:
                    self.token_exp = None

                if self.debug:
                    if self.token_exp:
                        dt = datetime.fromtimestamp(self.token_exp, tz=timezone.utc)
                        token_exp_str = dt.astimezone().strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        token_exp_str = 'non disponibile'

                    print(f"\n🔐 Access Token:\n{access_token}")
                    print(f"\n⏰ Scadenza token (exp): {token_exp_str}")

                self.token = access_token
                self.token_exp = self.token_exp or expiration_time
            else:
                raise Exception(f"⚠️ Nessun access token trovato:\n{json.dumps(json_response, indent=2)}")

        return self.token, self.token_exp
