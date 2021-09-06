import os
import orjson
import aiohttp
from datetime import datetime

from discord.ext.commands import Bot
from discord_slash import SlashCommand
from discord import Activity, ActivityType, Intents
from ossapi import OssapiV2
from cmyui import AsyncSQLPool, Version, Ansi, log

import config

"""
bot - our discord bot.
bot.start_time - our initial start time of Moe.
slash - integrated support for slash commands.
"""
bot = Bot(command_prefix="", intents=Intents.all()) # NOTE: no bot prefix - we use slash commands
bot.start_time = datetime.utcnow()
slash = SlashCommand(bot, sync_commands=True, override_type=True)



"""
bot.version - current version of Moe.
"""
bot.version = Version(0, 1, 0)



"""
cogs - load all external cogs for Moe.
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
on_ready() - tasks ran as soon as Moe is ready.
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

    # authorize with the osu!api
    bot.osu = OssapiV2(client_id=config.osu.get("id"), client_secret=config.osu.get("secret"))
    if config.debug:
        log(f"Authorized with the osu!api!", Ansi.LGREEN)

    # set status
    await bot.change_presence(activity=Activity(type=ActivityType.playing, name=f"with {f'{len(bot.users):,} users' if len(bot.users) > 1 else 'a user'} in {f'{len(bot.guilds):,} guilds' if len(bot.guilds) > 1 else 'a guild'}."))
    
    # Moe ready
    log(f"Moe has been logged in as {bot.user}.", Ansi.LBLUE)
    if config.debug:
        log(f"Running version {bot.version}!", Ansi.LBLUE)



"""
on_message() - tasks ran when a message is sent.
"""
@bot.event
async def on_message(message) -> None:
    # basic message logging to console
    # NOTE: ignore bot and mentions
    if message.author != bot.user and not "<@!" in message.content:
        log(f"[{message.guild.name} (#{message.channel.name})] {str(message.author)}: {message.content}", Ansi.LYELLOW)

    # basic ping response
    if bot.user.mentioned_in(message):
        await message.channel.send(f"Hi, **{message.author.name}**, my name is **Moe**!\nMy command prefix is **/**. Try typing it in chat to view my full commandset!")



"""
run - run Moe.
"""
if __name__ == "__main__":
    bot.run(config.token) # blocking call
