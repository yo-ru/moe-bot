from discord import ui
import discord
import os
import re
import aiohttp

import settings


class Register(ui.Modal, title="Register Subomain"):
    subdomain = ui.TextInput(
        label="Subdomain", placeholder="yoru", style=discord.TextStyle.short)
    record = ui.TextInput(label="DNS Record Type",
                          placeholder="CNAME/A", style=discord.TextStyle.short)
    value = ui.TextInput(label="DNS Record Value",
                         placeholder="yo-ru.github.io/X.X.X.X", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        # ignore invalid subdomain values
        if not bool(re.match("^[A-Za-z0-9-]*$", self.subdomain.value)):
            await interaction.response.send_message(f"Invalid subdomain: `{self.subdomain.value}`.\nCorrect Examples: `yoru`, `yo-ru`, `xn--ess`, `y0ru`, `y0-ru`.", ephemeral=True)
            return

        # ignore invalid record types
        if not any(s in self.record.value.upper() for s in ["CNAME", "A"]):
            await interaction.response.send_message(f"Invalid record type: `{self.record.value.upper()}`.\nPossible values: `A`, `CNAME`", ephemeral=True)
            return

        # ignore invalid ip addresses for A records
        if self.record.value.upper() == "A" \
                and not bool(re.match("^(?!^0\.)(?!^10\.)(?!^100\.6[4-9]\.)(?!^100\.[7-9]\d\.)(?!^100\.1[0-1]\d\.)(?!^100\.12[0-7]\.)(?!^127\.)(?!^169\.254\.)(?!^172\.1[6-9]\.)(?!^172\.2[0-9]\.)(?!^172\.3[0-1]\.)(?!^192\.0\.0\.)(?!^192\.0\.2\.)(?!^192\.88\.99\.)(?!^192\.168\.)(?!^198\.1[8-9]\.)(?!^198\.51\.100\.)(?!^203.0\.113\.)(?!^22[4-9]\.)(?!^23[0-9]\.)(?!^24[0-9]\.)(?!^25[0-5]\.)(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$", self.value.value)):
            await interaction.response.send_message(f"It looks like you are trying to setup a its.moe subdomain with an **A** record.\nInvalid record value: `{self.value.value}`.\nPlease enter a valid IPv4 address to point to.", ephemeral=True)
            return

        # ignore invalid domain names for CNAME records
        elif self.record.value.upper() == "CNAME" \
                and not bool(re.match("^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$", self.value.value)) \
                and ".github.io" in self.value.value:
            await interaction.response.send_message(f"It looks like you are trying to setup a its.moe subdomain with a **CNAME** record.\nInvalid record value: `{self.value.value}`.\nPlease enter a valid github pages domain to point to (ex. `yoru.github.io`.)", ephemeral=True)
            return

        # begin database connection
        async with interaction.client.database as db:
            # handle gold members
            if interaction.user.get_role(1008042019828011125):  # 👑 Gold
                query = f"""
                    SELECT COUNT(*)
                      FROM domains
                    WHERE discord_id = :discord_id
                """
                params = {"discord_id": interaction.user.id}
                if (await db.fetch_one(query, params))[0] >= 5:
                    await interaction.response.send_message(f"<@&1008042019828011125> members are limited to 5 its.moe subdomains.\nIf you believe you need more, contact <@207253376084344832>.", ephemeral=True)
                    return
            # handle regular members
            else:
                query = f"""
                    SELECT 1
                      FROM domains
                    WHERE discord_id = :discord_id
                """
                params = {"discord_id": interaction.user.id}

                if (await db.fetch_one(query, params)):
                    await interaction.response.send_message(f"Non-<@&1008042019828011125> members are limited to 1 free its.moe subdomain.\n<@&1008042019828011125> members have access up to 5 free its.moe subdomains.\nYou can purchase a <@&1008042019828011125> membership on our Ko-Fi!\nhttps://ko-fi.com/itsmoe", ephemeral=True)
                    return

            # begin http session
            async with aiohttp.ClientSession() as session:
                # check if subdomain is available (cf)
                async with session.request(
                    "GET",
                    f"https://api.cloudflare.com/client/v4/zones/{settings.CF_ZONE_ID}/dns_records",
                    headers={
                        "Authorization": f"Bearer {settings.CF_API_KEY}"},
                    params={"name": f"{self.subdomain.value}.its.moe"}
                ) as resp:
                    cf_unavail = (await resp.json())["result"]
                await session.close()

            # check if subdomain is available (db)
            query = f"""
                SELECT 1
                FROM domains
                WHERE subdomain = :subdomain
            """
            params = {"subdomain": self.subdomain.value}
            db_unavail = await db.fetch_one(query, params)

            if cf_unavail or db_unavail:
                await interaction.response.send_message(f"The subdomain, `{self.subdomain.value}`, is already in use!", ephemeral=True)
                return

            # insert record into database & update cf
            else:
                # begin http connection
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        "POST",
                        f"https://api.cloudflare.com/client/v4/zones/{settings.CF_ZONE_ID}/dns_records",
                        headers={
                            "Authorization": f"Bearer {settings.CF_API_KEY}"
                        },
                        json={
                            "type": self.record.value,
                            "name": f"{self.subdomain.value}.its.moe",
                            "content": self.value.value,
                            "ttl": 1,
                            "proxied": True,
                            "comment": f"{interaction.user.id} - its.moe subdomain request"
                        }
                    ) as resp:
                        cf_id = (await resp.json())["result"]["id"]
                    await session.close()

                query = f"""
                    INSERT INTO domains
                    (discord_id, record_type, record_value, subdomain, cloudflare_id)
                    VALUES (:discord_id, :record_type, :record_value, :subdomain, :cloudflare_id)
                """
                params = {
                    "discord_id": interaction.user.id,
                    "record_type": self.record.value.upper(),
                    "record_value": self.value.value,
                    "subdomain": self.subdomain.value,
                    "cloudflare_id": cf_id
                }
                id = await db.execute(query, params)
        await interaction.response.send_message(f"its.moe subdomain created!\n```Moé ID: {id}\nCloudflare ID: {cf_id}\nSubdomain: {self.subdomain.value}\nRecord Type: {self.record.value}\nRecord Value: {self.value.value}```\nYou can visit it at <https://{self.subdomain.value}.its.moe>.", ephemeral=True)
        return
