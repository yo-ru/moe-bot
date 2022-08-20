import os
import orjson
import aiohttp
import pymysql
import databases

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
async def mysql_connect(bot, cred: str) -> None:
    try:
        bot.db = databases.Database(cred)
        await bot.db.connect()
    except pymysql.err.OperationalError:
        log("Failed to connect to MySQL!", Ansi.LRED)
        os._exit(1) # NOTE: Moé loses a lot of functionality without mysql; stop execution
    finally:
        log("Connected to MySQL!", Ansi.LGREEN)



"""
create_client_session() - create the client session.
"""
async def create_client_session(bot) -> None:
    try:
        bot.request = aiohttp.ClientSession(json_serialize=orjson.dumps)
    except:
        log("Failed to get the Client Session!", Ansi.LRED)
        bot.db.close() # safely close db connection
        os._exit # NOTE: Moé loses a lot of functionality without the client session; stop execution
    finally:
        log("Client Session created!", Ansi.LGREEN)



"""
auth_osu_api() - authorize with the osu! api.
"""
async def auth_osu_api(bot) -> None:
    try:
        bot.osu = OssapiV2(client_id=config.osu.get("id"), client_secret=config.osu.get("secret"))
    except:
        bot.unload_extension("cogs.osu")
        log("Failed to authorize with the osu!api! (Unloaded cogs.osu!)", Ansi.LRED)
    finally:
        log("Authorized with the osu!api!", Ansi.LGREEN)



"""
# get_active_guilds() - return active guilds the bot is in.
"""
async def get_active_guilds(bot) -> None:
    log("--- Start Active Guilds ---", Ansi.MAGENTA)
    log("# | Guild Name | Guild ID | Member Count | Guild Invite", Ansi.LYELLOW)
    for i, g in enumerate(bot.guilds):
        async with bot.db.connection() as db:
            if not (inv := await db.fetch_one("SELECT inv FROM guildinvites WHERE guildid = :id", {"id": g.id})):
                try:
                    await bot.db.execute(
                        "INSERT INTO guildinvites "
                        "(guildid, inv) "
                        "VALUES (%s, %s) ",
                        [g.id, (await g.system_channel.create_invite()).code]
                    )
                except:
                    # TODO: probably an easier way to do this
                    ...
                
        log(f"{i+1}. {g.name} | {g.id} | {g.member_count} | {inv['inv'] if inv else None}", Ansi.LGREEN)
    log("--- End Active Guilds ---\n", Ansi.MAGENTA)