from typing import Union

from discord import Embed, guild
from discord.activity import Game
from ossapi.enums import GameMode
from cmyui.logging import Ansi, log
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

import config

class Osu(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    """
    osulink - link your osu
    TODO: use OAuth to link users' account
    """
    @cog_ext.cog_slash(
        name="osulink",
        description="Link your osu! profile to discord!",
        options=[
            create_option(
                name="profile",
                description="The osu! profile you are linking. This can your username or ID.",
                option_type=3,
                required=True
            )
        ]
    )
    async def _osulink(self, ctx: SlashContext, profile: Union[int, str]) -> SlashContext:
        # osu! profile already linked
        if await self.bot.db.fetch("SELECT 1 FROM osulink WHERE discordid = %s", ctx.author.id):
            return await ctx.send("You already have an osu! profile linked!")

        # check if osu! profile exists
        try:
            user = self.bot.osu.user(profile)
        except ValueError:
                return await ctx.send("I couldn't find that osu! profile!\nMake sure you spelled their **username** or entered their **ID** correctly!")
        except:
            return await ctx.send("An unknown error occured! Please report it to the developer!")
        
        # check if someone has already linked that osu! profile
        if await self.bot.db.fetch("SELECT 1 FROM osulink WHERE osuid = %s", profile):
            return await ctx.send(f"Someone has already linked the osu! profile, **{user.username}**, to their account!")
        # store osulink
        else:
            await self.bot.db.execute(
                "INSERT INTO osulink "
                "(discordid, osuid, favoritemode) "
                "VALUES (%s, %s, %s)",
                [ctx.author.id, user.id, user.playmode]
            )
            return await ctx.send(f"Successfully linked the osu! profile, **{user.username}**, to discord!")  



    """
    osulookup - look up user statistics for a specified osu! profile.
    """
    @cog_ext.cog_slash(
        name="osulookup",
        description="Look up your osu! profile!",
        options=[
            create_option(
                name="profile",
                description="The osu! profile you are looking up. This can be their username or ID.",
                option_type=3,
                required=False
            ),
            create_option(
                name="mode",
                description="The osu! gamemode you want to look up. This can be osu!, osu!taiko, osu!catch, or osu!mania.",
                option_type=3,
                required=False
            )
        ],
        guild_ids=config.guild_ids
    )
    async def _osulookup(self, ctx: SlashContext, profile: Union[int, str] = None, mode: str = None) -> SlashContext:
        TO_API_CONV = {
            "osu!": GameMode.STD,
            "osu!taiko": GameMode.TAIKO,
            "osu!catch": GameMode.CTB,
            "osu!mania": GameMode.MANIA
        }

        FROM_API_CONV = {
            "osu": "osu!",
            "taiko": "osu!taiko",
            "fruits": "osu!catch",
            "mania": "osu!mania"
        }

        VALID_MODES = [
            "osu!", 
            "osu!taiko", 
            "osu!catch", 
            "osu!mania"
        ]

        # user has linked account
        if not profile:
            member = await self.bot.db.fetch("SELECT * FROM osulink WHERE discordid = %s", ctx.author.id)
            if not member:
                return await ctx.send("You don't have a osu! profile linked!\nLink one with **/osulink** or specifiy a username when using **/osulookup**!")

            if mode:
                if mode not in VALID_MODES:
                    return await ctx.send("Invalid mode selection!\nValid modes are: **osu!**, **osu!taiko**, **osu!catch**, **osu!mania**.")

                user = self.bot.osu.user(member.get("osuid"), TO_API_CONV.get(mode))
            else:
                user = self.bot.osu.user(member.get("osuid"), member.get("favoritemode"))
                mode = FROM_API_CONV.get(member.get("favoritemode"))

        # profile used; no mode
        elif profile and not mode:
            # fetch user
            try:
                favoritemode = self.bot.osu.user(profile).playmode
                user = self.bot.osu.user(profile, favoritemode)
            except ValueError:
                return await ctx.send("I couldn't find that osu! profile!\nMake sure you spelled their **username** or entered their **ID** correctly!")
            except:
               return await ctx.send("An unknown error occured! Please report it to the developer!")
            
            # convert osu!api mode to fancy mode
            mode = FROM_API_CONV.get(favoritemode)
        # profile and mode used
        else:
            # check for user error
            if mode not in VALID_MODES:
                return await ctx.send("Invalid mode selection!\nValid modes are: **osu!**, **osu!taiko**, **osu!catch**, **osu!mania**.")

            # fetch user
            try:
                user = self.bot.osu.user(profile, TO_API_CONV.get(mode))
            except ValueError:
                return await ctx.send("I couldn't find that osu! profile!\nMake sure you spelled their **username** or entered their **ID** correctly!")
            except:
                return await ctx.send("An unknown error occured! Please report it to the developer!")

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
        
        if config.debug:
            log(f"Osu: Got api data: {user.username} ({user.id})", Ansi.LGREEN)
        return await ctx.send(embed=embed)

def setup(bot) -> None:
    bot.add_cog(Osu(bot))