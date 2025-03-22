import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import yt_dlp
import re


# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with Hoomans"))
    print("Bot is ready!")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.channel.send("**Bhaau Bhaau**")
    await bot.process_commands(message)

@bot.command(name="sleep", help="Makes the bot sleep for 1 hour")
async def sleep(ctx):
    await ctx.send("Going to sleep for **1 hour** because my powers are being misused!!")
    
    # Sleep for 1 hour (3600 seconds)
    await asyncio.sleep(3600)

    await ctx.send("I am awake now, Good Morning yall!!!")

@bot.command(name='spam', help='$spam {amount} {message}')
async def spam(ctx, amount: int, *, message):
    if amount > 50:
        await ctx.send("Shut up...delete discord and get a life!!")
    else:
        for _ in range(amount):
            await ctx.send(message)

@bot.command(name='DM', help='$DM {user} {amount} {message}')
async def dm(ctx, user: discord.User, amount: int, *, message):
    if amount > 20:
        await ctx.send('**Please....get a life**')
    else:
        await ctx.send('**Successfully sent!**')
        for _ in range(amount):
            await user.send(message)

@bot.command(name='pfp', help="Shows the user's avatar")
async def pfp(ctx, user: discord.User = None):
    user = user or ctx.author
    embed = discord.Embed(title=f"{user.name}'s Avatar")
    embed.set_image(url=user.display_avatar.url)
    await ctx.send(embed=embed)

# Music Player

yt_dl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.mp3',
    'noplaylist': True,
}

yt_dl = yt_dlp.YoutubeDL(yt_dl_opts)
queue = []
import yt_dlp
import discord

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': True,  # Prevents downloading entire playlists
        'default_search': 'ytsearch',
        'quiet': True,
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    def __init__(self, source, *, data):
        super().__init__(source)
        self.data = data
        self.title = data.get('title', 'Unknown Title')

    @classmethod
    async def from_url(cls, url: str, loop=None):
        loop = loop or asyncio.get_event_loop()
        
        # Run yt-dlp asynchronously
        with yt_dlp.YoutubeDL(cls.YTDL_OPTIONS) as ydl:
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))

        # If it's a playlist or search result, extract the first entry
        if 'entries' in data:
            data = data['entries'][0]

        if 'url' not in data:
            raise ValueError("No valid audio URL found.")

        return cls(discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS), data=data)


@bot.command(name='join', help='This command will connect me')
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send("You are not in a voice channel!")


# Create a queue to store song sources
song_queue = {}

@bot.command(name="play", help="Plays a song from YouTube")
async def play(ctx, url: str):
    voice_client = ctx.voice_client

    # Ensure the bot joins the voice channel
    if not voice_client:
        await join(ctx)

    # Convert search terms into "ytsearch:" queries
    if not re.match(r"https?://", url):
        url = f"ytsearch:{url}"

    try:
        player = await YTDLSource.from_url(url, loop=bot.loop)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {str(e)}")
        return

    # If the guild (server) does not have a queue, create one
    if ctx.guild.id not in song_queue:
        song_queue[ctx.guild.id] = []

    # Add the song to the queue
    song_queue[ctx.guild.id].append(player)

    if ctx.voice_client.is_playing():
        await ctx.send(f"Added **{player.title}** to the queue...")

    # If nothing is currently playing, start playing
    if not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command(name="skip", help="Skips the current song")
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()  # This will trigger `after` function in `play_next`
        await ctx.send("⏭ Skipping the song...")
    else:
        await ctx.send("❌ No song is currently playing!")

async def play_next(ctx):
    """Plays the next song in the queue."""
    if song_queue[ctx.guild.id]:  # If there are songs in queue
        player = song_queue[ctx.guild.id].pop(0)  # Get the next song
        ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f"**🎶 Now playing:** {player.title}")
    else:
        await ctx.send("✅ Queue is empty! Add more songs using `play <song>`.")

@bot.command(name="queue", help="Shows the current song queue")
async def queue(ctx):
    if ctx.guild.id in song_queue and song_queue[ctx.guild.id]:
        queue_list = "\n".join(f"{i+1}. {song.title}" for i, song in enumerate(song_queue[ctx.guild.id]))
        await ctx.send(f"🎵 **Current Queue:**\n{queue_list}")
    else:
        await ctx.send("🎵 The queue is empty! Add songs using `play <song>`.")

@bot.command(name="clear", help="Clears the song queue")
async def clear(ctx):
    if ctx.guild.id in song_queue:
        song_queue[ctx.guild.id] = []
    await ctx.send("🗑 Queue cleared!")

@bot.command(name='disconnect', help='Disconnects the bot from VC')
async def disconnect(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('**Disconnected...Sayonara!!**')
    else:
        await ctx.send('I am not in a voice channel!')

@bot.command(name='pause', help='Pauses the music')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("**Paused**")

@bot.command(name='resume', help='Resumes the music')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("**Resumed**")

@bot.command(name='stop', help='Stops the music')
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("**Stopped**")

bot.run(TOKEN)
