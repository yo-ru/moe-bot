import aiohttp
import nextcord
from cmyui.logging import Ansi, log
from nextcord.ext.commands import Cog
from nextcord import Interaction, SlashOption

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
        description="Recieve the customer role!",
        guild_ids=[1008042019828011120]  # Skittle Shop Discord
    )
    async def _customer(
        self, 
        ctx: Interaction,
        orderId: str = SlashOption(
            name="orderid",
            description="Enter the Order ID received after purchase.",
            required=True,
        )
    ):
        role = nextcord.utils.get(ctx.guild.roles, name="Customer")
        if ctx.user.get_role(role.id):
            return await ctx.send("🎉 You are already a customer!\nIf you haven't already, make sure to leave a `+rep` in <#1008042020549427261>!", ephemeral=True)

        session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {config.sellapp_token}"})
        async with session.get(f"https://sell.app/api/v1/invoices/{orderId}", allow_redirects=False) as resp:
            if resp.status == 404:
                return await ctx.send("⛔ Invalid Order ID!\nPlease double check and try again.", ephemeral=True)
            elif resp.status == 200:
                json = await resp.json()
                if json["data"]["status"]["status"]["status"] == "COMPLETED":
                    await ctx.user.add_roles(role)
                    return await ctx.send("🎉 Thank you for your support! Your customer role has been applied!\nMake sure to leave a `+rep` in <#1008042020549427261>!", ephemeral=True)
                else:
                    return await ctx.send("⛔ Oh no! This is a valid Order ID, but it hasn't been marked as completed!\nNice try.", ephemeral=True)
            await session.close()
            return await ctx.send("⛔ An unknown error occured!\nContact my developer!", ephemeral=True)

def setup(bot) -> None:
    bot.add_cog(Skittle(bot))