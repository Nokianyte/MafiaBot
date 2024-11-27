import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from lobby import *
from gameplay import *

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
    Timer()

'''
Сводка по командам:

    foo (arg) - возвращает arg в текстовый канал из которого была прописана команда
    create_Lobby (name, max_users) - создаёт лобби со всеми нужными каналами, переносит создателя в него (можно запускать только находясь в голосовом канале)
    start_game* - начинает игру (возможно только при как минимум 8 игроках в лобби)
    ban (user)* - забанить пользователя из лобби
    vote (user) - проголосовать за игрока
    kill (user) - 'убить' игрока (role=killer)
    inspect (user) - узнать роль игрока (role=inspector)
    protect (user) - защитить игрока (role=protector)

    * - комманды доступны только хосту лобби

'''

@bot.command()
async def foo(ctx, arg): #тест на ввод-вывод
    await ctx.send(arg)

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
        protector_text = await guild.create_text_channel(name='защитник', category=category, overwrites=overwrites)

        create_lobby(
            voice_channel_id = voice_channel.id, 
            common_text_id = common_text.id, 
            mafia_text_id = mafia_text.id, 
            inspector_text_id = inspector_text.id,
            protector_text_id = protector_text.id, 
            max_players_count = max_users
        )

        await ctx.author.move_to(voice_channel) #Перекидывает хоста в голосовой
    
    else: await ctx.send('Вы должны быть в голосовом канале!')

@bot.command()
async def start_game(ctx): # команда начала игры

    await ctx.message.delete()

    try: target_lobby = fetch_by_username(ctx.author.name)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['common_text_id']: 
            if fetch_by_username(ctx.author.name)['player'] == target_lobby.players[0]:
                if target_lobby.game_stats == None:
                    if len(target_lobby.players) > 3:
                        await target_lobby.start_game()
                        await ctx.send('Игра началась!')
                    else: await ctx.send('Недостаточно игроков!')
                else: await ctx.send('Игра уже в процессе!')
            else: await ctx.send('Недостаточно прав!')
        else: await ctx.send('Неправильный канал!')

@bot.command()
async def ban(ctx, target): #функция бана

    await ctx.message.delete() # удаление сообщения автора

    target_member = discord.utils.find(lambda m: m.name == target, ctx.guild.members)

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_player = fetch_by_username(target)['player']
        target_lobby = fetch_by_username(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['common_text_id']:
            if author_player == target_lobby.players[0]:
                await target_member.move_to(None)

                await bot.get_channel(target_lobby.channels['voice_channel_id']).set_permissions(target_member, connect=False)
                await bot.get_channel(target_lobby.channels['common_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['mafia_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['inspector_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['protector_text_id']).set_permissions(target_member, view_channel=False)

                target_lobby.remove_player(target_player)

                await ctx.send(f'Пользователь {target} был забанен!')

            else: await ctx.send('Недостаточно прав!')
        else: await ctx.send('Неправильный канал!')


@bot.command()
async def vote(ctx, target): #функция голосования

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['common_text_id']:
            if author_player in target_lobby:
                if author_player['voted_for'] != None:
                    author_player['voted_for'] = target
                    await ctx.send(f'{ctx.author.name} проголосовал за {target}!')
                else: await ctx.send('Вы уже проголосовали!')
            else: await ctx.send('Невалидная цель!')
        else: await ctx.send('Неправильный канал!')


@bot.command()
async def kill(ctx, target): #функция 'убийства'

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['mafia_text_id']:
            if author_player in target_lobby:
                if author_player['role'] == 'killer':
                    target_lobby.game_stats['target'] = target
                    await ctx.send(f'{target} пал новой целью убийцы!')
            else: await ctx.send('Невалидня цель!')

@bot.command()
async def inspect(ctx, target): #функция проверки

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['inspector_text_id']:
            if author_player in target_lobby:
                if author_player['role'] == 'inspector':
                    target_lobby.game_stats['inspected'] = target
                    await ctx.send(f'Шериф собирается проверить {target}!')
            else: await ctx.send('Невалидная цель!')

@bot.command()
async def protect(ctx, target): #функция защиты

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']

    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['protector_text_id']:
            if author_player in target_lobby:
                if author_player['role'] == 'protector':
                    target_lobby.game_stats['protected'] = target
                    await ctx.send(f'{target} защищён от смерти!')
            else: await ctx.send('Невалидная цель!')

async def delete_lobby(lobby):
    await bot.get_channel(lobby.channels['voice_channel_id']).delete()
    await bot.get_channel(lobby.channels['common_text_id']).delete()
    await bot.get_channel(lobby.channels['mafia_text_id']).delete()
    await bot.get_channel(lobby.channels['inspector_text_id']).delete()
    await bot.get_channel(lobby.channels['protector_text_id']).delete()
    lobby_list.remove(lobby)

@bot.event
async def on_voice_state_update(member, before, after):

    #Регистрирует заход/выход игроков из голосовых каналов

    first_channel_lobby = fetch_lobby_by_channel(before.channel.id)
    second_channel_lobby = fetch_lobby_by_channel(after.channel.id)

    if second_channel_lobby != None:
        second_channel_lobby.add_player(member)
        if second_channel_lobby.game_stats != None:
            await bot.get_channel(second_channel_lobby.channels['voice_channel_id']).set_permissions(member, speak=False)
            await bot.get_channel(second_channel_lobby.channels['common_text_id']).set_permissions(member, send_messages=False)
        await bot.get_channel(second_channel_lobby.channels['common_text_id']).set_permissions(member, view_channel=True)
        
    if first_channel_lobby != None:
        first_channel_lobby.remove_player(member)
        await bot.get_channel(first_channel_lobby.channels['voice_channel_id']).set_permissions(member, speak=True)
        await bot.get_channel(first_channel_lobby.channels['common_text_id']).set_permissions(member, send_messages=True)
        await bot.get_channel(first_channel_lobby.channels['common_text_id']).set_permissions(member, view_channel=False)
        await bot.get_channel(first_channel_lobby.channels['mafia_text_id']).set_permissions(member, view_channel=False)
        await bot.get_channel(first_channel_lobby.channels['inspector_text_id']).set_permissions(member, view_channel=False)
        await bot.get_channel(first_channel_lobby.channels['protector_text_id']).set_permissions(member, view_channel=False)
        if len(first_channel_lobby.players)==0: await delete_lobby(first_channel_lobby)

bot.run(TOKEN)
