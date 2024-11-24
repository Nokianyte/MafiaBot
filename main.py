# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import tasks, commands

from players import *
from events import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.guild_voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event # отмечает готовность к работе
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_voice_state_update(member, before, after): # внести изменения

    if fetch_lobby(after.channel.id) != None and fetch_lobby(after.channel.id).game_in_process == False:
        fetch_lobby(after.channel.id).add_player(member)
        await bot.get_channel(fetch_lobby(after.channel.id).text_channel_id).set_permissions(ctx.author, view_channel=True)
        
    if fetch_lobby(before.channel.id) != None and fetch_lobby(after.channel.id).game_in_process == False:
        fetch_lobby(before.channel.id).remove_player(member)
        await bot.get_channel(fetch_lobby(before.channel.id).text_channel_id).set_permissions(ctx.author, view_channel=False)


class MyCog(commands.Cog): # система тактов, вызывает функцию tick у объектов классов Lobby и Player раз в 10 секунд
    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=10.0)
    async def printer(self):
        print(self.index)
        self.index += 1

@bot.command() # тестовая
async def foo(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def create_Lobby(ctx, name: str, max_users: int):

    guild = ctx.guild
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
    }
    
    create_lobby(host = ctx.author, classic_gamemode = True, max_player_count = max_users)

    voice_channel = await guild.create_voice_channel(
        name=name,
        user_limit=max_users,
    )

    channel = await guild.create_channel(
        name=name,
        overwrites=overwrites
    )

    await channel.set_permissions(ctx.author, view_channel=True)


@bot.command()
async def vote(ctx, number):
    pass

@bot.command() # покинуть игру
async def leave(ctx, user: discord.Member = None):
    remove_player(user)
    print(player_list)

##

def fetch_lobby(vc_id):
    output = None
    for i in lobby_list:
        if vc_id == i.voice_channel_id: output = i
    return output

def delete_channel(id):
    channel = bot.get_channel(id)
    channel.delete()
    return None

def move_to_vc(user, id):
    channel = bot.get_channel(id)
    user.move_to(channel)

bot.run(TOKEN)

#channel = discord.utils.get(ctx.guild.channels, name=given_name)
#channel_id = channel.id
