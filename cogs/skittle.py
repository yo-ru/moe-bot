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

        session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {config.sellapp_token}", 
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                     "Accept": "*/*",
                     "Sec-Fetch-Site": "none",
                     "Sec-Fetch-Mode": "cors",
                     "Sec-Fetch-Dest": "empty",
                     "Accept-Encoding": "gzip, deflate, br",
                     "Accept-Language": "en-US,en;q=0.9",
                     "Cookie": "intercom-id-p2t4ex6z=d66274d9-1cea-42bc-9182-58c0bcd1c68d; intercom-session-p2t4ex6z=; crisp-client%2Fsession%2F29be3e5d-af36-448b-8852-21515be5bbee=session_844c5e4e-c042-42c7-ab41-0226051b0dc5; cf_clearance=6sSzOgEU3jnWiKUeCpJ6DfRhLr_MbOtp6tl.0vAqrDM-1660551480-0-150; XSRF-TOKEN=eyJpdiI6IkJXbm5QQTJyeVI0aW4rdzJpS0RpOXc9PSIsInZhbHVlIjoiRG5XbUt5OUlBZVNCNjZGL2x3QTI2cW5uQis1WjduSXlpaHVQUk5ReC9XU0hjRFFjZ2Y3VGlXajlUeGgxSEJlbWZ3YzJJSTY3UjYxM3F6VGR1SmlrOURFU0tjVzY0RFFCb0k0YUhRbHcvQ04wR0FIbVhhQ0dwV1R1eHhaaGMyNnUiLCJtYWMiOiJjZjA3MzhhMmNkNzBiZmNjYjE3ODUxYzdlMjcwZGUzNWY5MjFjYTU1MDA0OGY0ODBhY2ZjNDlkM2FkMWJkODM3IiwidGFnIjoiIn0%3D; sellapp_session=eyJpdiI6IjlrQWx1akpTdTY5TDlKQ0U1S29PcVE9PSIsInZhbHVlIjoiSDYwTmwvUEpueWJVTWNHVHVaQmJNaG9KOG05MEpZRnBzNnhOdGR5dzJJbGgxWkdkUjhWTnJSNEhvYWdZY0FBVkZZenlaN1doMFdoMnhMa1NkTG4rK1dpVC9SSXgxZmVadDBYVjNnbFovQmRJR3Q0QXlZajMzYTRjQ3FLV2dnU3oiLCJtYWMiOiIzNDEzYzZkY2U3YzcwZWQ3MzVkMDJiZDY2ZmZmNDM1MDRkOWE4MzlmZDMwZGFkZTUwZGQ1MmY2YjExZTE4MDFlIiwidGFnIjoiIn0%3D"
                    }
        )
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