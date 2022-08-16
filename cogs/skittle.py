import aiohttp
import nextcord
from datetime import datetime
from nextcord.activity import Game
from cmyui.logging import Ansi, log
from nextcord.ext.commands import Cog
from nextcord import Embed, Interaction, SlashOption

import config

class Skittle(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot



    """
    customer - apply the customer role after successful purchase.
    NOTE: Exclusively for https://skittle.shop.
    """
    @nextcord.slash_command(
        name="customer",
        guild_ids=[1008042019828011120]  # Skittle Shop Discord
    )
    async def _customer(
        self, 
        ctx: Interaction,
        orderId: str = SlashOption(
            name="orderid",
            description="Enter the Order ID received after purchase.",
            required=True
        )
    ):
        role = nextcord.utils.get(ctx.guild.roles, name="Customer")
        if ctx.user.get_role(role.id):
            return await ctx.send("You already have the customer role!", ephemeral=True)

        session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {config.sellapp_token}"})
        url = f"https://sell.app/api/v1/invoices/{orderId}"
        async with session.get(url, allow_redirects=False) as resp:
            log(orderId)
            log(resp.request_info.headers)
            if resp.status == 404:
                return await ctx.send("Invalid Order ID!\nPlease double check and try again.", ephemeral=True)
            elif resp.status == 200:
                await ctx.user.add_roles(role, f"Customer role applied automiatcally via Order ID: {orderId}")
                return await ctx.send("🎉 Thank you for your support! Your customer role has been applied!\nMake sure to leave a `+rep` in <#1008042020549427261>!", ephemeral=True)
            await session.close()
            return await ctx.send("An unknown error occured! Contact my developer!", ephemeral=True)

def setup(bot) -> None:
    bot.add_cog(Skittle(bot))