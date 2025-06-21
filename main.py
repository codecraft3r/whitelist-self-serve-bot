from os import environ
import sys

import discord
from discord import option
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import aiohttp
from pterodactyl_api import update_all_whitelists, update_all_ops
from mojang_api import get_mojang_profile

from db import init_db, add_player, get_player_by_discord, list_players, is_blocked, block_user, remove_player_by_discord
from config import load_pterodactyl_instances, load_admin_config
import json

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)
register_only = False

allowed_role_id, allowed_user_ids = load_admin_config()

def is_whitelist_admin():
    async def predicate(ctx):
        # Allow if user has the allowed role ID
        if allowed_role_id and any(role.id == allowed_role_id for role in ctx.author.roles):
            return True
        # Allow if user ID is in allowed list
        if ctx.author.id in allowed_user_ids:
            return True
        await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        return False
    return commands.check(predicate)

@bot.event
async def on_ready():
    init_db()
    if register_only:
        await bot.register_commands()
        exit(0)
    print(f"Logged in as {bot.user}")

@bot.slash_command()
@option("username", discord.SlashCommandOptionType.string, parameter_name="mc_username")
async def register(ctx, mc_username):
    discord_username = str(ctx.author)
    if is_blocked(discord_username=discord_username) or is_blocked(mc_username=mc_username):
        await ctx.respond("You are blocked from registering.", ephemeral=True)
        return
    if get_player_by_discord(discord_username):
        await ctx.respond("You have already registered a Minecraft username.", ephemeral=True)
        return
    data = await get_mojang_profile(mc_username)
    if not data:
        await ctx.respond(f"Username '{mc_username}' does not exist.", ephemeral=True)
        return
    uuid = data.get('id')
    # Check admin
    is_admin = False
    if hasattr(ctx.author, 'roles') and any(role.id == allowed_role_id for role in ctx.author.roles):
        is_admin = True
    if ctx.author.id in allowed_user_ids:
        is_admin = True
    add_player(mc_username, discord_username, uuid, op=1 if is_admin else 0)
    await update_all_whitelists()
    if is_admin:
        await update_all_ops()
    op_msg = "\nYou will need to restart the server to apply your operator permissions."
    await ctx.respond(f"You have been registered as: {mc_username}. {op_msg if is_admin else ""}", ephemeral=True)

# Admin command to list all users
@bot.slash_command()
@is_whitelist_admin()
async def list_users(ctx):
    users = list_players()
    if not users:
        await ctx.respond("No users found.", ephemeral=True)
        return
    msg = "Registered users:\n" + "\n".join([f"MC: {u[0]}, Discord: {u[1]}, UUID: {u[2]}" for u in users])
    await ctx.respond(msg, ephemeral=True)

# Admin command to add users without Discord
@bot.slash_command()
@option("mc_username", discord.SlashCommandOptionType.string)
@option("uuid", discord.SlashCommandOptionType.string)
@option("discord_username", discord.SlashCommandOptionType.user, required=False)
@is_whitelist_admin()
async def add_user(ctx, mc_username, uuid, discord_username=None):
    if not discord_username:
        discord_username = "(none)"
    if get_player_by_discord(discord_username) and discord_username != "(none)":
        await ctx.respond("This Discord user already has a Minecraft username registered.", ephemeral=True)
        return
    # Check admin
    is_admin = False
    if hasattr(ctx.author, 'roles') and any(role.id == allowed_role_id for role in ctx.author.roles):
        is_admin = True
    if ctx.author.id in allowed_user_ids:
        is_admin = True
    add_player(mc_username, discord_username, uuid, op=1 if is_admin else 0)
    await update_all_whitelists()
    if is_admin:
        await update_all_ops()
    await ctx.respond(f"Added user: MC={mc_username}, Discord={discord_username}, UUID={uuid}", ephemeral=True)

# Admin command to block users
@bot.slash_command()
@is_whitelist_admin()
@option("discord_username", discord.SlashCommandOptionType.user, required=False)
@option("mc_username", discord.SlashCommandOptionType.string, required=False)
async def block(ctx, discord_username=None, mc_username=None):
    if not discord_username and not mc_username:
        await ctx.respond("Provide at least a Discord username or MC username to block.", ephemeral=True)
        return
    block_user(discord_username, mc_username)
    await ctx.respond(f"Blocked user: Discord={discord_username}, MC={mc_username}", ephemeral=True)

# Admin command to sync whitelist
@bot.slash_command()
@is_whitelist_admin()
async def sync_whitelist(ctx):
    await ctx.defer(ephemeral=True)
    await update_all_whitelists()
    await update_all_ops()
    await ctx.respond("Whitelist sync triggered.", ephemeral=True)

@bot.slash_command()
async def deregister(ctx):
    discord_username = str(ctx.author)
    if not get_player_by_discord(discord_username):
        await ctx.respond("You are not registered.", ephemeral=True)
        return
    remove_player_by_discord(discord_username)
    await update_all_whitelists()
    await ctx.respond("You have been deregistered and removed from the whitelist.", ephemeral=True)

    
if __name__ == "__main__":
    load_dotenv()
    if "-r" in sys.argv:
        register_only = True

    bot.run(environ.get("BOT_TOKEN"))