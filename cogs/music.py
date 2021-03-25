import asyncio
from cmyui import Ansi, log
from youtube_dl import YoutubeDL
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from youtube_dl.utils import bug_reports_message
from discord import Embed, FFmpegPCMAudio, PCMVolumeTransformer

import config

"""
youtube_dl - our source for audio played in voice channels.
"""
bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'options': '-vn'
}

ytdl = YoutubeDL(ytdl_format_options)
class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



"""
Music - a cog designed to play music.
"""
class Music(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    """
    play - play a specified YouTube video in the currently connected voice channel.
    """
    @cog_ext.cog_slash(
        name="play",
        description="Play a YouTube video in a voice channel!",
        guild_ids=config.guild_ids
    )
    async def _play(self, ctx: SlashContext, URL: str) -> SlashContext:
        await ctx.respond()

        player = await YTDLSource.from_url(URL, loop=self.bot.loop, stream=True)
        voice_client = ctx.author.guild.voice_client
        channel = ctx.author.voice.channel
        
        # channel logic.
        if not channel:
            return await ctx.send("You aren't connect to a voice channel!\nConnect to one and try again.")
        elif voice_client:
            await voice_client.move_to(channel)
        else:
            await channel.connect()
        if voice_client.is_playing():
            return await ctx.send("Something is already playing!\nDisconnect or stop the current track and try again.")

        voice_client.play(player)
        await ctx.send(f"Now playing: **{player.title}**")

def setup(bot) -> None:
    bot.add_cog(Music(bot))