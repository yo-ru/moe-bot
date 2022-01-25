import orjson
import aiohttp

from ossapi import OssapiV2
from cmyui.logging import Ansi, log
from cmyui.mysql import AsyncSQLPool
from nextcord import Activity, ActivityType

import config



"""
update_presence() - update bot's presence.
"""
async def update_presence(bot) -> None:
    try:
        log("Presence set!", Ansi.LGREEN)
        await bot.change_presence(
            activity=Activity(
                type=ActivityType.playing, 
                name=f"with {f'{len(bot.users):,} users' if len(bot.users) > 1 else 'a user'} in {f'{len(bot.guilds):,} guilds' if len(bot.guilds) > 1 else 'a guild'}."
            )
        )
    except:
        log("Failed to set Presence!", Ansi.LRED)
    


"""
mysql_connect() - connect to mysql.
"""
async def mysql_connect(bot, cred: dict) -> None:
    try:
        bot.db = AsyncSQLPool()
        await bot.db.connect(cred)
        if config.debug:
            log("Connected to MySQL!", Ansi.LGREEN)
    except:
        log("Failed to connect to MySQL!", Ansi.LRED)
        exit(1) # NOTE: Moé loses a lot of functionality without mysql; stop execution



"""
create_client_session() - create the client session.
"""
async def create_client_session(bot) -> None:
    try:
        bot.request = aiohttp.ClientSession(json_serialize=orjson.dumps)
        log("Client Session created!", Ansi.LGREEN)
    except:
        log("Failed to get the Client Session!", Ansi.LRED)
        bot.db.close() # safely close db connection
        exit(1) # NOTE: Moé loses a lot of functionality without the client session; stop execution



"""
auth_osu_api() - authorize with the osu! api.
"""
async def auth_osu_api(bot) -> None:
    try:
        bot.osu = OssapiV2(client_id=config.osu.get("id"), client_secret=config.osu.get("secret"))
        log("Authorized with the osu!api!", Ansi.LGREEN)
    except:
        bot.unload_extension("cogs.osu")
        log("Failed to authorize with the osu!api! (Unloaded cogs.osu!)", Ansi.LRED)