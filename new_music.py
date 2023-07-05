#!/usr/bin/env python3


from asyncio import sleep
import asyncio
import functools
import itertools
import math
import random
import os
import typing
import pathlib


import eyed3
import io
import discord
import yt_dlp
import subprocess
from errors import ChatError
from youtube_api import YouTubeDataAPI, youtube_api
from youtube_api.parsers import parse_playlist_metadata
from async_timeout import timeout
from discord.ext import commands, tasks
from decorators import has_jonbot_perms


class MusicPlayerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, YT_API):
        self.bot = bot
        self.localmusicpaht = '/media/Music/'
        self.YT_API = YouTubeDataAPI(YT_API)
        self.voice_client = None
        self.song_queue = asyncio.Queue()
        self.playback_task = None
        self.done_playing = asyncio.Event()
        self.current_song = None

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_unload(self) -> None:
        if self.voice_client is not None:
            await self.voice_client.disconnect()
        return await super().cog_unload()

    async def _join_voice(self, vc: discord.VoiceChannel):

        if self.voice_client is None:
            self.voice_client = await vc.connect()
            return

        if vc == self.voice_client.channel:
            return

        if not self.voice_client.is_playing():
            await self.voice_client.move_to(vc)
            return

        raise(ChatError('Bot busy in another VC'))

    async def _disconnect(self):
        await self.voice_client.disconnect()
        self.voice_client = None
        self.playback_task = None
        self.current_song = None
        self.done_playing.clear()
        self.song_queue = asyncio.Queue()


    @commands.command(name='leave')
    @has_jonbot_perms()
    async def disconnect_vc(self, ctx: commands.Context):
        await self._disconnect()

    async def playback(self):
        try:
            while True:
                async with asyncio.timeout(30):
                    self.current_song = await self.song_queue.get()
                await self.current_song.send_now_playing_msg()
                self.voice_client.play(self.current_song.source, after=lambda _ : self.done_playing.set())

                await self.done_playing.wait()

                self.current_song.source.cleanup()
                self.current_song = None
                self.done_playing.clear()

        except TimeoutError:
            await self._disconnect()

    async def queue_song(self, song, ctx: commands.Context, print_queue = True):

        self.song_queue.put_nowait(song)

        if self.playback_task:
            if print_queue:
                await self.post_queue(ctx)
            return
        else:
            self.playback_task = asyncio.create_task(self.playback())


    @commands.command(name='queue')
    async def post_queue(self, ctx: commands.Context):
        songqueue_size = self.song_queue.qsize()
        if songqueue_size == 0:
            await ctx.send('No songs in queue.')
            return

        queue_songname_list = [song.songname for song in list(self.song_queue._queue)]
        await ctx.send(embed =
                    discord.Embed(color=discord.Color.blurple())
                    .set_footer(text=f'{songqueue_size} songs in queue')
                    .add_field(name='Queued:', value='\n'.join(queue_songname_list), inline=True)
                    )


    @commands.command(name='playlocal')
    async def play_local(self, ctx: commands.Context, *, filepath: str):
        media_path = pathlib.Path('/', 'media', 'Music')
        path = media_path.joinpath(pathlib.Path(*filepath.split('/')))

        if path.is_file():
            await self._queue_local(ctx, path)
            return
        if path.is_dir():
            song_paths = list(path.glob('*.mp3'))
            for song_path in song_paths:
                await self._queue_local(ctx, song_path, print_queue=False)

            await self.post_queue(ctx)
            return


    async def _queue_local(self, ctx: commands.Context, path, print_queue = True):
        song = await Song.create_local_song(path, ctx)
        await self._join_voice(ctx.author.voice.channel)
        await self.queue_song(song, ctx, print_queue)

    @commands.command(name='ls')
    async def list_dir(self, ctx: commands.Context, *, filepath=''):
        media_path = pathlib.Path('/', 'media', 'Music')
        path = media_path.joinpath(pathlib.Path(*filepath.split('/')))

        dir_contents = [f'{filepath}/{x.name}' for x in path.iterdir() if (x.is_dir() or (x.suffix == '.mp3'))]
        await ctx.send('\n'.join(dir_contents), delete_after=60)


    @commands.command(name='play')
    async def play_yt(self, ctx: commands.Context, *search_query: str):
        yt_url = await self.search_yt(search_query)
        if 'playlist?list' in yt_url:
            _, playlist_id = yt_url.split('=')
            playlist_vid_ids = self.YT_API.get_videos_from_playlist_id(playlist_id)
            for vid_id in playlist_vid_ids:
                url = "https://www.youtube.com/watch?v=" + vid_id['video_id']
                await self._queue_yt(ctx, url, print_queue = False)
            await self.post_queue(ctx)

        else:
            await self._queue_yt(ctx, yt_url)


    async def _queue_yt(self, ctx: commands.Context, yt_url: str, print_queue = True):
        song = await Song.create_yt_source(yt_url, ctx)
        await self._join_voice(ctx.author.voice.channel)
        await self.queue_song(song, ctx, print_queue)

    @commands.command(name='skip')
    async def skip(self, ctx: commands.Context):
        if self.done_playing.is_set():
            return
        if ctx.author == self.current_song.requester:
            self.voice_client.stop()
            # self.done_playing.set()

    @commands.command(name='yt')
    async def yt(self, ctx, *args):
        print(args)
        url = await self.search_yt(args)
        await ctx.send(url)

    async def search_yt(self, query : typing.List[str]):
        if query[0] == '--playlist':

            print(' '.join(query[1:]))
            playlist_search = self.YT_API.search(' '.join(query[1:]), max_results=1, search_type='playlist', parser=None)
            url = "https://www.youtube.com/playlist?list=" + playlist_search[0]["id"]["playlistId"]
        else:
            vid_search = self.YT_API.search(' '.join(query), max_results=1, search_type='video')
            url = "https://www.youtube.com/watch?v=" + vid_search[0]["video_id"]

        return url


