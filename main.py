import os

import discord
from dotenv import load_dotenv
from discord.ext import tasks, commands

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
async def on_voice_state_update(member, before, after):

    #Регистрирует заход/выход игроков из голосовых каналов

    first_channel_lobby = fetch_lobby_by_channel(before.channel.id)
    second_channel_lobby = fetch_lobby_by_channel(after.channel.id)

    if second_channel_lobby != None:
        second_channel_lobby.add_player(member.name)
        print(second_channel_lobby.players)
        await bot.get_channel(second_channel_lobby.channels['common_text_id']).set_permissions(member, view_channel=True)
        
    if first_channel_lobby != None:
        first_channel_lobby.remove_player(member.name)
        print(first_channel_lobby.players)
        await bot.get_channel(first_channel_lobby.channels['common_text_id']).set_permissions(member, view_channel=False)
        if len(first_channel_lobby.players)==0: await delete_lobby(first_channel_lobby)


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

# --- КОМАНДЫ --- 

@bot.command()
async def foo(ctx, arg): #тест на ввод-вывод
    await ctx.send(arg)

@bot.command()
async def check_all(ctx): #тест на ввод-вывод
    await ctx.send(lobby_list)

@bot.command()
async def create_Lobby(ctx, name=f'Лобби {len(lobby_list)+1}', max_users=14): #Создание лобби

    #!Добавить условие чтобы можно было создавать лобби только из голосового

    if ctx.author.voice: # проверяет, находится ли автор в каком-либо голосовом канале

        guild = ctx.guild
    
        category = discord.utils.get(guild.categories, name="Игра")
        if category == None: category = await guild.create_category(name='Игра')

        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False),}

        voice_channel = await guild.create_voice_channel(name=name, category=category, user_limit=int(max_users))
        common_text = await guild.create_text_channel(name='общий', category=category, overwrites=overwrites)
        mafia_text = await guild.create_text_channel(name='мафия', category=category, overwrites=overwrites)
        inspector_text = await guild.create_text_channel(name='шериф', category=category, overwrites=overwrites)

        create_lobby(
            voice_channel_id = voice_channel.id, 
            common_text_id = common_text.id, 
            mafia_text_id = mafia_text.id, 
            inspector_text_id = inspector_text.id, 
            max_players_count = max_users
        )

        await ctx.author.move_to(voice_channel) #Перекидывает хоста в голосовой

@bot.command()
async def ban(ctx, target): #функция бана

    await ctx.message.delete() # удаление сообщения автора

    target_member = discord.utils.find(lambda m: m.name == target, ctx.guild.members)

    try:
        author_player = fetch_by_user(ctx.author.name)['player']
        target_player = fetch_by_user(target)['player']
        target_lobby = fetch_by_user(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['common_text_id']:
            if author_player == target_lobby.players[0]:
                await target_member.move_to(None)

                await bot.get_channel(target_lobby.channels['voice_channel_id']).set_permissions(target_member, connect=False)
                await bot.get_channel(target_lobby.channels['common_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['mafia_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['inspector_text_id']).set_permissions(target_member, view_channel=False)

                target_lobby.remove_player(target_player)

                await ctx.send(f'Пользователь {target} был забанен!')


@bot.command()
async def vote(ctx, target): #функция голосования

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_user(ctx.author.name)['player']
        target_lobby = fetch_by_user(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['common_text_id']:
            if author_player in target_lobby:
                if author_player['voted_for'] != None:
                    author_player['voted_for'] = target
                    await ctx.send(f'{ctx.author} проголосовал за {target}!')


@bot.command()
async def kill(ctx, target): #функция 'убийства'

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_user(ctx.author.name)['player']
        target_lobby = fetch_by_user(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['mafia_text_id']:
            if author_player in target_lobby:
                if author_player['role'] == 'killer':
                    target_lobby.game_stats['target'] = target
                    await ctx.send(f'{target} пал новой целью убийцы!')

@bot.command()
async def inspect(ctx, target): #функция проверки

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_user(ctx.author.name)['player']
        target_lobby = fetch_by_user(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['inspector_text_id']:
            if author_player in target_lobby:
                if author_player['role'] == 'inspector':
                    target_lobby.game_stats['inspected'] = target
                    await ctx.send(f'Шериф собирается проверить {target}!')


# --- ДРУГИЕ ФУНКЦИИ ---

async def delete_lobby(lobby):
    await bot.get_channel(lobby.channels['voice_channel_id']).delete()
    await bot.get_channel(lobby.channels['common_text_id']).delete()
    await bot.get_channel(lobby.channels['mafia_text_id']).delete()
    await bot.get_channel(lobby.channels['inspector_text_id']).delete()
    lobby_list.remove(lobby)


bot.run(TOKEN)
