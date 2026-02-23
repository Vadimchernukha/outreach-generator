"""
core/config_loader.py
Loads and validates a client YAML config file.
"""

import os
import yaml


REQUIRED_KEYS = [
    "client_name",
    "language",
    "gemini_model",
    "company_context",
    "csv_columns",
    "dynamic_fields_after",
    "generation_prompt",
    "humanize_prompt",
    "tone_rules",
]


def load_config(client_name: str, clients_dir: str = "clients") -> dict:
    """
    Load a client config from clients/<client_name>.yaml
    Raises clear errors if file is missing or config is incomplete.
    """
    path = os.path.join(clients_dir, f"{client_name}.yaml")

    if not os.path.exists(path):
        available = [
            f.replace(".yaml", "")
            for f in os.listdir(clients_dir)
            if f.endswith(".yaml") and not f.startswith("_")
        ]
        raise FileNotFoundError(
            f"Client config not found: '{path}'\n"
            f"Available clients: {available}"
        )

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Validate required keys
    missing = [k for k in REQUIRED_KEYS if k not in config]
    if missing:
        raise ValueError(
            f"Client config '{path}' is missing required keys: {missing}"
        )

    print(f"Config loaded: {config['client_name']} ({path})")
    return config
