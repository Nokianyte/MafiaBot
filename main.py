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
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event # отмечает готовность к работе
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_voice_state_update(member, before, after): # внести изменения

    #Регистрирует заход/выход игроков из голосовых каналов

    if fetch_lobby(after.channel.id) != None: #and fetch_lobby(after.channel.id).game_in_process == False:
        fetch_lobby(after.channel.id).add_player(member)
        await bot.get_channel(fetch_lobby(after.channel.id).channels['common_text_id']).set_permissions(member, view_channel=True)
        
    if fetch_lobby(before.channel.id) != None: #and fetch_lobby(after.channel.id).game_in_process == False:
        fetch_lobby(before.channel.id).remove_player(member)
        await bot.get_channel(fetch_lobby(before.channel.id).channels['common_text_id']).set_permissions(member, view_channel=False)
        if len(before.channel.members)==0: await delete_lobby(fetch_lobby(before.channel.id))


class MyCog(commands.Cog): 
    
    # система тактов, вызывает функцию tick у объектов классов Lobby и Player раз в 10 секунд

    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=10.0)
    async def printer(self):
        print(self.index)
        self.index += 1

@bot.command()
async def foo(ctx, arg): #тест на ввод-вывод
    await ctx.send(arg)

@bot.command()
async def create_Lobby(ctx, name=f'Лобби {len(lobby_list)+1}', max_users=14): #Создание лобби

    #!Добавить условие чтобы можно было создавать лобби только из голосового

    if ctx.author.voice:

        guild = ctx.guild
    
        category = discord.utils.get(guild.categories, name="Игра")
        if category == None: category = await guild.create_category(name='Игра')

        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False),}

        voice_channel = await guild.create_voice_channel(name=name, category=category, user_limit=int(max_users))
        common_text = await guild.create_text_channel(name='общий', category=category, overwrites=overwrites)
        mafia_text = await guild.create_text_channel(name='мафия', category=category, overwrites=overwrites)
        inspector_text = await guild.create_text_channel(name='шериф', category=category, overwrites=overwrites)

        await common_text.set_permissions(ctx.author, view_channel=True)

        await ctx.author.move_to(voice_channel) #Перекидывает хоста в голосовой

        create_lobby(
            host = ctx.author, 
            name = name, 
            voice_channel_id = voice_channel.id, 
            common_text_id = common_text.id, 
            mafia_text_id = mafia_text.id, 
            inspector_text_id = inspector_text.id, 
            max_players_count = max_users
        )

@bot.command()
async def ban(ctx, user): #функция бана
    await ctx.message.delete()
    if ctx.channel.id == fetch_by_user(ctx.author)['lobby'].channels['common_text_id']:
        if fetch_by_user(ctx.author)['player']==fetch_by_user(ctx.author)['lobby'].players[0]:
            if fetch_by_user(user)['player'] in fetch_by_user(ctx.author)['lobby']:
                if user.voice.channel.id == fetch_by_user(user)['lobby'].channels['voice_channel_id']:
                    await user.move_to(None)

                fetch_by_user(user)['lobby'].channels['voice_channel_id'].set_permissions(user, connect=False)
                fetch_by_user(user)['lobby'].channels['common_text_id'].set_permissions(user, view_channel=False)
                fetch_by_user(user)['lobby'].channels['mafia_text_id'].set_permissions(user, view_channel=False)
                fetch_by_user(user)['lobby'].channels['inspector_tetx_id'].set_permissions(user, view_channel=False)

                fetch_by_user(user)['lobby'].remove_player(fetch_by_user(user)['player'])

                await ctx.send(f'Пользователь {user} был забанен!')
            
# Всё это надо дописать...

@bot.command()
async def vote(ctx, user): #функция голосования
    await ctx.message.delete()
    if ctx.channel.id == fetch_by_user(ctx.author)['lobby'].channels['common_text_id']:
        if fetch_by_user(user)['player'] in fetch_by_user(ctx.author)['lobby']:
            if fetch_by_user(ctx.author)['player'].voted_for != None:
                fetch_by_user(ctx.author)['player'].voted_for = user
                await ctx.send(f'{ctx.author} проголосовал за {user}!')

@bot.command()
async def kill(ctx, user): #функция убийства
    await ctx.message.delete()
    if ctx.channel.id == fetch_by_user(ctx.author)['lobby'].channels['mafia_text_id']:
        if fetch_by_user(user)['player'] in fetch_by_user(ctx.author)['lobby']:
            if fetch_by_user(ctx.author)['player'].role == 'killer':
                fetch_by_user(ctx.author)['lobby'].game_stats['target'] = user
                await ctx.send(f'{user} пал новой целью убийцы!')

@bot.command()
async def inspect(ctx, user): #функция проверки
    await ctx.message.delete()
    if ctx.channel.id == fetch_by_user(ctx.author)['lobby'].channels['inspector_text_id']:
        if fetch_by_user(user)['player'] in fetch_by_user(ctx.author)['lobby']:
            if fetch_by_user(ctx.author)['player'].role == 'inspector':
                fetch_by_user(ctx.author)['lobby'].game_stats['inspected'] = user
                await ctx.send(f'Шериф собирается проверить {user}!')

##

def fetch_by_user(user): #!Меганеудобная фигня, тк всегда проходится по ВСЕМ лобби и ВСЕМ игрокам пока не найдёт нужного (Помогите!)
    output = None
    for i in lobby_list:
        for j in i.players:
            if j.user == user: output = {'player':j, 'lobby':i}
    return output #!Переделать это тк будут вылетать ошибки

def fetch_lobby(channel_id): # берёт ID голосового канала, возвращает объект привязанного лобби
    output = None
    for i in lobby_list:
        if channel_id == i.channels.values(): output = i
    return output

async def delete_lobby(lobby):
    await bot.get_channel(lobby.channels['voice_channel_id']).delete()
    await bot.get_channel(lobby.channels['common_text_id']).delete()
    await bot.get_channel(lobby.channels['mafia_text_id']).delete()
    await bot.get_channel(lobby.channels['inspector_text_id']).delete()
    lobby_list.remove(lobby)

  
    
bot.run(TOKEN)
