# scripts/config.py

import yaml

def load_config(config_path="config.yaml"):
    """Load the YAML configuration file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
