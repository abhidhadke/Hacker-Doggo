import discord
import nacl

import os
from dotenv import load_dotenv
from discord.ext import commands,tasks
import asyncio
import youtube_dl
import re
import requests
import datetime
import urllib


client = discord.Client()



bot = commands.Bot(command_prefix='$')

@bot.listen('on_message')
async def mention_bot(message):
    if bot.user.mentioned_in(message):
      await message.channel.send("**Bhaau Bhaau**")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with Hoomans"))
    print("Bot is ready!")

      




@bot.command(name='sleep', help = 'Shutsdown the bot')
async def shutdown(ctx):
  userid = '543447097945489418'
  await ctx.send("**Going to sleep coz my powers are being misused..tell <@{}> to wake me up.**".format(userid))
  exit()


@bot.command(name='spam', help='Spams the input message for x number of times')
async def spam(ctx, amount:int, *, message):  
      if ctx.message.author.id == 756747629739638945:
        await ctx.send("**Shut up nigga**")
      elif amount > 50:
        await ctx.send(f"Shut up...delete discord and get a life!!")
      else:
        for i in range(amount): 
            await ctx.send(message)


@bot.command(name = 'DM', help = 'Send the target user dm')
async def DM(ctx, user: discord.User, amount:int, *, message):
  if ctx.message.author.id == 756747629739638945:
        await ctx.send("**Shut up ni**a**")
  elif amount > 20:
        await ctx.send('**Please....get a life**')
  else:
        await ctx.send('**Successfully sent!**')
        for i in range(amount): 
            await user.send(message) 

    
 
 
@bot.command(name = 'pfp', help = "Downloads the target's pfp")
async def pfp(ctx, user: discord.User):
  pfp = user.avatar_url
  user_id = user.id
  await ctx.send("Hello Hooman!! a.k.a <@{}>, here is your avatar {}".format(user_id, pfp))
  
  
@bot.command(name='ban',help='bans the user')
@commands.has_any_role('mod','Anudi Mod')
async def ban(ctx,user: discord.User = None, *, reason = None):
    if (user == None or user == ctx.message.author):
      await ctx.send("**Why ban yourself when u can ban others??!!**")
      return
    if (reason == None):
      reason = "**Fuck you!!!...Thats why!!**"
    message = f"**You have been banned from {ctx.guild.name} for following reason: {reason}**"
    await user.send(message)
    await ctx.guild.ban(user, reason=reason)
    await ctx.send(f"**@{user} has been banned for the following reason: {reason}**")
  
    
@bot.command(name = 'timeout', help = 'The user is timed out from the server')
@commands.has_any_role('mod','Anudi Mod')
async def timeout(ctx, user: discord.User = None, time:int = None):
  if (user == None or user == ctx.message.author):
    await ctx.send("**You timed out yourself, wait you can't dumbass!!**")
    return
  duration = datetime.timedelta(minutes=time)
  user_id = user.id
  await user.timeout_for(duration)
  await ctx.send(f"**<@{user_id}> is successfully timed out for {time} minutes!!**")
  
  
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'audioformat': 'mp3',
    'outtmpl': '%(title)s.mp3',
    'preferredquality': '256',
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

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
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
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


queue=[]

@tasks.loop(seconds=5)
async def not_playing(ctx):
    voice_client = ctx.message.guild.voice_client
    server = ctx.message.guild
    voice_channel = server.voice_client
    if voice_client and voice_client.is_playing():
        pass
    else:
        if voice_client and voice_client.is_paused():
            pass
        else:
            async with ctx.typing():
                player_queue = await YTDLSource.from_url(queue[0], loop=client.loop)
                voice_channel.play(player_queue, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('**Now playing: {}**'.format(player_queue.title)+' **\nRequested By: **'+format(ctx.author.mention))
            os.remove(player_queue.title)
            del queue[0]


@bot.command(name='join' ,help='This command will connect me')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.author.mention))
        return
    else:
        channel = ctx.message.author.voice.channel
        
    await channel.connect()


@bot.command(name='play', help='This command plays music')
async def play(ctx,url,*args):
      voice_client = ctx.message.guild.voice_client
      server = ctx.message.guild
      voice_channel = server.voice_client
      

      for word in args:
        url += ' '
        url += word
      if voice_client and voice_client.is_playing():
        queue.append(url)
        print(queue)
        await ctx.send('**Added:** {}'.format(url)+' **Requested By: **'+format(ctx.author.mention))
        if not not_playing.is_running():
          not_playing.start(ctx)
      else:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=client.loop)
                voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('**Now Spamming:** {}'.format(player.title)+'** \nRequested By: **'+format(ctx.author.mention))
   


@bot.command(name='disconnect', help='This command stops the music and makes the bot leave the voice channel')
async def disconnect(ctx):
    voice_client = ctx.message.guild.voice_client
    await ctx.send('**Disconnected...Sayonara!!**')
    queue.clear()
    
  
    await voice_client.disconnect()
    
    

@bot.command(name='stop', help='Stops the music')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await ctx.send('**Stopped**')
    await voice_client.stop()

@bot.command(name='queue', help='Displays the queue')
async def queue_(ctx):
    await ctx.send('**Queue: ** ```{\n}```'.format(queue))

@bot.command(name='pause' , help='Pauses the music')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("**Paused**")
    else:
        await ctx.send("**I am not playing anything!!! why targeting me??!!**")

@bot.command(name='resume', help='Resumes the music')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("**Resumed**")
    else:
        await ctx.send("**It's playing...you deaf or what??**")

@bot.command(name='skip' , help='Skips the song')
async def skip(ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            async with ctx.typing():
                player_queue = await YTDLSource.from_url(queue[0], loop=client.loop)
                voice_channel.play(player_queue, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send("**Song Skipped**")
            await ctx.send('**Now playing:** {}'.format(player_queue.title))
            del queue[0]  
  

load_dotenv()
bot.run(os.getenv("TOKEN"))