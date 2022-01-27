import os
from datetime import datetime

from nextcord import Intents
from cmyui.version import Version
from cmyui.logging import Ansi, log
from nextcord.ext.commands import Bot

import util
import config

"""
bot - our discord bot.
bot.start_time - our initial start time of Moé.
"""
bot = Bot(command_prefix=[], intents=Intents.all()) # NOTE: no bot prefix - we use slash commands
bot.start_time = datetime.utcnow()



"""
bot.version - current version of Moé.
NOTE:
    - major: breaking changes
    - minor: command changes/new features
    - patch: typo fixes/bug fixes
"""
bot.version = Version(2, 4, 4)



"""
cogs - load all external cogs for Moé.
"""
log("--- Start Cogs ---", Ansi.MAGENTA)
for c in os.listdir("./cogs"):
    filename, ext = os.path.splitext(c)
    try:
        if filename != "__pycache__":
            bot.load_extension(f"cogs.{filename}")
            log(f"Loaded cog: cog.{filename}!", Ansi.LGREEN)
    except Exception as ex:
        log(f"Failed to load cog: cog.{filename}!", Ansi.LRED)
        if config.debug:
            log(f"{ex}", Ansi.LRED)
        continue
log("--- End Cogs ---\n", Ansi.MAGENTA)



"""
on_member_join() - tasks ran as soon as a player joins a guild.
"""
@bot.listen()
async def on_member_join(member) -> None:
    # update bot presence
    await util.update_presence(bot)



"""
on_member_leave() - tasks ran as soon as a player leaves a guild.
"""
@bot.listen()
async def on_member_leave(member) -> None:
    # update bot presence
    await util.update_presence(bot)



"""
on_guild_join() - tasks ran when the bot joins a guild.
"""
@bot.listen()
async def on_guild_join(guild) -> None:
    # update bot presence
    await util.update_presence(bot)



"""
on_guild_remove() - tasks ran when the bot is removed from a guild.
"""
@bot.listen()
async def on_guild_remove(guild) -> None:
    # update bot presence
    await util.update_presence(bot)



"""
on_message() - tasks ran when a message is sent.
"""
@bot.event
async def on_message(message) -> None:
    # ignore bot
    if message.author == bot.user:
        return
    # ignore everyone mentions
    if message.mention_everyone:
        return

    # basic message logging to console
    if not "<@!" in message.content:
        log(f"[{message.guild.name} (#{message.channel.name})] {str(message.author)}: {message.content}", Ansi.LYELLOW)

    # basic ping response
    if bot.user.mentioned_in(message):
        await message.channel.send(f"Hi, **{message.author.name}**, my name is **Moé**!\nMy command prefix is **/**. Try typing it in chat to view my full commandset!")



"""
on_ready() - tasks ran as soon as Moé is ready.
"""
@bot.listen()
async def on_ready() -> None:
    log("--- Start Tasks ---", Ansi.MAGENTA)
    # connect to mysql
    await util.mysql_connect(bot, config.mysql)
    # create the client session
    await util.create_client_session(bot)
    # authorize with the osu!api
    await util.auth_osu_api(bot)
    # update presence
    await util.update_presence(bot)
    log("--- End Tasks ---\n", Ansi.MAGENTA)

    # Active guilds
    await util.get_active_guilds(bot)

    # Moé ready
    log(f"Moé has been logged in as {bot.user}.", Ansi.LBLUE)
    log(f"Running version {bot.version}!\n", Ansi.LBLUE)



"""
run - run Moé.
"""
if __name__ == "__main__":
    bot.run(config.token) # blocking call
