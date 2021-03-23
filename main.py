import os
import orjson
import aiohttp
from datetime import datetime
from discord.ext.commands import Bot
from discord_slash import SlashCommand
from discord import Client, Activity, ActivityType
from cmyui import AsyncSQLPool, Version, Ansi, log
from discord.ext.commands.errors import CommandNotFound

import config

"""
bot - our discord bot.
bot.start_time - our initial start time of Sekai.
slash - integrated support for slash commands.
"""
bot = Bot(command_prefix="") # NOTE: no bot prefix - we use slash commands
bot.start_time = datetime.utcnow()
slash = SlashCommand(bot, sync_commands=True, override_type=True)



"""
bot.version - current version of Sekai.
"""
bot.version = Version(0, 1, 0)



"""
cogs - load all external cogs for Sekai.
"""
for c in os.listdir("./cogs"):
    filename, ext = os.path.splitext(c)
    try:
        if filename != "__pycache__":
            bot.load_extension(f"cogs.{filename}")
            if config.debug:
                log(f"Successfully loaded cog: cog.{filename}!", Ansi.LGREEN)
    except:
        log(f"Failed to load cog: cog.{filename}!", Ansi.LRED)
        continue



"""
on_ready() - tasks ran as soon as Sekai is ready.
"""
@bot.event
async def on_ready() -> None:
    # connect to mysql
    bot.db = AsyncSQLPool()
    await bot.db.connect(config.mysql)
    if config.debug:
        log(f"Connected to MySQL!", Ansi.LGREEN)

    # get client session
    bot.request = aiohttp.ClientSession(json_serialize=orjson.dumps)
    if config.debug:
        log(f"Got Client Session!", Ansi.LGREEN)

    # set status
    await bot.change_presence(activity=Activity(type=ActivityType.watching, name="\"Hello World\" on Netflix!"))
    
    # Sekai ready
    log(f"Sekai has been logged in as {bot.user}.", Ansi.LBLUE)
    if config.debug:
        log(f"Running version {bot.version}!", Ansi.LBLUE)



"""
run - run Sekai.
"""
if __name__ == "__main__":
    bot.run(config.token) # blocking call
