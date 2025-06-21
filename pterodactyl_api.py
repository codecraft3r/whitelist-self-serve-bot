import aiohttp
import json
from pterodactyl_config import PTERODACTYL_INSTANCES
from db import list_players

async def update_all_whitelists():
    players = list_players()
    whitelist = [{"uuid": u[2], "name": u[0]} for u in players]
    whitelist_json = json.dumps(whitelist, indent=2)
    for instance in PTERODACTYL_INSTANCES:
        await update_whitelist_on_panel(instance, whitelist_json)

async def update_whitelist_on_panel(instance, whitelist_json):
    url = instance["api_url"]
    api_key = instance["api_key"]
    path = instance["whitelist_path"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "root": False,
        "file": path,
        "content": whitelist_json,
        "truncate": True
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            if resp.status != 204:
                print(f"Failed to update whitelist on {instance['name']}: {resp.status}")
            else:
                print(f"Whitelist updated on {instance['name']}")
