import aiohttp

async def get_mojang_profile(mc_username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{mc_username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return None
