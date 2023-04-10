import logging
from discord.ext import commands
import discord
from rich.console import Console
import os
import asyncio
import databases

from typing import Literal, Optional

import dotenv
dotenv.load_dotenv()


logging.basicConfig(level=logging.DEBUG)
discord.utils.setup_logging()


class Moe(commands.Bot):
    async def setup_hook(self):
        moe.console.print("Moe is ready!", style="bold pink1")


moe = Moe(command_prefix="!", intents=discord.Intents.all(), help_command=None)
moe.console = Console()
moe.database = databases.Database(os.environ["DB_DSN"])


@moe.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    # Works like:
    # !sync -> global sync
    # !sync ~ -> sync current guild
    # !sync * -> copies all global app commands to current guild and syncs
    # !sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
    # !sync id_1 id_2 -> syncs guilds with id 1 and 2
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

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
                moe.console.print(f"Loaded cog.{f}!", style="bold green")
        except Exception as ex:
            moe.console.print(
                f"Failed to load cog.{f}!\n{ex}", style="bold red")


async def main():
    async with moe:
        await load_cogs()
        await moe.start(token=os.environ["TOKEN"])

asyncio.run(main())
