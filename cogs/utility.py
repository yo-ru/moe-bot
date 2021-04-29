from datetime import datetime
from discord.ext import commands
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

import config

class Utility(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    """
    ping - get an accurate representation of latency between Sekai and Discord!
    """
    @cog_ext.cog_slash(
        name="ping",
        description="Get an accurate representation of latency between Sekai and Discord!"
    )
    async def _ping(self, ctx: SlashContext) -> SlashContext:
        await ctx.respond()
        return await ctx.send(f"Pong! (**{self.bot.latency*1000:.2f}**ms)")

    

    """
    uptime - get Sekai's current total operation time.
    """
    @cog_ext.cog_slash(
        name="uptime",
        description="Get Sekai's current total operation time!"
    )
    async def _uptime(self, ctx: SlashContext) -> SlashContext:
        await ctx.respond()
        delta = datetime.utcnow() - self.bot.start_time
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        return await ctx.send(f"Hey! I've been up for around **{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds.")



    """
    version - get Sekai's current development version.
    """
    @cog_ext.cog_slash(
        name="version",
        description="Get Sekai's current development version!"
    )
    async def _version(self, ctx: SlashContext) -> SlashContext:
        await ctx.respond()
        return await ctx.send(f"I'm currently running version **{self.bot.version}**!\nCheck my GitHub page to see if my firmware is out of date!")

    

    """
    shutdown - restart Sekai.
    """
    @cog_ext.cog_slash(
        name="shutdown",
        description="Shutdown my mainframe. (Requires ownership)"
    )
    @commands.is_owner()
    async def _shutdown(self, ctx: SlashContext) -> SlashContext:
        await ctx.respond()
        await ctx.send("Power failure, shutting down...")
        # close all connections and logout
        await self.bot.db.close()
        await self.bot.request.close()
        await self.bot.logout()
    
def setup(bot) -> None:
    bot.add_cog(Utility(bot))