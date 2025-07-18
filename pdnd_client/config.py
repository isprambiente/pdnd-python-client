# pdnd_client/config.py

import json
import os

# La classe Config viene inizializzata con un percorso verso un file di configurazione e una chiave di ambiente.
# Legge la configurazione dal file e la memorizza in un dizionario.
# Il metodo get consente di recuperare valori specifici della configurazione, con un valore predefinito opzionale.
class Config:
    # Questo metodo inizializza l'oggetto Config caricando la configurazione da un file JSON.
    def __init__(self, config_path, env):
        self.env = env
        with open(config_path, "r") as f:
            full_config = json.load(f)
        if env not in full_config:
            raise ValueError(f"Environment '{env}' not found in config file.")
        self.config = full_config[env]

    # Questo metodo recupera un valore di configurazione tramite una chiave, restituendo un valore predefinito se la chiave non viene trovata.
    def get(self, key, default=None):
        return self.config.get(key, default)
