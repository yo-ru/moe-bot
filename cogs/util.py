import nextcord
from datetime import datetime
from nextcord.activity import Game
from cmyui.logging import Ansi, log
from nextcord.ext.commands import Cog
from nextcord import Embed, Interaction, SlashOption

import config

class Util(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot



    """
    util - the base util command.
    """
    @nextcord.slash_command(
        name="util"
    )
    async def _util(
        self, 
        ctx: Interaction
    ):
        ...

    

    """
    ping - get an accurate representation of latency between Moé and Discord!
    """
    @_util.subcommand(
        name="ping",
        description="Get an accurate representation of latency between Moé and Discord!"
    )
    async def _ping(
        self, 
        ctx: Interaction
    ):
        return await ctx.send(f"Pong **({self.bot.latency*1000:.2f}ms)**", ephemeral=True)

    

    """
    uptime - get Moé's current total operation time.
    """
    @_util.subcommand(
        name="uptime",
        description="Get Moé's current total operation time!"
    )
    async def _uptime(
        self, 
        ctx: Interaction
    ):
        delta = datetime.utcnow() - self.bot.start_time
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        return await ctx.send(f"Hey! I've been up for around **{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds.")



    """
    version - get Moé's current development version.
    """
    @_util.subcommand(
        name="version",
        description="Get Moé's current development version!"
    )
    async def _version(
        self, 
        ctx: Interaction
    ):
        return await ctx.send(f"I'm currently running version **{self.bot.version}**!\nCheck my GitHub page to see if my firmware is out of date!")

def setup(bot) -> None:
    bot.add_cog(Util(bot))
