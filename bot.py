from discord.ext import commands
from youtube import YTDLSource
import discord

intents = discord.Intents.all()

#env.txt - Im too lazy for .env loader
with open('env.txt') as f:
    token = f.readlines()

#client
client = commands.Bot(command_prefix='.', intents=intents)
queue = []
current_song = None

@client.command(
    help="Join voice channel",
    pass_context=False)
async def join(ctx):
    await joinVC(ctx)

@client.command(
    help=".play Song_URL/title",
    pass_context=True)
async def play(ctx, *, input):
    global queue
    voice_client = await joinVC(ctx)
    if voice_client is not None:
        info_song = await YTDLSource.from_url_detail(input)
        queue.append(info_song)
        await ctx.message.channel.send('Queued: {} by {}\n'.format(info_song['title'], info_song['channel']))
        if voice_client.is_playing() is False:
            play_song(voice_client)

def play_song(voice_client):
    global current_song
    if not voice_client.is_playing():
        current_song = None
    if len(queue) > 0:
        try:
            voice_client.play(queue[0]['data'], after=lambda e: play_song(voice_client))
            current_song=queue.pop(0)
        except:
            print('Already playing')
            pass

async def joinVC(ctx):
    try:
        voice_channel = ctx.message.author.voice.channel
        guild = ctx.message.guild
        voice_client = [voice_client for voice_client in client.voice_clients if voice_client.channel == voice_channel and voice_client.guild == guild]
        if len(voice_client) < 1:
            voice_client = await voice_channel.connect()
        else:
            voice_client=voice_client[0]
        return voice_client
    except NameError:
        await ctx.message.channel.send('Connect to VC to play songs!')
        print(NameError)
        return None

@client.command(
    help="Leave voice channel",
    pass_context=False)
async def leave(ctx):
    voice_channel = ctx.message.author.voice.channel
    voice_clients = [
        voice_client for voice_client in client.voice_clients if voice_client.channel == voice_channel]
    if len(voice_clients) > 0 :
        await voice_clients[0].disconnect()

@client.command(
    help="Stop and remove current song",
    pass_context=False)
async def stop(ctx):
    voice_client = await joinVC(ctx)
    voice_client.stop()

@client.command(
    help="Stop and Clear",
    pass_context=False)
async def clear(ctx):
    global current_song
    global queue
    voice_client = await joinVC(ctx)
    voice_client.stop()
    queue=[]
    current_song=None

@client.command(
    help="Pause/Play",
    pass_context=False)
async def p(ctx):
    voice_client = await joinVC(ctx)
    if voice_client.is_paused():
        voice_client.resume()
    else:
        voice_client.pause()

@client.command(
    help="Skip song",
    pass_context=False)
async def skip(ctx):
    global current_song
    voice_client = await joinVC(ctx)
    if voice_client.is_playing():
        voice_client.stop()
        current_song = None
    else:
        current_song = None
    play_song(voice_client)

@client.command(
    help="Shutdown bot",
    pass_context=False)
async def shutdown(ctx):
    for voice_client in client.voice_clients:
        await voice_client.disconnect()
    await client.close()

@client.command(
    help="Shows queue",
    pass_context=False)
async def q(ctx):
    string = ''
    if current_song is not None:
        msg = 'Current Song: {} by {}\n'.format(current_song['title'], current_song['channel'])
    else:
        msg = 'Current Song: Not playing\n'
    string += msg
    string += 'Queue: \n'
    ind = 1
    for song in queue:
        msg = '{}. {} by {}\n'.format(ind, song['title'], song['channel'])
        string += msg
        ind += 1
    if len(queue)<1:
        await ctx.message.channel.send('No songs in queue')
    else:
        await ctx.message.channel.send("```{}```".format(string))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
client.run(token[0])