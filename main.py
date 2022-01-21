import os
import orjson
import aiohttp
from datetime import datetime

from ossapi import OssapiV2
from cmyui.version import Version
from cmyui.logging import Ansi, log
from cmyui.mysql import AsyncSQLPool
from nextcord.ext.commands import Bot
from nextcord import Activity, ActivityType, Intents



import config

"""
bot - our discord bot.
bot.start_time - our initial start time of Moé.
"""
bot = Bot(command_prefix="", intents=Intents.all()) # NOTE: no bot prefix - we use slash commands
bot.start_time = datetime.utcnow()



"""
bot.version - current version of Moé.
NOTE:
    - major: breaking changes
    - minor: command changes/new features
    - patch: typo fixes/bug fixes
"""
bot.version = Version(2, 1, 4)



"""
cogs - load all external cogs for Moé.
"""
log("--- Start Cogs ---", Ansi.MAGENTA)
for c in os.listdir("./cogs"):
    filename, ext = os.path.splitext(c)
    try:
        if filename != "__pycache__":
            bot.load_extension(f"cogs.{filename}")
            if config.debug:
                log(f"Loaded cog: cog.{filename}!", Ansi.LGREEN)
    except Exception as ex:
        log(f"Failed to load cog: cog.{filename}!", Ansi.LRED)
        if config.debug:
            log(f"{ex}", Ansi.LRED)
        continue
log("--- End Cogs ---\n", Ansi.MAGENTA)



"""
on_ready() - tasks ran as soon as Moé is ready.
"""
@bot.event
async def on_ready() -> None:
    log("--- Start Tasks ---", Ansi.MAGENTA)
    # connect to mysql
    try:
        bot.db = AsyncSQLPool()
        await bot.db.connect(config.mysql)
        if config.debug:
            log("Connected to MySQL!", Ansi.LGREEN)
    except:
        log("Failed to connect to MySQL!", Ansi.LRED)
        log("--- End Tasks ---\n", Ansi.MAGENTA)
        exit(1) # NOTE: Moé loses a lot of functionality without mysql; stop execution

    # create the client session
    try:
        bot.request = aiohttp.ClientSession(json_serialize=orjson.dumps)
        if config.debug:
            log("Created the Client Session!", Ansi.LGREEN)
    except:
        log("Failed to get the Client Session!", Ansi.LRED)
        log("--- End Tasks ---\n", Ansi.MAGENTA)
        bot.db.close() # safely close db connection
        exit(1) # NOTE: Moé loses a lot of functionality without the client session; stop execution

    # authorize with the osu!api
    try:
        bot.osu = OssapiV2(client_id=config.osu.get("id"), client_secret=config.osu.get("secret"))
        if config.debug:
            log("Authorized with the osu!api!", Ansi.LGREEN)
    except:
        bot.unload_extension("cogs.osu")
        log("Failed to authorize with the osu!api! (Unloaded osu.cog!)", Ansi.LRED)

    # set presence
    try:
        if config.debug:
            log("Presence set!", Ansi.LGREEN)
        await bot.change_presence(
            activity=Activity(
                type=ActivityType.playing, 
                name=f"with {f'{len(bot.users):,} users' if len(bot.users) > 1 else 'a user'} in {f'{len(bot.guilds):,} guilds' if len(bot.guilds) > 1 else 'a guild'}."
            )
        )
    except:
        log("Failed to set Presence!", Ansi.LRED)
    log("--- End Tasks ---\n", Ansi.MAGENTA)

    # Moé ready
    log(f"Moé has been logged in as {bot.user}.", Ansi.LBLUE)
    if config.debug:
        log(f"Running version {bot.version}!", Ansi.LBLUE)



"""
on_message() - tasks ran when a message is sent.
"""
@bot.event
async def on_message(message) -> None:
    # ignore bot
    if message.author == bot.user:
        return
    if message.mention_everyone:
        return

    # basic message logging to console
    if not "<@!" in message.content:
        log(f"[{message.guild.name} (#{message.channel.name})] {str(message.author)}: {message.content}", Ansi.LYELLOW)

    # basic ping response
    if bot.user.mentioned_in(message):
        await message.channel.send(f"Hi, **{message.author.name}**, my name is **Moé**!\nMy command prefix is **/**. Try typing it in chat to view my full commandset!")



"""
run - run Moé.
"""
if __name__ == "__main__":
    bot.run(config.token) # blocking call
