# PDND Python Client

![Python Security Audit](https://github.com/isprambiente/pdnd-python-client/actions/workflows/security-audit.yml/badge.svg)
![Python CI](https://github.com/isprambiente/pdnd-python-client/actions/workflows/python-ci.yml/badge.svg)
![License](https://img.shields.io/github/license/isprambiente/pdnd-python-client)
![Python Version](https://img.shields.io/pypi/pyversions/pdnd-python-client)
![Latest PyPI Version](https://img.shields.io/pypi/v/pdnd-python-client)

Client Python per autenticazione e interazione con le API della Piattaforma Digitale Nazionale Dati (PDND).

## Licenza

MIT

## Requisiti

- Python >= 3.10 (versioni precedenti sono [EOL](https://endoflife.date/python))
- PIP

## Installazione

1. Installa la libreria via composer:
   ```bash
   pip install pdnd-python-client
   ```

2. Configura il file JSON con i parametri richiesti (esempio in `configs/sample.json`):
   ```json
    {
      "collaudo": {
        "kid": "kid",
        "issuer": "issuer",
        "clientId": "clientId",
        "purposeId": "purposeId",
        "privKeyPath": "/tmp/key.priv"
      },
      "produzione": {
        "kid": "kid",
        "issuer": "issuer",
        "clientId": "clientId",
        "purposeId": "purposeId",
        "privKeyPath": "/tmp/key.priv"
      }
    }
   ```
## Istruzioni base

```python

from pdnd_client.config import Config
from pdnd_client.jwt_generator import JWTGenerator
from pdnd_client.client import PDNDClient

config = Config("./configs/sample.json")
jwt_gen = JWTGenerator(config)
token, exp = jwt_gen.request_token()
client = PDNDClient()
client.set_token(token)
client.set_expiration(exp)
client.set_api_url("https://www.tuogateway.example.it/indirizzo/della/api")
client.set_filters("id=1234")
status_code, response = client.get_api()

# Stampa il risultato
print(response)

```

## Leggi e Salva il token

```python

from pdnd_client.config import Config
from pdnd_client.jwt_generator import JWTGenerator
from pdnd_client.client import PDNDClient

# Inizializza la configurazione
# Load the configuration from the specified JSON file and environment key.
config = Config("./configs/sample.json")

# Initialize the PDND client with the generated JWT token and SSL verification settings.
client = PDNDClient()
# Carica il token file precedentemente salvato
token, exp = client.load_token()
# verifica la scadenza del token
if not client.is_token_valid(exp):
    # Generate a JWT token using the loaded configuration.
    jwt_gen = JWTGenerator(config)
    # Se il token non è valido, ne richiede uno nuovo
    token, exp = jwt_gen.request_token()
    # Salva su file esterno il token e la scadenza
    client.save_token(token, exp)

client.set_api_url("https://www.tuogateway.example.it/indirizzo/della/api")
client.set_filters("id=1234")
status_code, response = client.get_api(token)

# Stampa il risultato
print(response)

```

### Funzionalità aggiuntive

**Disabilita verifica certificato SSL**

La funzione `client.set_verify_ssl(False)` Disabilita verifica SSL per ambiente impostato (es. collaudo).
Default: true

**Salva il token**

La funzione `client.save_token(token, exp)` consente di memorizzare il token e la scadenza e non doverlo richiedere a ogni chiamata.

**Carica il token salvato**

La funzione `client.load_token()` consente di richiamare il token precedentemente salvato.

**Valida il token salvato**

La funzione `client.is_token_valid()` verifica la validità del token salvato.

**Imposta nome al token file**

La funzione `client.set_token_file("tmp/tuofile.json")` imposta un nome personalizzato al file.

## Utilizzo da CLI

Esegui il client dalla cartella principale:

```python
python main.py --api-url "https://api.pdnd.example.it/resource" --config /configs/progetto.json
```

### Opzioni disponibili

- `--env` : Specifica l'ambiente da usare (es. collaudo, produzione). Default: `produzione`
- `--config` : Specifica il percorso completo del file di configurazione (es: `--config /configs/progetto.json`)
- `--debug` : Abilita output dettagliato
- `--pretty` : Abilita l'output dei json formattato in modo leggibile
- `--api-url` : URL dell’API da chiamare dopo la generazione del token
- `--api-url-filters` : Filtri da applicare all'API (es. ?parametro=valore)
- `--status-url` : URL dell’API di status per verificare la validità del token
- `--json`: Stampa le risposte delle API in formato JSON
- `--save`: Salva il token per evitare di richiederlo a ogni chiamata
- `--no-verify-ssl`: Disabilita la verifica SSL (utile per ambienti di collaudo)
- `--help`: Mostra questa schermata di aiuto

### Esempi

**Chiamata API generica:**
```bash
python main.py --api-url="https://api.pdnd.example.it/resource" --config /configs/progetto.json
```

**Verifica validità token:**
```bash
python main.py --status-url="https://api.pdnd.example.it/status" --config /configs/progetto.json
```

**Debug attivo:**
```bash
python main.py --debug --api-url="https://api.pdnd.example.it/resource"
```

**Pretty attivo:**
```bash
python main.py --pretty --api-url="https://api.pdnd.example.it/resource"
```

### Opzione di aiuto

Se esegui il comando con `--help` oppure senza parametri, viene mostrata una descrizione delle opzioni disponibili e alcuni esempi di utilizzo:

```bash
python main.py --help
```

**Output di esempio:**
```
Utilizzo:
  python main.py -c /percorso/config.json [opzioni]

Opzioni:
  --env             Specifica l'ambiente da usare (es. collaudo, produzione)
                    Default: produzione
  --config          Specifica il percorso completo del file di configurazione
  --debug           Abilita output dettagliato
  --api-url         URL dell’API da chiamare dopo la generazione del token
  --api-url-filters Filtri da applicare all'API (es. ?parametro=valore)
  --status-url      URL dell’API di status per verificare la validità del token
  --json            Stampa le risposte delle API in formato JSON
  --save            Salva il token per evitare di richiederlo a ogni chiamata
  --no-verify-ssl   Disabilita la verifica SSL (utile per ambienti di collaudo)
  --help            Mostra questa schermata di aiuto

Esempi:
  python main.py --api-url="https://api.pdnd.example.it/resource" --config /percorso/config.json
  python main.py --status-url="https://api.pdnd.example.it/status" --config /percorso/config.json
  python main.py --debug --api-url="https://api.pdnd.example.it/resource"
```

## Variabili di ambiente supportate

Se un parametro non è presente nel file di configurazione, puoi definirlo come variabile di ambiente:

- `PDND_KID`
- `PDND_ISSUER`
- `PDND_CLIENT_ID`
- `PDND_PURPOSE_ID`
- `PDND_PRIVKEY_PATH`

## Note

- Il token viene salvato in un file temporaneo e riutilizzato finché è valido.
- Gli errori specifici vengono gestiti tramite la classe `PdndException`.

## Esempio di configurazione minima

```json
{
  "produzione": {
    "kid": "kid",
    "issuer": "issuer",
    "clientId": "clientId",
    "purposeId": "purposeId",
    "privKeyPath": "/tmp/key.pem"
  }
}
```
## Esempio di configurazione per collaudo e prosuzione

```json
{
  "collaudo": {
    "kid": "kid",
    "issuer": "issuer",
    "clientId": "clientId",
    "purposeId": "purposeId",
    "privKeyPath": "/tmp/key.pem"
  },
  "produzione": {
    "kid": "kid",
    "issuer": "issuer",
    "clientId": "clientId",
    "purposeId": "purposeId",
    "privKeyPath": "/tmp/key.pem"
  }
}
```
---

## Contribuire

Le pull request sono benvenute! Per problemi o suggerimenti, apri una issue.
