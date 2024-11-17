# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import tasks, commands

from players import *

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
async def on_voice_state_update(member, before, after):

    if fetch_lobby(after.channel.id) != None and fetch_lobby(after.channel.id).game_in_process == False:
        fetch_lobby(after.channel.id).add_player(member)
        
    if fetch_lobby(before.channel.id) != None and fetch_lobby(after.channel.id).game_in_process == False:
        fetch_lobby(before.channel.id).remove_player(member)


class MyCog(commands.Cog): # система тактов
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
async def create_lobby(ctx, name: str, max_users: int):
    """
    Команда для создания скрытого голосового канала.
    
    :param ctx: Контекст команды.
    :param name: Имя создаваемого голосового канала.
    :param max_users: Максимальное количество участников.
    """
    guild = ctx.guild
#    overwrites = {
#        guild.default_role: discord.PermissionOverwrite(view_channel=False),  это чтобы сделать канал скрытым (пока не нужно)
#        ctx.author: discord.PermissionOverwrite(view_channel=True, connect=True)  # Разрешить автору видеть и подключаться
#    }
    
    # Создаём канал
    try:
        channel = await guild.create_voice_channel(
            name=name,
            user_limit=max_users,
 #           overwrites=overwrites
        )
        await ctx.send(f"Скрытый голосовой канал '{name}' создан с лимитом {max_users} участников!")
    except Exception as e:
        await ctx.send(f"Произошла ошибка при создании канала: {e}")




@bot.command() # добавляет игрока в список
async def join(ctx):
    member = ctx.author
    guild = ctx.guild
    channel_name = f"личный канал {len(player_list)+1}"

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True)
    }

    new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

    add_player(user=member, channel=new_channel.id)
    print(player_list)

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
