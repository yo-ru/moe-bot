import aiohttp
import nextcord
from datetime import datetime
from nextcord.ext.commands import Cog
from nextcord.ext import application_checks
from nextcord import Embed, Interaction, SlashOption

from cmyui import log, Ansi

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
            await session.close()
            if resp.status == 404:
                return await ctx.send("⛔ Invalid Order ID!\nPlease double check and try again.", ephemeral=True)
            elif resp.status == 200:
                json = await resp.json()
                if json["data"]["status"]["status"]["status"] == "COMPLETED":
                    await ctx.user.add_roles(role)
                    return await ctx.send("🎉 Thank you for your support! Your customer role has been applied!\nMake sure to leave a `+rep` in <#1008042020549427261>!", ephemeral=True)
                else:
                    return await ctx.send("⛔ Oh no! This is a valid Order ID, but it hasn't been marked as completed!\nNice try.", ephemeral=True)
            return await ctx.send("⛔ An unknown error occured!\nContact my developer!", ephemeral=True)



    """
    order - lookup an order by id.
    NOTE: Exclusively for https://skittle.shop.
    """
    @nextcord.slash_command(
        name="order",
        description="Lookup an order by ID.",
        guild_ids=[1008042019828011120]  # Skittle Shop Discord
    )
    @application_checks.has_permissions(administrator=True)
    async def _order(
        self, 
        ctx: Interaction,
        orderId: str = SlashOption(
            name="orderid",
            description="Enter an Order ID.",
            required=True,
        )
    ):
        product_title: str = ""
        product_urls: str = ""
        session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {config.sellapp_token}"})
        async with session.get(f"https://sell.app/api/v1/invoices/{orderId}", allow_redirects=False) as resp:
            await session.close()
            if resp.status == 404:
                return await ctx.send("⛔ Invalid Order ID!\nPlease double check and try again.", ephemeral=True)
            elif resp.status == 200:
                json = await resp.json()
                payment = json["data"]["payment"]
                customer_info = json["data"]["customer_information"]
                status = json["data"]["status"]
                products = json["data"]["products"]

                for product in products:
                    product_title += f"{product['title']} "
                    product_urls += f"[Click Here]({product['url']})"

                embed=Embed(
                    title=product_title, 
                    color=0xff94ed
                )
                base_price = payment['gateway']['data']['total']['base']
                embed.add_field(name="Payment Status", value=status["status"]["status"], inline=True)
                embed.add_field(name="Payment Amount", value=f"${base_price[:-2]}.{base_price[-2:]} USD", inline=True)
                embed.add_field(name="Payment Date", value=datetime.strptime(status["status"]["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S - %B %d, %Y"), inline=True)
                embed.add_field(name="Order Email", value=customer_info["email"], inline=True)
                embed.add_field(name="Order IP", value=customer_info["ip"], inline=True)
                embed.add_field(name="Product URL", value=product_urls, inline=True)
                embed.set_footer(text=f"running Moé v{self.bot.version}", icon_url="https://bot.its.moe/assets/favicon/favicon-16x16.png")
                return await ctx.send(embed=embed)
            return await ctx.send("⛔ An unknown error occured!\nContact my developer!", ephemeral=True)



    """
    stock - lookup an current stock amount.
    NOTE: Exclusively for https://skittle.shop.
    """
    @nextcord.slash_command(
        name="stock",
        description="Look up current stock amount.",
        guild_ids=[1008042019828011120]  # Skittle Shop Discord
    )
    async def _stock(
        self, 
        ctx: Interaction
    ):
        session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {config.sellapp_token}"})
        async with session.get(f"https://sell.app/api/v1/listings", allow_redirects=False) as resp:
            await session.close()
            json = await resp.json()
            products = json["data"]

            embed=Embed(
                title="Current Stock", 
                color=0xff94ed
            )

            for product in products:
                if (stock := product["deliverable"]["data"]["stock"]) is None: stock = "N/A"
                embed.add_field(name=product["title"], value=stock, inline=True)

            embed.set_footer(text=f"running Moé v{self.bot.version}", icon_url="https://bot.its.moe/assets/favicon/favicon-16x16.png")
            return await ctx.send(embed=embed)



def setup(bot) -> None:
    bot.add_cog(Skittle(bot))