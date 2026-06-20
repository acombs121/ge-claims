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

def load_customer_dataset(dataset_type):
    """
    Loads target dataset dictionary dynamically based on the current active customer context.
    Looks inside backend/data/datasets/[customer_id]/[dataset_type].json.
    """
    cfg = load_config()
    customer_id = cfg.get("customer_id", "default")
    
    # Try resolving in datasets folder
    dataset_path = os.path.join(DATA_DIR, 'datasets', customer_id, f"{dataset_type}.json")
    if os.path.exists(dataset_path):
        with open(dataset_path, 'r') as f:
            return json.load(f)
            
    # Fallback to direct DATA_DIR file
    direct_path = os.path.join(DATA_DIR, f"{dataset_type}.json")
    if os.path.exists(direct_path):
        with open(direct_path, 'r') as f:
            return json.load(f)
            
    raise FileNotFoundError(f"Customer dataset '{dataset_type}' not found for customer '{customer_id}' (Checked path: {dataset_path} and {direct_path})")
