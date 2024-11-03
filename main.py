# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import tasks, commands

from players import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event # отмечает готовность к работе
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

class MyCog(commands.Cog): # система тактов
    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=1.0)
    async def printer(self):
        print(self.index)
        self.index += 1

@bot.command() # тестовая
async def foo(ctx, arg):
    await ctx.send(arg)

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

@bot.command() # покинуть игру
async def leave(ctx, user: discord.Member = None):
    remove_player(user)
    print(player_list)

##

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
