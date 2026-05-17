import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def load_config():
    """Loads system-wide application JSON properties."""
    config_path = os.path.join(DATA_DIR, 'config.json')
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return json.load(f)



def get_parameter_default(key, fallback=None):
    """Reads target default setting returning an agnostic application parameter."""
    cfg = load_config()
    defaults = cfg.get("demo_defaults", {})
    return defaults.get(key, fallback)
