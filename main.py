#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto di ingresso principale per l'applicazione client PDND.
Questo script gestisce gli argomenti da linea di comando, il caricamento della configurazione,
la generazione del JWT e le interazioni con le API.
"""
import argparse
import json
import tempfile
from pdnd_client.config import Config
from pdnd_client.jwt_generator import JWTGenerator
from pdnd_client.client import PDNDClient

# Funzione principale che gestisce gli argomenti da linea di comando ed esegue la logica del client PDND.
# Inizializza la configurazione, genera un token JWT
# ed effettua chiamate API in base agli argomenti forniti.
def main():
    # Configura il parser degli argomenti da linea di comando.
    # Questo consente agli utenti di specificare file di configurazione, chiavi di ambiente,
    # URL delle API e altre opzioni durante l'esecuzione dello script.
    # Il modulo argparse fornisce un modo per gestire gli argomenti
    # e genera automaticamente i messaggi di aiuto.
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.json", help="Percorso del file JSON di configurazione")
    parser.add_argument("--env", default="produzione", help="Chiave dell'ambiente nel file di configurazione")
    parser.add_argument("--api-url", help="URL dell'API da chiamare con POST")
    parser.add_argument("--status-url", help="URL di stato da chiamare con GET")
    parser.add_argument("--debug", action="store_true", help="Abilita l'output di debug")
    parser.add_argument("--pretty", action="store_true", help="Abilita l'output dei json formattandoli in modo leggibile")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disabilita la verifica SSL")
    parser.add_argument("--api-url-filters", help="Parametri di query per l'API (es. chiave1=val1&chiave2=val2)")
    args = parser.parse_args()

    # Carica la configurazione dal file JSON specificato e dalla chiave ambiente.
    config = Config(args.config, args.env)

    # Inizializza il client PDND con il token JWT generato e le impostazioni SSL.
    client = PDNDClient()
    client.set_debug(args.debug)
    client.set_verify_ssl(not args.no_verify_ssl)
    temp_dir = tempfile.gettempdir()
    client.set_token_file(f"{temp_dir}/pdnd_token_{config.get('purposeId')}.json")
    token, exp = client.load_token()

    if client.is_token_valid(exp):
        # Se il token è valido, lo carica da file
        # token, exp = client.load_token()
        if args.debug:
            print(f"\n⏰ Scadenza token (exp): {exp}")
            print("\nToken valido, lo carico da file...")
            print(f"\n{token}\n")
    else:
        if args.debug:
            print("Token non valido o scaduto, ne richiedo uno nuovo...")
        # Genera un token JWT usando la configurazione caricata
        jwt_gen = JWTGenerator(config)
        jwt_gen.set_debug(args.debug)
        jwt_gen.set_env(args.env)
        # Se il token non è valido, ne richiede uno nuovo
        token, exp = jwt_gen.request_token()
        # Salva il token per usi futuri
        client.save_token(token, exp)

    client.set_token(token)
    client.set_expiration(exp)

    # Se l'utente ha fornito un URL di stato, effettua una richiesta GET a quell'URL.
    if args.status_url:
        client.set_status_url(args.status_url)
        status_code, response = client.get_status(args.status_url)
        if args.debug or args.pretty:
            print(f"\nRisposta API [status_code: {status_code}]")
            parsed = json.loads(response)
            # Stampa in formato leggibile
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            print(pretty)
        else:
            print(response)

    # Se l'utente ha fornito un URL API, analizza i filtri ed effettua una richiesta POST a quell'URL.
    if args.api_url:
        client.set_api_url(args.api_url)
        client.set_filters(args.api_url_filters)
        status_code, response = client.get_api(token)
        if args.debug or args.pretty:
            print(f"\nRisposta API [status_code: {status_code}]")
            parsed = json.loads(response)
            # Stampa in formato leggibile
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            print(pretty)
        else:
            print(response)

# Se questo script viene eseguito direttamente, esegue la funzione main.
# Questo consente di usare lo script come applicazione standalone.
# Se importato come modulo, la funzione main non verrà eseguita automaticamente.
# È una pratica comune in Python per permettere sia l'esecuzione diretta che l'importazione.
if __name__ == "__main__":
    main()
