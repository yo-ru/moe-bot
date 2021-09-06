from datetime import datetime
from discord.ext import commands
from cmyui.logging import Ansi, log
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

import config

class Utility(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    """
    ping - get an accurate representation of latency between Moe and Discord!
    """
    @cog_ext.cog_slash(
        name="ping",
        description="Get an accurate representation of latency between Moe and Discord!"
    )
    async def _ping(self, ctx: SlashContext) -> SlashContext:
        return await ctx.send(f"Pong! (**{self.bot.latency*1000:.2f}**ms)")

    

    """
    uptime - get Moe's current total operation time.
    """
    @cog_ext.cog_slash(
        name="uptime",
        description="Get Moe's current total operation time!"
    )
    async def _uptime(self, ctx: SlashContext) -> SlashContext:
        delta = datetime.utcnow() - self.bot.start_time
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        return await ctx.send(f"Hey! I've been up for around **{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds.")



    """
    version - get Moe's current development version.
    """
    @cog_ext.cog_slash(
        name="version",
        description="Get Moe's current development version!"
    )
    async def _version(self, ctx: SlashContext) -> SlashContext:
        return await ctx.send(f"I'm currently running version **{self.bot.version}**!\nCheck my GitHub page to see if my firmware is out of date!")

    

    """
    shutdown - restart Moe.
    """
    @cog_ext.cog_slash(
        name="shutdown",
        description="Shutdown my mainframe. (Requires ownership)"
    )
    @commands.is_owner()
    async def _shutdown(self, ctx: SlashContext) -> SlashContext:
        await ctx.send("Power failure, shutting down...")
        log("\nShutting down...", Ansi.LRED)
        # close all connections and logout
        await self.bot.db.close()
        await self.bot.request.close()
        await self.bot.close()
    
def setup(bot) -> None:
    bot.add_cog(Utility(bot))