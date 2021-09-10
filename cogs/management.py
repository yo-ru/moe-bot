import discord
from discord.ext import commands
from cmyui.logging import Ansi, log
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option


class Management(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    
    """
    ban - ban a member in current guild
    """
    @cog_ext.cog_slash(
        name="ban",
        description="Ban a member from the current guild.",
        options=[
            create_option(
                name="member",
                description="The mention of the member you are banning.",
                option_type=6,
                required=True
            ),
            create_option(
                name="reason",
                description="The reason for banning.",
                option_type=3,
                required=False
            )
        ]
    )
    @commands.has_guild_permissions(ban_members=True)
    async def _ban(self, ctx: SlashContext, member: discord.Member, reason="no reason specified") -> SlashContext:
        # ban member
        try:
            await ctx.guild.ban(user=member, reason=f"By {ctx.author} for {reason}.")
            await ctx.send(f"{member.mention} was banned for {reason}.")
        except discord.Forbidden:
            return await ctx.send("Are you trying to ban someone with higher privileges than me?")

    

    """
    kick - kick a member in current guild
    """
    @cog_ext.cog_slash(
        name="kick",
        description="Kick a member from the current guild.",
        options=[
            create_option(
                name="member",
                description="The mention of the member you are kicking.",
                option_type=6,
                required=True
            ),
            create_option(
                name="reason",
                description="The reason for kicking.",
                option_type=3,
                required=False
            )
        ]
    )
    @commands.has_guild_permissions(kick_members=True)
    async def _kick(self, ctx, member: discord.Member, reason="no reason specified"):
        # kick member
        try:
            await ctx.guild.kick(user=member, reason=f"By {ctx.author} for {reason}.") 
        except discord.Forbidden:
            return await ctx.send("Are you trying to kick someone with higher privileges than me?")
    


    """
    shutdown - shutdown Moé.
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
    bot.add_cog(Management(bot))