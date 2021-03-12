from discord import Embed
from cmyui import Ansi, log
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from objects import glob

class Osu(Cog):
    def __init(self, bot) -> None:
        self.bot = bot

    """
    lookup - look up user statistics for a specified osu! profile.
    """
    @cog_ext.cog_slash(
        name="lookup",
        description="Look up your osu! profile!",
        guild_ids=glob.config.guild_ids
    )
    async def _lookup(self, ctx: SlashContext, profile: str, mode: str) -> SlashContext:
        # build url
        url = f"https://osu.ppy.sh/api/get_user?k={glob.config.osu_api_key}&u={profile}"
        if mode not in ["osu!", "osu!taiko", "osu!catch", "osu!mania"]:
            return await ctx.send(f"Invalid mode selection!\nValid modes are: osu!, osu!taiko, osu!catch, osu!mania.")
        mode_conv =  {
            "osu!": 0,
            "osu!taiko": 1,
            "osu!catch": 2,
            "osu!mania": 3 
        }
        url += f"&m={mode_conv.get(mode)}"

        # fetch results
        async with glob.http.get(url) as resp:
            json = await resp.json()
            if not resp or not resp.ok or json == []:
                if glob.config.debug:
                    log("Osu: Failed to get api data: request failed.", Ansi.LRED)
                return await ctx.send(f"Failed to fetch {profile}'s osu! profile!\nMake sure that you have entered their name correctly!")

            embed=Embed(title=f":flag_{json['country']}: {json['username']} | {mode}", color=0xff94ed)
            embed.set_thumbnail(url=f"https://a.ppy.sh/{json['user_id']}")
            embed.add_field(name="Global Rank", value=f"{json['pp_rank']}", inline=False)
            embed.add_field(name="Country Rank", value=f"{json['pp_country_rank']}", inline=False)
            embed.add_field(name="PP", value=f"{json['pp_raw']}", inline=False)
            embed.add_field(name="Ranked Score", value=f"{json['ranked_score']}", inline=False)
            embed.add_field(name="Total Score", value=f"{json['total_score']}", inline=False)
            embed.add_field(name="Accuracy", value=f"{json['accuracy']}", inline=False)
            embed.add_field(name="Play Count", value=f"{json['playcount']}", inline=False)
            return await ctx.send(embed=embed)
            #return await ctx.send(f"Got user!\n```{json}```")


def setup(bot) -> None:
    bot.add_cog(Osu(bot))