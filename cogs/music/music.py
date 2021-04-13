import discord
import asyncio
import random
import youtube_dl
import string
import os
from discord.ext import commands
from googleapiclient.discovery import build
from discord.ext.commands import command

import config

YOUTUBE_API = config.YOUTUBE_API

ytdl_format_options = {
    'audioquality': 5,
    'format': 'bestaudio',
    'outtmpl': '{}',
    'restrictfilenames': True,
    'flatplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    "extractaudio": True,
    "audioformat": "opus",
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

# Download youtube-dl options
ytdl_download_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.mp3',
    'reactrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addreacses cause issues sometimes
    'source_addreacs': '0.0.0.0',
    'output': r'youtube-dl',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
        }]
}

stim = {
    'default_search': 'auto',
    "ignoreerrors": True,
    'quiet': True,
    "no_warnings": True,
    "simulate": True,  # do not keep the video files
    "nooverwrites": True,
    "keepvideo": False,
    "noplaylist": True,
    "skip_download": False,
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}


ffmpeg_options = {
    'options': '-vn',
    # 'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}


class Downloader(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get("url")
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration')
        self.views = data.get('view_count')
        self.playlist = {}

    @classmethod
    async def video_url(cls, url, ytdl, *, loop=None, stream=False):
        """
        Download the song file and data
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        song_list = {'queue': []}
        if 'entries' in data:
            if len(data['entries']) > 1:
                playlist_titles = [title['title'] for title in data['entries']]
                song_list = {'queue': playlist_titles}
                song_list['queue'].pop(0)

            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data), song_list

    async def get_info(self, url):
        """
        Get the info of the next song by not downloading the actual file but just the data of song/query
        """
        yt = youtube_dl.YoutubeDL(stim)
        down = yt.extract_info(url, download=False)
        data1 = {'queue': []}
        if 'entries' in down:
            if len(down['entries']) > 1:
                playlist_titles = [title['title'] for title in down['entries']]
                data1 = {'title': down['title'], 'queue': playlist_titles}

            down = down['entries'][0]['title']

        return down, data1


class музыка(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.music=self.database.find_one('music')
        self.player = {
            "audio_files": []
        }
        '''проигрывание музыки через YouTube'''

    def database_setup(self):
        URL = os.getenv("MONGO")
        if URL is None:
            return False

    @property
    def random_color(self):
        return discord.Color.from_rgb(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))

    async def yt_info(self, song):
        """
        Get info from youtube
        """
        API_KEY = 'API_KEY'
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        song_data = youtube.search().list(part='snippet').execute()
        return song_data[0]

    @commands.Cog.listener('on_voice_state_update')
    async def music_voice(self, user, before, after):
        """
        Clear the server's playlist after bot leave the voice channel
        """
        if after.channel is None and user.id == self.bot.user.id:
            try:
                self.player[user.guild.id]['queue'].clear()
            except KeyError:
                # NOTE: server ID not in bot's local self.player dict
                # Server ID lost or was not in data before disconnecting
                print(f"Failed to get guild id {user.guild.id}")

    async def filename_generator(self):
        """
        Generate a unique file name for the song file to be named as
        """
        chars = list(string.ascii_letters+string.digits)
        name = ''
        for i in range(random.randint(9, 25)):
            name += random.choice(chars)

        if name not in self.player['audio_files']:
            return name

        return await self.filename_generator()

    async def playlist(self, data, msg):
        """
        THIS FUNCTION IS FOR WHEN YOUTUBE LINK IS A PLAYLIST
        Add song into the server's playlist inside the self.player dict
        """
        for i in data['queue']:
            print(i)
            self.player[msg.guild.id]['queue'].append(
                {'title': i, 'author': msg})

    async def queue(self, msg, song):
        """
        Add the query/song to the queue of the server
        """
        title1 = await Downloader.get_info(self, url=song)
        title = title1[0]
        data = title1[1]
        # NOTE:needs fix here
        if data['queue']:
            await self.playlist(data, msg)
            # NOTE: needs to be embeded to make it better output
            return await msg.send(f"✅⟩Был добавлен плейлист {data['title']} в очередь")
        self.player[msg.guild.id]['queue'].append(
            {'title': title, 'author': msg})
        return await msg.send(f"✅⟩**{title} была добавлена в очередь**".title())

    async def voice_check(self, msg):
        """
        function used to make bot leave voice channel if music not being played for longer than 2 minutes
        """
        if msg.voice_client is not None:
            await asyncio.sleep(120)
            if msg.voice_client is not None and msg.voice_client.is_playing() is False and msg.voice_client.is_paused() is False:
                await msg.voice_client.disconnect()

    async def clear_data(self, msg):
        """
        Clear the local dict data
            name - remove file name from dict
            remove file and filename from directory
            remove filename from global audio file names
        """
        name = self.player[msg.guild.id]['name']
        os.remove(name)
        self.player['audio_files'].remove(name)

    async def loop_song(self, msg):
        """
        Loop the currently playing song by replaying the same audio file via `discord.PCMVolumeTransformer()`
        """
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(self.player[msg.guild.id]['name']))
        loop = asyncio.get_event_loop()
        try:
            msg.voice_client.play(
                source, after=lambda a: loop.create_task(self.done(msg)))
            msg.voice_client.source.volume = self.player[msg.guild.id]['volume']
            # if str(msg.guild.id) in self.music:
            #     msg.voice_client.source.volume=self.music['vol']/100
        except Exception as Error:
            # Has no attribute play
            print(Error)  # NOTE: output back the error for later debugging

    async def done(self, msg, msgId: int = None):
        """
        Function to run once song completes
        Delete the "Now playing" message via ID
        """
        if msgId:
            try:
                message = await msg.channel.fetch_message(msgId)
                await message.delete()
            except Exception as Error:
                print("Failed to get the message")

        if self.player[msg.guild.id]['reset'] is True:
            self.player[msg.guild.id]['reset'] = False
            return await self.loop_song(msg)

        if msg.guild.id in self.player and self.player[msg.guild.id]['repeat'] is True:
            return await self.loop_song(msg)

        await self.clear_data(msg)

        if self.player[msg.guild.id]['queue']:
            queue_data = self.player[msg.guild.id]['queue'].pop(0)
            return await self.start_song(msg=queue_data['author'], song=queue_data['title'])

        else:
            await self.voice_check(msg)

    async def start_song(self, msg, song):
        new_opts = ytdl_format_options.copy()
        audio_name = await self.filename_generator()

        self.player['audio_files'].append(audio_name)
        new_opts['outtmpl'] = new_opts['outtmpl'].format(audio_name)

        ytdl = youtube_dl.YoutubeDL(new_opts)
        download1 = await Downloader.video_url(song, ytdl=ytdl, loop=self.bot.loop)
        download = download1[0]
        data = download1[1]
        self.player[msg.guild.id]['name'] = audio_name
        emb = discord.Embed(colour=self.random_color, title='Сейчас играет',
                            description=download.title, url=download.url)
        emb.set_thumbnail(url=download.thumbnail)
        emb.set_footer(
            text=f'Была вызвана {msg.author.display_name}', icon_url=msg.author.avatar_url)
        loop = asyncio.get_event_loop()

        if data['queue']:
            await self.playlist(data, msg)

        msgId = await msg.send(embed=emb)
        self.player[msg.guild.id]['player'] = download
        self.player[msg.guild.id]['author'] = msg
        msg.voice_client.play(
            download, after=lambda a: loop.create_task(self.done(msg, msgId.id)))

        # if str(msg.guild.id) in self.music: #NOTE adds user's default volume if in database
        #     msg.voice_client.source.volume=self.music[str(msg.guild.id)]['vol']/100
        msg.voice_client.source.volume = self.player[msg.guild.id]['volume']
        return msg.voice_client

    @commands.command()
    async def play(self, msg, *, song):
        """Поставить музыку в голосовом чате

        Пример:

        mplay dont start now или ссылка на музыку с ютуба
        """
        if msg.guild.id in self.player:
            if msg.voice_client.is_playing() is True:  # NOTE: SONG CURRENTLY PLAYING
                return await self.queue(msg, song)

            if self.player[msg.guild.id]['queue']:
                return await self.queue(msg, song)

            if msg.voice_client.is_playing() is False and not self.player[msg.guild.id]['queue']:
                return await self.start_song(msg, song)

        else:
            # IMPORTANT: THE ONLY PLACE WHERE NEW `self.player[msg.guild.id]={}` IS CREATED
            self.player[msg.guild.id] = {
                'player': None,
                'queue': [],
                'author': msg,
                'name': None,
                "reset": False,
                'repeat': False,
                'volume': 0.5
            }
            return await self.start_song(msg, song)

    @play.before_invoke
    async def before_play(self, msg):
        """ Поставить музыку с ютуб

        Пример:

        mplay <название/ссылка на ютуб>
        """

        if msg.author.voice is None:
            return await msg.send('**Пожалуйста** войдите в голосовой канал'.title())

        if msg.voice_client is None:
            return await msg.author.voice.channel.connect()

        if msg.voice_client.channel != msg.author.voice.channel:

            # NOTE: Check player and queue
            if msg.voice_client.is_playing() is False and not self.player[msg.guild.id]['queue']:
                return await msg.voice_client.move_to(msg.author.voice.channel)
                # NOTE: move bot to user's voice channel if queue does not exist

            if self.player[msg.guild.id]['queue']:
                # NOTE: user must join same voice channel if queue exist
                return await msg.send("Пожалуйста, войдите в голосовой канал, чтобы поставить музыку в очередь")

    @commands.command()
    async def repeat(self, msg):
        """Повторить прошлую музыку

        Пример:

        mrepeat
        """
        if msg.guild.id in self.player:
            if msg.voice_client.is_playing() is True:
                if self.player[msg.guild.id]['repeat'] is True:
                    self.player[msg.guild.id]['repeat'] = False
                    return await msg.message.add_reaction(emoji='✅')

                self.player[msg.guild.id]['repeat'] = True
                return await msg.message.add_reaction(emoji='✅')

            return await msg.send("Музыки нет, чтобы повторить")
        return await msg.send("Я не нахожусь в голосовом канале, чтобы проиграть музыку")


    @commands.command()
    async def skip(self, msg):
        """Пропустить музыку

        Пример:

        mskip
        """
        if msg.voice_client is None:
            return await msg.send("**В данный момент музыка не играет**".title(), delete_after=60)

        if msg.author.voice is None or msg.author.voice.channel != msg.voice_client.channel:
            return await msg.send("Пожалуйста войдите в голосовой канал ко мне")

        if not self.player[msg.guild.id]['queue'] and msg.voice_client.is_playing() is False:
            return await msg.send("**Нет песен для пропуска**".title(), delete_after=60)

        self.player[msg.guild.id]['repeat'] = False
        msg.voice_client.stop()
        return await msg.message.add_reaction(emoji='✅')


    @commands.command(name='queue')
    async def queue(self, msg):
        """Посмотреть музыку в очереди

        Пример:

        mqueue
        """
        if msg.voice_client is not None:
            if msg.guild.id in self.player:
                if self.player[msg.guild.id]['queue']:
                    emb = discord.Embed(
                        colour=self.random_color, title='queue')
                    emb.set_footer(
                        text=f'Команда была вызвана {msg.author.name}', icon_url=msg.author.avatar_url)
                    for i in self.player[msg.guild.id]['queue']:
                        emb.add_field(
                            name=f"**{i['author'].author.name}**", value=i['title'], inline=False)
                    return await msg.send(embed=emb, delete_after=120)

        return await msg.send("Песен нет в очереди")


    @commands.command(aliases=['vol'])
    async def volume(self, msg, vol: int):
        """Поставить громкость бота

        Пример:

        mvolume <0-250>
        """

        if vol > 200:
            vol = 200
        vol = vol/100
        if msg.author.voice is not None:
            if msg.voice_client is not None:
                if msg.voice_client.channel == msg.author.voice.channel and msg.voice_client.is_playing() is True:
                    msg.voice_client.source.volume = vol
                    self.player[msg.guild.id]['volume'] = vol
                    # if (msg.guild.id) in self.music:
                    #     self.music[str(msg.guild.id)]['vol']=vol
                    return await msg.message.add_reaction(emoji='✅')

        return await msg.send("**Пожалуйста** войдите в голосовой канал для изменения громкости".title(), delete_after=30)

def setup(bot):
    bot.add_cog(музыка(bot))
