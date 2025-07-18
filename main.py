#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the PDND client application.
This script handles command-line arguments, configuration loading,
JWT generation, and API interactions.
"""
import argparse
import json
import tempfile
from pdnd_client.config import Config
from pdnd_client.jwt_generator import JWTGenerator
from pdnd_client.client import PDNDClient

# This function parses the filter string from command-line arguments
# and returns a dictionary of key-value pairs.
# The expected format is "key1=val1&key2=val2".
def parse_filters(filter_string):
    if not filter_string:
        return {}
    return dict(pair.split("=", 1) for pair in filter_string.split("&"))

# Main function to handle command-line arguments and execute the PDND client logic.
# It initializes the configuration, generates a JWT token,
# and performs API calls based on the provided arguments.
def main():
    # Set up argument parsing for command-line options.
    # This allows users to specify configuration files, environment keys,
    # API URLs, and other options when running the script.
    # The argparse module provides a way to handle command-line arguments
    # and automatically generates help messages.
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.json", help="Path to config JSON file")
    parser.add_argument("--env", default="produzione", help="Environment key in config file")
    parser.add_argument("--api-url", help="API URL to call with POST")
    parser.add_argument("--status-url", help="Status URL to call with GET")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL verification")
    parser.add_argument("--api-url-filters", help="Query parameters for API URL (e.g. key1=val1&key2=val2)")
    args = parser.parse_args()

    # Load the configuration from the specified JSON file and environment key.
    config = Config(args.config, args.env)

    # Initialize the PDND client with the generated JWT token and SSL verification settings.
    client = PDNDClient()
    client.set_debug(args.debug)
    client.set_verify_ssl(not args.no_verify_ssl)
    temp_dir = tempfile.gettempdir()
    client.set_token_file(f"{temp_dir}/pdnd_token_{config.get("purposeId")}.json")
    token, exp = client.load_token()

    if client.is_token_valid(exp):
        if args.debug:
            print(f"\n⏰ Scadenza token (exp): {exp}")
            print("\nToken valido, lo carico da file...")
        # Se il token è valido, lo carica da file
        token, exp = client.load_token()
    else:
        if args.debug:
            print("Token non valido o scaduto, ne richiedo uno nuovo...")
        # Generate a JWT token using the loaded configuration.
        jwt_gen = JWTGenerator(config)
        jwt_gen.set_debug(args.debug)
        jwt_gen.set_env(args.env)
        # Se il token non è valido, ne richiede uno nuovo
        token, exp = jwt_gen.request_token()
        # Salva il token per usi futuri
        client.save_token(token, exp)

    client.set_token(token)
    client.set_expiration(exp)

    # If the user has provided a status URL, make a GET request to that URL.
    if args.status_url:
        client.set_status_url(args.status_url)
        status_code, response = client.get_status(args.status_url)
        if args.debug:
            print(f"\nAPI URL Response [status_code: {status_code}]")
            parsed = json.loads(response)
            # Stampa in formato leggibile
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            print(pretty)
        else:
            print(response)

    # If the user has provided an API URL, parse the filters and make a POST request to that URL.
    if args.api_url:
        client.set_api_url(args.api_url)
        client.set_filters(parse_filters(args.api_url_filters))
        status_code, response = client.get_api(token)
        if args.debug:
            print(f"\nAPI URL Response [status_code: {status_code}]")
            parsed = json.loads(response)
            # Stampa in formato leggibile
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            print(pretty)
        else:
            print(response)

# If this script is run directly, execute the main function.
# This allows the script to be used as a standalone application.
# If imported as a module, the main function will not run automatically.
# This is a common Python practice to allow for both script execution and module import.
if __name__ == "__main__":
    main()
