from typing import Union

from discord import Embed
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
    lookup - look up user statistics for a specified osu! profile.
    """
    @cog_ext.cog_slash(
        name="osulookup",
        description="Look up your osu! profile!",
        options=[
            create_option(
                name="profile",
                description="The osu! profile you are looking up. This can be their username or ID.",
                option_type=3,
                required=True
            ),
            create_option(
                name="mode",
                description="The osu! gamemode you want to look up. This can be osu!, osu!taiko, osu!catch, or osu!mania.",
                option_type=3,
                required=False
            )
        ]
    )
    async def _osulookup(self, ctx: SlashContext, profile: Union[int, str], mode: str = None) -> SlashContext:
        # no mode specified; get favorite mode stats
        if not mode:
            # mode conversion dict
            mode_conv = {
                "osu": "osu!",
                "taiko": "osu!taiko",
                "fruits": "osu!catch",
                "mania": "osu!mania"
            }

            # fetch user
            try:
                playmode = self.bot.osu.user(profile).playmode
                user = self.bot.osu.user(profile, playmode)
            except ValueError:
                return await ctx.send("I couldn't find that osu! profile!\nMake sure you spelled their **username** or entered their **ID** correctly!")
            except:
               return await ctx.send("An unknown error occured! Please report it to the developer!")
            
            # convert osu!api mode to fancy mode
            mode = mode_conv.get(playmode)
        # mode specified; get specified mode stats
        else:
            # check for user error
            if mode not in ["osu!", "osu!taiko", "osu!catch", "osu!mania"]:
                return await ctx.send("Invalid mode selection!\nValid modes are: **osu!**, **osu!taiko**, **osu!catch**, **osu!mania**.")

            # mode conversion dict
            mode_conv =  {
                "osu!": GameMode.STD,
                "osu!taiko": GameMode.TAIKO,
                "osu!catch": GameMode.CTB,
                "osu!mania": GameMode.MANIA
            }

            # fetch user
            try:
                user = self.bot.osu.user(profile, mode_conv.get(mode))
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