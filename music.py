# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Valentin B.

A simple music bot written in discord.py using youtube-dl.

Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.

Requirements:

Python 3.5+
pip install -U discord.py pynacl youtube-dl

You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
"""
from asyncio import sleep
import asyncio
import functools
import itertools
import math
import random
import os

import eyed3
import io
import discord
import youtube_dl
import subprocess
from youtube_api import YouTubeDataAPI
from async_timeout import timeout
from discord.ext import commands, tasks
from decorators import has_jonbot_perms

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


# TODO playlist support

class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': False,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        # self.uploader = data.get('uploader')
        # self.uploader_url = data.get('uploader_url')
        # date = data.get('upload_date')
        # self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        # self.title = data.get('title')
        # self.thumbnail = data.get('thumbnail')
        # self.description = data.get('description')
        # self.duration = self.parse_duration(int(data.get('duration')))
        # self.tags = data.get('tags')
        # self.url = data.get('webpage_url')
        # self.views = data.get('view_count')
        # self.likes = data.get('like_count')
        # self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')


    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        
        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        print(info['url'])
        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

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

class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        file = None
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return file, embed

class LocalSource(discord.PCMVolumeTransformer):
    FFMPEG_OPTIONS = {
        #'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        #'options': '-ar 44100',
    }

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, tags, info, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.tags = tags

        self.date = tags.getBestDate()
        self.title = tags.title
        self.albumtitle = tags.album
        self.artist = tags.album_artist
        self.url = tags.album_artist
        self.duration = self.parse_duration(int(info.time_secs))
        try:
            self.thumbnail = tags.images[0]
        except IndexError:
            self.thumbnail = None

    def __str__(self):
        return '**{0.title}** by **{0.artist}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, filepath: str):

        audiometadata = eyed3.load(filepath)
        return cls(ctx, discord.FFmpegPCMAudio(filepath, **cls.FFMPEG_OPTIONS), tags=audiometadata.tag, info = audiometadata.info)

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

class LocalSong:
    __slots__ = ('source', 'requester')

    def __init__(self, source: LocalSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        file = None
        embed = (discord.Embed(title=f'{self.source.title}', description=f'{self.source.artist}  -  {self.source.albumtitle} [{self.source.date}]', color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration, inline=True)
                 .add_field(name='Requested by', value=self.requester.mention, inline = True))

        if self.source.thumbnail is not None:
            file = discord.File(io.BytesIO(self.source.thumbnail.image_data), filename="thumb.png")
            embed.set_thumbnail(url="attachment://thumb.png")

        return file, embed

class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                self.current = await self.songs.get()

            file, embed = self.current.create_embed()
            await self.current.source.channel.send(file = file, embed = embed)

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)

            # pause for a sec to buffer
            self.voice.pause()
            await asyncio.sleep(0.5)
            self.voice.resume()


            await self.next.wait()
            if not self.voice.is_playing():
                if not len(self.songs):
                    await self.auto_disconnect()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None

    @tasks.loop(count=1)
    async def auto_disconnect(self):
        for _ in range(60):
            await sleep(1)
            if len(self.songs):
                return
        if not self.voice.is_playing() and not len(self.songs):
            await self.stop()


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot, YT_API):
        self.bot = bot
        self.voice_states = {}
        self.localmusicpath = '/media/Music/'
        self.YT_API = YouTubeDataAPI(YT_API)


    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    # async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    #     await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    @has_jonbot_perms()
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.

        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    @has_jonbot_perms()
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        # if not ctx.voice_state.voice:
        #     return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        await ctx.author.voice.channel.disconnect()

        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')

        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""

        file, embed = ctx.voice_state.current.create_embed()
        await ctx.send(file=file, embed=embed)

    @commands.command(name='pause')
    @has_jonbot_perms()
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    @has_jonbot_perms()
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    @has_jonbot_perms()
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.

        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                url = await self.search_yt(search)
                source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else: 
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {}'.format(str(source)))

    async def search_yt(self, search):
        vid_search = self.YT_API.search(search)
        url = "https://www.youtube.com/watch?v=" + vid_search[0]["video_id"]
        return url

    @commands.command(name='playlocal')
    async def _play_local(self, ctx: commands.Context, *, filepath: str):

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            source = await LocalSource.create_source(ctx, f'{self.localmusicpath}{filepath}')
            song = LocalSong(source)
            await ctx.voice_state.songs.put(song)
            await ctx.send('Enqueued {}'.format(str(source)))

    @commands.command(name='playlocalalbum')
    async def _play_local_album(self, ctx: commands.Context, *, folderpath: str):
        song_list = [f for f in os.listdir(f'{self.localmusicpath}{folderpath}') if f.endswith(('.mp3'))]
        for song in sorted(song_list):
            await self._play_local(ctx, filepath=f'{folderpath}/{song}')


    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

    # @commands.command(name='yt')
    # async def yt(self, ctx, *, arg):
    #     url = await self.search_yt(arg)
    #     await ctx.send(url)

    # async def search_yt(self, search):
    #     vid_search = self.YT_API.search(search)
    #     url = "https://www.youtube.com/watch?v=" + vid_search[0]["video_id"]
    #     return url

class Filetree(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.root_path = '/media/Music/'

    @commands.command(name='tree')
    async def _tree(self, ctx: commands.Context, *, folderpath = ""):
        full_path = f'{self.root_path}{folderpath}'
        out = subprocess.check_output(['tree','-L','1',full_path])
        await ctx.send(out.decode('UTF-8'), delete_after=30)

