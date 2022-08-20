from multiprocessing.sharedctypes import Value
import nextcord
from ossapi.enums import GameMode
from nextcord.activity import Game
from cmyui.logging import Ansi, log
from nextcord.ext.commands import Cog
from nextcord import Embed, Interaction, SlashOption

import config

class Osu(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

        self.TO_API_CONV = {
            "osu!": GameMode.STD,
            "osu!taiko": GameMode.TAIKO,
            "osu!catch": GameMode.CTB,
            "osu!mania": GameMode.MANIA
        }

        # NOTE: for some reason the key of a dict cannot be an enum, but it's value can??
        self.FROM_API_CONV = {
            "osu": "osu!",
            "taiko": "osu!taiko",
            "fruits": "osu!catch",
            "mania": "osu!mania"
        }

        self.VALID_MODES = [
            "osu!", 
            "osu!taiko", 
            "osu!catch", 
            "osu!mania"
        ]



    """
    osu - the base osu command.
    """
    @nextcord.slash_command(
        name="osu"
    )
    async def _osu(
        self, 
        ctx: Interaction
        ):
        ...



    """
    link - link your osu! profile to discord.
    TODO: use OAuth to link users' account.
    """

    @_osu.subcommand(
        name="link",
        description="Link your osu! profile to discord!"
    )
    async def _link(
        self, 
        ctx: Interaction, 
        profile: str = SlashOption(
            name="profile",
            description="The osu! profile you are linking. This can be your username or ID.",
            required=True,  
        )
    ):
        # defer
        await ctx.response.defer(ephemeral=True)

        async with self.bot.db.connection() as db:
            if await db.fetch_one("SELECT 1 FROM osulink WHERE discordid = :id", {"id": ctx.user.id}):
                return await ctx.send("You already have an osu! profile linked!", ephemeral=True)

        # check if osu! profile exists
        try:
            user = self.bot.osu.user(profile)
        except ValueError:
                return await ctx.send("I couldn't find that osu! profile!\nMake sure you spelled their **username** or entered their **ID** correctly!", ephemeral=True)
        except:
            return await ctx.send("Failed to contact the osu!api. Please try again.", ephemeral=True)
        
        # check if someone has already linked that osu! profile
        async with self.bot.db.connection() as db:
            if await db.fetch_one("SELECT 1 FROM osulink WHERE osuid = :id", {"id": user.id}):
                return await ctx.send(f"Someone has already linked the osu! profile, **{user.username}**, to their account!", ephemeral=True)
        # store osulink
            else:
                await db.execute(
                    "INSERT INTO osulink "
                    "(discordid, osuid, favoritemode) "
                    "VALUES (:did, :oid, :mode)",
                    {"did": ctx.user.id, "oid": user.id, "mode": user.playmode}
                )
                return await ctx.send(f"Successfully linked the osu! profile, **{user.username}**, to discord!", ephemeral=True)  



    """
    unlink - unlink your osu! profile from discord.
    """
    @_osu.subcommand(
        name="unlink",
        description="Unlink osu! profile from discord!"
    )
    async def _unlink(
        self, 
        ctx: Interaction
    ):
        # defer
        await ctx.response.defer(ephemeral=True)

        async with self.bot.db.connection() as db:
            if await db.fetch_one("SELECT 1 FROM osulink WHERE discordid = :id", {"id": ctx.user.id}):
                await db.execute("DELETE FROM osulink WHERE discordid = :id", {"id": ctx.user.id})
                return await ctx.send("Successfully unlinked your osu! profile from discord!", ephemeral=True)
            else:
                return await ctx.send("You don't have an osu! profile linked to your discord!", ephemeral=True)



    """
    lookup - look up user statistics for a specified osu! profile.
    """
    @_osu.subcommand(
        name="lookup",
        description="Look up a osu! profile!"
    )
    async def _lookup(
        self, 
        ctx: Interaction, 
        profile: str = SlashOption(
            name="profile",
            description="The osu! profile you are looking up. This can be their username or ID.",
            required=False,
            default=None
        ),
        mode: str = SlashOption(
            name="mode",
            description="The osu! gamemode you want to look up. This can be osu!, osu!taiko, osu!catch, or osu!mania.",
            required=False,
            default=None
        )
    ):
        # defer
        await ctx.response.defer(ephemeral=False)

        # user has linked account
        if not profile:
            # check if member has an osu! profile linked
            async with self.bot.db.connection() as db:
                member = await db.fetch_all("SELECT * FROM osulink WHERE discordid = :id", {"id": ctx.user.id})
            if not member:
                return await ctx.send("You don't have a osu! profile linked!\nLink one with **/osu link** or specifiy a username when using **/osu lookup**!", ephemeral=True)

            # specified mode; get data
            if mode:
                if mode not in self.VALID_MODES:
                    return await ctx.send("Invalid mode selection!\nValid modes are: **osu!**, **osu!taiko**, **osu!catch**, **osu!mania**.", ephemeral=True)
                
                # TODO: handle this better
                try:
                    user = self.bot.osu.user(member.get("osuid"), self.TO_API_CONV.get(mode))
                except:
                    return await ctx.send("Failed to contact the osu!api. Please try again.", ephemeral=True)

                    
            # unspecified mode; use favoritemode
            else:
                # TODO: handle this better
                try:
                    user = self.bot.osu.user(member.get("osuid"), member.get("favoritemode"))
                except:
                    return await ctx.send("Failed to contact the osu!api. Please try again.", ephemeral=True)
                
                mode = self.FROM_API_CONV.get(member.get("favoritemode"))

        # profile used; no mode
        elif profile and not mode:
            # fetch user
            try:
                favoritemode = self.bot.osu.user(profile).playmode
                user = self.bot.osu.user(profile, favoritemode)
            except ValueError:
                return await ctx.send("I couldn't find that osu! profile!\nMake sure you spelled their **username** or entered their **ID** correctly!", ephemeral=True)
            except:
               return await ctx.send("An unknown error occured! Please report it to the developer!", ephemeral=True)
            
            # convert osu!api mode to fancy mode
            mode = self.FROM_API_CONV.get(favoritemode)
        # profile and mode used
        else:
            # check for user error
            if mode not in self.VALID_MODES:
                return await ctx.send("Invalid mode selection!\nValid modes are: **osu!**, **osu!taiko**, **osu!catch**, **osu!mania**.", ephemeral=True)

            # fetch user
            try:
                user = self.bot.osu.user(profile, self.TO_API_CONV.get(mode))
            except ValueError:
                return await ctx.send("I couldn't find that osu! profile!\nMake sure you spelled their **username** or entered their **ID** correctly!", ephemeral=True)
            except:
                return await ctx.send("An unknown error occured! Please report it to the developer!", ephemeral=True)

        # embed
        embed=Embed(
            title=f":flag_{user.country_code.lower()}: {':heartpulse:' if user.is_supporter else ''}{':wrench:' if user.is_bot else ''} {user.username} | {mode}", 
            color=int(hex(int(user.profile_colour.strip("#"), 16)), 0) if user.profile_colour else 0xff94ed
            )
        embed.set_thumbnail(url=f"https://a.ppy.sh/{user.id}")

        # user doesn't have statistics for requested gamemode
        if not user.statistics.global_rank:
            embed.add_field(name=f"No {mode} stats are available for {user.username}.", value="** **", inline=True)
        # user has statistics for requested gamemode
        else:
            embed.add_field(name="Global Rank", value=f"{user.statistics.global_rank:,}", inline=True)
            embed.add_field(name="Country Rank", value=f"{user.statistics.country_rank:,}", inline=True)
            embed.add_field(name="PP", value=f"{user.statistics.pp:,.2f}", inline=True)
            embed.add_field(name="Ranked Score", value=f"{user.statistics.ranked_score:,}", inline=True)
            embed.add_field(name="Total Score", value=f"{user.statistics.total_score:,}", inline=True)
            embed.add_field(name="Accuracy", value=f"{user.statistics.hit_accuracy:.2f}%", inline=True)
            embed.add_field(name="Play Count", value=f"{user.statistics.play_count:,}", inline=True)
        
        embed.set_footer(text=f"running Moé v{self.bot.version}", icon_url="https://bot.its.moe/assets/favicon/favicon-16x16.png")
        if config.debug:
            log(f"Osu: Got api data: {user.username} ({user.id})", Ansi.LGREEN)
        return await ctx.send(embed=embed)

def setup(bot) -> None:
    bot.add_cog(Osu(bot))