from modals.subdomain.register import Register
from discord.ext import commands
from discord import app_commands
import discord
import os
import aiohttp

import settings


class Subdomain(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="subdomain", description="Manage your its.moe subdomains!",
                               guild_only=True, guild_ids=[1008042019828011120])

    @group.command(name="register", description="Register a its.moe subdomain!")
    async def register(self, interaction: discord.Interaction):
        return await interaction.response.send_modal(Register())

    @group.command(name="list", description="List your currently registered its.moe subdomains.")
    async def list(self, interaction: discord.Interaction):
        async with self.bot.database as db:
            query = """
                SELECT *
                  FROM domains
                WHERE discord_id = :discord_id
            """
            params = {"discord_id": interaction.user.id}
            domains = await db.fetch_all(query, params)

        if not domains:
            return await interaction.response.send_message("Unable to find any subdomains created by you.\nTry `/subdomain register` first.", ephemeral=True)

        message = "your its.moe subdomains:\n```ID) Subdomain | Record Type | Record Value\n"
        for domain in domains:
            message += "{id}) {subdomain} | {record_type} | {record_value}\n".format(
                **domain)
        message += "```\nWant to delete a subdomain? `/subdomain delete <ID>`"

        return await interaction.response.send_message(message, ephemeral=True)

    @group.command(name="delete", description="Delete a its.moe subdomain!")
    @app_commands.describe(id="The ID of the subdomain you wish to delete. Found at /subdomain list.")
    async def delete(self, interaction: discord.Interaction, id: int):
        async with self.bot.database as db:
            query = """
                SELECT *
                  FROM domains
                WHERE id = :id AND discord_id = :discord_id
            """
            params = {"id": id, "discord_id": interaction.user.id}
            domain = await db.fetch_one(query, params)

            if not domain:
                return await interaction.response.send_message("Unable to find a subdomain by that ID.\nCheck `/subdomain list` again.", ephemeral=True)

            async with aiohttp.ClientSession() as session:
                await session.request(
                    "DELETE",
                    f"https://api.cloudflare.com/client/v4/zones/{settings.CF_ZONE_ID}/dns_records/{domain['cloudflare_id']}",
                    headers={
                        "Authorization": f"Bearer {settings.CF_API_KEY}"
                    }
                )
                await session.close()

            query = """
                DELETE
                  FROM domains
                WHERE id = :id
            """
            params = {"id": id}
            await db.execute(query, params)

            return await interaction.response.send_message(f"its.moe subdomain:\n```Moé ID: {id}\nCloudflare ID: {domain['cloudflare_id']}\nSubdomain: {domain['subdomain']}\nRecord Type: {domain['record_type']}\nRecord Value: {domain['record_value']}```\nhas been deleted.", ephemeral=True)


async def setup(moe):
    await moe.add_cog(Subdomain(moe))