class Song():
    def __init__(self, source, requester, songname, now_playing_msg = None):
        self.source = source
        self.requester = requester
        self.now_playing_msg = now_playing_msg
        self.songname = songname

    @classmethod
    async def create_yt_source(cls, url, ctx: commands.Context):
        YTDLP_OPTIONS = {
            # 'extractaudio': True,
            # 'audioformat' : 'mp3',
            'format' : 'mp3/bestaudio/best',
            'quiet' : True
                         }
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        requester = ctx.author
        now_playing_msg = ctx.send(f'Now playing {url}')


        with yt_dlp.YoutubeDL(YTDLP_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

        # import json
        # json_string = json.dumps(ydl.sanitize_info(info), indent=4)
        # with open('yt_data.json', 'w') as outfile:
        #     outfile.write(json_string)

        songtitle = info['title']
        source = discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS)
        return cls(source, requester, songtitle, now_playing_msg)

    @classmethod
    async def create_local_song(cls, filepath: str, ctx: commands.Context):
        FFMPEG_OPTIONS = {
            #'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            #'options': '-ar 44100',
        }
        requester = ctx.author
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filepath, **FFMPEG_OPTIONS), 0.5)
        metadata = cls.parse_localsong_metadata(filepath)
        file = None
        embed = (discord.Embed(title=f'{metadata["title"]}',
                    description=f'{metadata["artist"]}  -  {metadata["albumtitle"]} [{metadata["date"]}]',
                    color=discord.Color.blurple())
                 .add_field(name='Duration', value=metadata["duration"], inline=True)
                 .add_field(name='Requested by', value=requester.mention, inline = True))

        if metadata["thumbnail"] is not None:
            file = discord.File(io.BytesIO(metadata["thumbnail"].image_data), filename="thumb.png")
            embed.set_thumbnail(url="attachment://thumb.png")
        embed_send = ctx.send(file=file, embed=embed)


        return cls(source, requester, metadata['title'], embed_send)


    async def send_now_playing_msg(self):
        if self.now_playing_msg is not None:
            await self.now_playing_msg

    
    @classmethod
    def parse_localsong_metadata(cls, filepath):
            audiometadata = eyed3.load(filepath)
            tags = audiometadata.tag
            info = audiometadata.info
            try:
                thumbnail = tags.images[0]
            except IndexError:
                thumbnail = None

            return {
                'date' : tags.getBestDate(),
                'title' : tags.title,
                'albumtitle' : tags.album,
                'artist' : tags.album_artist,
                'url' : tags.album_artist,
                'duration' : cls.parse_duration(int(info.time_secs)),
                'thumbnail' : thumbnail
            }

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)
