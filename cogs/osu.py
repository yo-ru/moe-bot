from discord import Embed
from cmyui import Ansi, log
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

import config

class Osu(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    """
    lookup - look up user statistics for a specified osu! profile.
    """
    @cog_ext.cog_slash(
        name="lookup",
        description="Look up your osu! profile!",
        guild_ids=config.guild_ids
    )
    async def _lookup(self, ctx: SlashContext, profile: str, mode: str) -> SlashContext:
        await ctx.respond()

        # build url
        url = f"https://osu.ppy.sh/api/get_user?k={config.osu_api_key}&u={profile}"
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
        async with self.bot.request.get(url) as resp:
            json = await resp.json()
            if not resp or not resp.ok or json == []:
                if config.debug:
                    log("Osu: Failed to get api data: request failed.", Ansi.LRED)
                return await ctx.send(f"Failed to fetch {profile}'s osu! profile!\nMake sure that you have entered their name correctly!")

            osu = json[0]
            embed=Embed(title=f":flag_{osu['country'].lower()}: {osu['username']} | {mode}", color=0xff94ed)
            embed.set_thumbnail(url=f"https://a.ppy.sh/{osu['user_id']}")
            embed.add_field(name="Global Rank", value=f"{int(osu['pp_rank']):,}", inline=True)
            embed.add_field(name="Country Rank", value=f"{int(osu['pp_country_rank']):,}", inline=True)
            embed.add_field(name="PP", value=f"{float(osu['pp_raw']):,.2f}", inline=True)
            embed.add_field(name="Ranked Score", value=f"{int(osu['ranked_score']):,}", inline=True)
            embed.add_field(name="Total Score", value=f"{int(osu['total_score']):,}", inline=True)
            embed.add_field(name="Accuracy", value=f"{float(osu['accuracy']):.2f}%", inline=True)
            embed.add_field(name="Play Count", value=f"{int(osu['playcount']):,}", inline=True)
            return await ctx.send(embed=embed)

def setup(bot) -> None:
    bot.add_cog(Osu(bot))