import os

# Example config for Pterodactyl panel instances
# Add your panel info here
PTERODACTYL_INSTANCES = [
    {
        "name": "Server1",
        "api_url": "https://panel.example.com/api/client/servers/<SERVER_ID>/files/write",
        "api_key": os.environ.get("PTERO_API_KEY_SERVER1"),
        "whitelist_path": "/home/container/whitelist.json"
    },
    # Add more instances as needed, using os.environ.get for each key
]
