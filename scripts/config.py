# scripts/config.py

import os
import yaml

def load_config(config_path=None):
    """Load the YAML configuration file."""
    if config_path is None:
        current_dir = os.path.dirname(__file__)
        config_path = os.path.join(current_dir, "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config
