# pdnd_client/config.py

import json
import os

# The Config class initializes with a path to a configuration file and an environment key.
# It reads the configuration from the file and stores it in a dictionary.
# The get method allows retrieval of specific configuration values, with an optional default.
class Config:
    # This method initializes the Config object by loading the configuration from a JSON file.
    def __init__(self, config_path, env):
        self.env = env
        with open(config_path, "r") as f:
            full_config = json.load(f)
        if env not in full_config:
            raise ValueError(f"Environment '{env}' not found in config file.")
        self.config = full_config[env]
    # This method retrieves a configuration value by key, returning a default value if the key is not found.
    def get(self, key, default=None):
        return self.config.get(key, default)
