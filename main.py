import os
import asyncio
import logging
from typing import Literal, Optional

import discord
import databases
from discord.ext import commands
from rich.logging import RichHandler

import settings

moe = commands.Bot(command_prefix="!",
                   intents=discord.Intents.all(), help_command=None)
moe.database = databases.Database(settings.DB_DSN)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG_MODE else logging.INFO,
    format="%(message)s",
    datefmt="[%m/%d/%Y | %H:%M:%S]",
    handlers=[RichHandler(omit_repeated_times=False)]
)
moe.log = logging.getLogger("rich")


@moe.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        # !sync ~ -> sync current guild
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
         # !sync * -> copies all global app commands to current guild and syncs
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        # !sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        # !sync -> global sync
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return
    # !sync id_1 id_2 -> syncs guilds with id 1 and 2
    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def load_cogs():
    for c in os.listdir("./cogs"):
        f, e = os.path.splitext(c)
        try:
            if f != "__pycache__":
                await moe.load_extension(f"cogs.{f}")
                moe.log.info(f"Loaded cog.{f}!")
        except Exception as ex:
            moe.log.warn(
                f"Failed to load cog.{f}!\n{ex}")


async def main():
    async with moe:
        await load_cogs()
        await moe.start(token=settings.DISCORD_TOKEN)

asyncio.run(main())
