import os
import yaml  # type: ignore

CONFIG_PATH = "config.yaml"

def load_pterodactyl_instances():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    instances = []
    for server in config.get("servers", []):
        # Prefer direct api_key, fallback to env if api_key_env is present
        api_key = server.get("api_key")
        if not api_key and server.get("api_key_env"):
            api_key = os.environ.get(server["api_key_env"])
        instances.append({
            "name": server["name"],
            "api_url": server["api_url"],
            "api_key": api_key,
            "whitelist_path": server["whitelist_path"]
        })
    return instances

def load_admin_config():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    admin = config.get("admin", {})
    allowed_role_id = admin.get("allowed_role_id")
    allowed_user_ids = admin.get("allowed_user_ids", [])
    return allowed_role_id, allowed_user_ids

# Load Pterodactyl instances from config
PTERODACTYL_INSTANCES = load_pterodactyl_instances()
