import os
import json
from config import load_pterodactyl_instances
from db import list_players
import aiohttp
from urllib.parse import quote

async def run_command(instance, command):
    url = f"{instance['api_url']}/command"
    api_key = instance["api_key"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {"command": command}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            if resp.status != 204:
                print(f"Failed to run '{command}' on {instance['name']}: {resp.status}")
            else:
                print(f"'{command}' run on {instance['name']}")

async def update_all_whitelists():
    players = list_players()
    whitelist = [{"uuid": u[2], "name": u[0]} for u in players]
    whitelist_json = json.dumps(whitelist, indent=2)
    for instance in load_pterodactyl_instances():
        await update_whitelist_on_panel(instance, whitelist_json)
        await run_command(instance, "whitelist reload")

async def update_whitelist_on_panel(instance, whitelist_json):
    # Use query param for file path, send raw data as body
    file_path = instance["whitelist_path"]
    url = f"{instance['api_url']}/files/write?file={quote(file_path)}"
    api_key = instance["api_key"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "text/plain"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=whitelist_json.encode("utf-8")) as resp:
            if resp.status != 204:
                print(f"Failed to update whitelist on {instance['name']}: {resp.status}")
            else:
                print(f"Whitelist updated on {instance['name']}")

async def update_ops_on_panel(instance, ops_json):
    url = f"{instance['api_url']}/files/write?file={quote('/home/container/ops.json')}"
    api_key = instance["api_key"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "text/plain"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=ops_json.encode("utf-8")) as resp:
            if resp.status != 204:
                print(f"Failed to update ops.json on {instance['name']}: {resp.status}")
            else:
                print(f"ops.json updated on {instance['name']}")

async def update_all_ops():
    players = list_players()
    ops = []
    for u in players:
        # u: (mc_username, discord_username, uuid, op)
        if len(u) > 3 and u[3]:
            ops.append({"uuid": u[2], "name": u[0], "level": 4, "bypassesPlayerLimit": False})
    import json
    ops_json = json.dumps(ops, indent=2)
    for instance in load_pterodactyl_instances():
        await update_ops_on_panel(instance, ops_json)
