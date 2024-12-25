import os, discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
from random import choice

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

lobby_list = []

'''

Сводка по классам:

    Lobby:
        launch_game - начать игру в лобби
        add_player (user) - добавить игрока
        remove_player (user) - удалить игрока
        delete_lobby - удаляет лобби и связанные каналы
        phase_shift - сдвиг фазы игры, происходит каждые 2 минуты
        reset - конец игры, перезапуск лобби
        kill_player (user) - забирает возможность говорить/писать в лобби

    Timer - объект меняет счётчики каждые 10 сек

Сводка по командам:

    foo (arg) - возвращает arg в текстовый канал из которого была прописана команда
    create_lobby (name, max_users) - создаёт лобби со всеми нужными каналами, переносит создателя в него (можно запускать только находясь в голосовом канале)
    start_game* - начинает игру (возможно только при как минимум 6 игроках в лобби)
    ban (user)* - забанить пользователя из лобби
    vote (user) - проголосовать за игрока
    kill (user) - 'убить' игрока (role=killer)
    inspect (user) - узнать роль игрока (role=inspector)
    protect (user) - защитить игрока (role=protector)

Cводка по функциям:

    on_voice_state_update - триггерится при перемещении пользователя между голосовыми каналами чтобы выполнять функцию входа/выхода из лобби
    fetch_by_username (user.name) - берёт имя пользователя - возвращает его лобби и статы игрока в dict
    fetch_lobby_by_channel (channel_id) - берёт ID канала, возвращает лобби, к которому он принадлежит
    
    * - комманды доступны только хосту лобби

'''


class Lobby:
    def __init__(self, players: list, channels: dict, game_data: dict, game_stats: dict):

        self.players = players
        self.channels = channels 
        self.game_data = game_data
        self.game_stats = game_stats


    async def launch_game(self): #команда начала игры
        self.game_data = {
            'timer':15,
            'target':None,
            'inspected':None,
            'protected':None
        }
        self.game_stats = {
            'mafia':[],
            'killer':[],
            'inspector':[],
            'protector':[],
            'killed':0,
            'voted_out':0,
            'mafia_voted_out':0,
            'inspected':0,
            'mafia_inspected':0,
            'protected':0
        }

        # Распределение ролей

        count = len(self.players)
        cmafia = round(count / 5)
        cpeaceful = count - cmafia - 3
        roles = ['mafia'] * cmafia
        roles.append('protector')
        roles.append('inspector')
        roles.append('killer')
        roles.extend(['citizen'] * cpeaceful)
        for player in self.players:
            role = choice(roles)
            player['role'] = role
            roles.remove(role)
  

    def add_player(self, user:tuple): #добавить игрока
        self.players.append({
            'user':user, 
            'role':None, 
            'alive':False, 
            'voted_for':None
        })


    def remove_player(self, user:tuple): #удалить игрока
        for player in self.players:
            if player['user'] == user: 
                self.players.remove(player)
                break


    async def delete_lobby(self): #удаление лобби
        for channel in self.channel.values():
            await bot.get_channel(channel).delete()
        lobby_list.remove(self)


    async def phase_shift(self):

        # Убиство

        target_player = None
        for player in self.players:
            if self.game_data['target'] == player['user'].name:
                target_player = player
                break
               
        if target_player != None and self.game_data['protected'] != self.game_data['target']:
            target_player['alive'] = False
            self.game_stats['killed'] += 1
            await self.kill_player(target_player['user'])
            await bot.get_channel(self.channels['common_text_id']).send(f'{target_player['user'].name} был убит!')
        elif self.game_data['protected'] == self.game_data['target']:
            self.game_stats['protected'] += 1
            await bot.get_channel(self.channels['common_text_id']).send('Никто не был убит!')
            await bot.get_channel(self.channels['protector_text_id']).send('Вы защитили свою цель!')
        else: await bot.get_channel(self.channels['common_text_id']).send('Никто не был убит!')

        # Голосование

        ranking = [0] * len(self.players)
        for player in self.players:
            if player['voted_for'] != None:
                for index in range(len(self.players)):
                    if self.players[index]['user'].name == player['voted_for'] and self.players[index]['alive']:
                        ranking[index] += 1

        if ranking.index(max(ranking)) != ranking.index(max(ranking), -1, 0):
            await bot.get_channel(self.channels['common_text_id']).send('Голоса разделились!')
        else:
            voted_out = self.players[ranking.index(max(ranking))]
            voted_out['alive'] = False
            self.game_stats['voted_out'] += 1
            if voted_out['role'] == 'mafia' or voted_out['role'] == 'killer': self.game_stats['mafia_voted_out'] += 1
            await self.kill_player(voted_out['user'])
            await bot.get_channel(self.channels['common_text_id']).send(f'{voted_out['user'].name} был выгнан!')

        # Проверка игрока

        inspected_player = None
        for player in self.players:
            if self.game_data['inspected'] == player['user'].name:
                inspected_player = player
                break  

        if inspected_player != None and inspected_player['alive'] == True:
            if inspected_player['role'] == 'mafia' or inspected_player['role'] == 'killer':
                self.game_stats['inspected'] += 1
                self.game_stats['mafia_inspected'] += 1
                await bot.get_channel(self.channels['inspector_text_id']).send(f'{inspected_player['user']} работает на мафию!')
            else:
                self.game_stats['inspected'] += 1
                await bot.get_channel(self.channels['inspector_text_id']).send(f'{inspected_player['user']} НЕ работает на мафию!')
        else: await bot.get_channel(self.channels['inspector_text_id']).send('Проверка не была совершена!')

        # Проверка на победу

        if sum([1 for player in self.players if ((player['role'] == "mafia" or player['role'] == "killer") and player['alive'])]) > sum([1 for player in self.players if player['alive']])/2:
            await bot.get_channel(self.channels['common_text_id']).send('Победила мафия')
        elif sum([1 for player in self.players if ((player['role'] == "mafia" or player['role'] == "killer") and player['alive'])]) == 0:
            await bot.get_channel(self.channels['common_text_id']).send('Победили мирные!')
        await bot.get_channel(self.channels['common_text_id']).send(self.game_stats)
        await self.reset()


    async def reset(self):
        self.game_data = None
        self.game_stats = None
        for player in self.players:
            player = {
                'user':player['user'],
                'role':None,
                'alive':False,
                'voted_for':None
            }
        
            await bot.get_channel(self.channels['voice_channel_id']).set_permissions(player['user'], speak=True)
            await bot.get_channel(self.channels['common_text_id']).set_permissions(player['user'], send_messages=True)
            await bot.get_channel(self.channels['mafia_text_id']).set_permissions(player['user'], send_messages=True, view_channel=False)
            await bot.get_channel(self.channels['inspector_text_id']).set_permissions(player['user'], send_messgaes=True, view_channel=False)
            await bot.get_channel(self.channels['protector_text_id']).set_permissions(player['user'], send_messgaes=True, view_channel=False)
        
    
    async def kill_player(self, user:tuple):
        await bot.get_channel(self.channels['voice_channel_id']).set_permissions(user, speak=False)
        await bot.get_channel(self.channels['common_text_id']).set_permissions(user, send_messages=False)
        await bot.get_channel(self.channels['mafia_text_id']).set_permissions(user, send_messages=False)
        await bot.get_channel(self.channels['inspector_text_id']).set_permissions(user, send_messgaes=False)
        await bot.get_channel(self.channels['protector_text_id']).set_permissions(user, send_messgaes=False)



class Timer(commands.Cog): 
    
    # система тактов

    def __init__(self):
        self.trigger.start()

    def stop(self):
        self.trigger.cancel()

    @tasks.loop(seconds=10.0) # триггерится каждые 10 сек
    async def trigger(self):
        for lobby in lobby_list:
            if lobby.game_data != None:
                lobby.game_data['timer'] -= 1
                if lobby.game_data['timer'] == 1: 
                    await bot.get_channel(lobby.channels['common_text_id']).send('Осталось 10 секунд!')
                if lobby.game_data['timer'] == 0: 
                    await lobby.phase_shift()



@bot.event # отмечает готовность к работе
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    Timer() #запуск таймера


# --- КОММАНДЫ --- #


@bot.command()
async def foo(ctx, arg:str): #тест на ввод-вывод
    await ctx.send(arg)


@bot.command()
async def create_lobby(ctx, name=f'Лобби {len(lobby_list)+1}', max_users=14): #Создание лобби

    if ctx.author.voice and 6<=max_users<=14: # проверяет, находится ли автор в каком-либо голосовом канале

        guild = ctx.guild
    
        category = discord.utils.get(guild.categories, name="Игра")
        if category == None: category = await guild.create_category(name='Игра')
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False),}

        lobby_list.append(Lobby(
            players = [], 
            channels = {
                'voice_channel_id':await guild.create_voice_channel(name=name, category=category, user_limit=int(max_users)).id, 
                'common_text_id':await guild.create_text_channel(name='общий', category=category, overwrites=overwrites).id, 
                'mafia_text_id':await guild.create_text_channel(name='мафия', category=category, overwrites=overwrites).id, 
                'inspector_text_id':await guild.create_text_channel(name='шериф', category=category, overwrites=overwrites).id,
                'protector_text_id':await guild.create_text_channel(name='защитник', category=category, overwrites=overwrites).id
            }, 
            game_data = None,
            game_stats = None,
        ))

        await ctx.author.move_to(lobby_list[-1]) #Перекидывает хоста в голосовой
    
    elif not ctx.author.voice: await ctx.send('Вы должны быть в голосовом канале!')
    elif max_users < 6: await ctx.send('Максимальное количество игроков не может быть меньше 6!')
    elif max_users > 14: await ctx.send('Максимальное количество игроков не может быть больше 14!')
    else: await ctx.send('Непредвиденная ошибка!')


@bot.command()
async def start_game(ctx): # команда начала игры

    await ctx.message.delete()

    try: target_lobby = fetch_by_username(ctx.author.name)['lobby']
    except TypeError: await ctx.send('Нет в лобби!')
    else:

        if ctx.channel.id == target_lobby.channels['common_text_id'] and\
            fetch_by_username(ctx.author.name)['player'] == target_lobby.players[0] and\
            target_lobby.game_data == None and\
            len(target_lobby.players) > 3:
                
            await target_lobby.launch_game()
            for player in target_lobby.players:
                if player['role'] != 'citizen':
                    await bot.get_channel(target_lobby.channels[f'{player['role']}_text_id']).set_permissions(player['user'], view_channel=True)
                    target_lobby.game_stats[player['role']].append(player['user'].name)
    
            await ctx.send('Игра началась!')

        elif ctx.channel.id != target_lobby.channels['common_text_id']: await ctx.send('Неправильный канал!')
        elif fetch_by_username(ctx.author.name)['player'] != target_lobby.players[0]: await ctx.send('Недостаточно прав!')
        elif target_lobby.game_data != None: await ctx.send('Игра уже в процессе!')
        elif len(target_lobby.players) <= 5: await ctx.send('Недостаточно игроков!')
        else: await ctx.send('Непредвиденная ошибка!')


@bot.command()
async def ban(ctx, target:str): #функция бана

    await ctx.message.delete() # удаление сообщения автора

    target_member = discord.utils.find(lambda m: m.name == target, ctx.guild.members)
    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_player = fetch_by_username(target)['player']
        target_lobby = fetch_by_username(target)['lobby']
    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['common_text_id'] and\
            author_player == target_lobby.players[0]:
                
                await target_member.move_to(None)

                await bot.get_channel(target_lobby.channels['voice_channel_id']).set_permissions(target_member, connect=False)
                await bot.get_channel(target_lobby.channels['common_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['mafia_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['inspector_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['protector_text_id']).set_permissions(target_member, view_channel=False)
                await bot.get_channel(target_lobby.channels['protector_text_id']).set_permissions(target_member, view_channel=False)

                target_lobby.remove_player(target_player)

                await ctx.send(f'Пользователь {target} был забанен!')

        elif author_player != target_lobby.players[0]: await ctx.send('Недостаточно прав!')
        elif ctx.channel.id != target_lobby.channels['common_text_id']: await ctx.send('Неправильный канал!')


@bot.command()
async def vote(ctx, target:str): #функция голосования

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']
    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['common_text_id'] and\
            author_player in target_lobby and\
            author_player['voted_for'] == None:
                    
                author_player['voted_for'] = target
                await ctx.send(f'{ctx.author.name} проголосовал за {target}!')

        elif author_player['voted_for'] != None: await ctx.send('Вы уже проголосовали!')
        elif author_player not in target_lobby: await ctx.send('Невалидная цель!')
        elif ctx.channel.id != target_lobby.channels['common_text_id']: await ctx.send('Неправильный канал!')
        else: await ctx.send('Непредвиденная ошибка!')


@bot.command()
async def kill(ctx, target:str): #функция 'убийства'

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']
    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['mafia_text_id'] and\
            author_player in target_lobby and\
            author_player['role'] == 'killer':
                    
                target_lobby.game_data['target'] = target
                await ctx.send(f'{target} пал новой целью убийцы!')

        elif ctx.channel.id != target_lobby.channels['mafia_text_id']: await ctx.send('Неправильный канал!')
        elif author_player not in target_lobby: await ctx.send('Невалидня цель!')


@bot.command()
async def inspect(ctx, target:str): #функция проверки

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']
    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['inspector_text_id'] and\
            author_player in target_lobby and\
            author_player['role'] == 'inspector':
                    
                target_lobby.game_data['inspected'] = target
                await ctx.send(f'Шериф собирается проверить {target}!')

        elif ctx.channel.id != target_lobby.channels['inspector_text_id']: await ctx.send('Неправильный канал!')
        elif author_player not in target_lobby: await ctx.send('Невалидная цель!')


@bot.command()
async def protect(ctx, target:str): #функция защиты

    await ctx.message.delete() # удаление сообщения автора

    try:
        author_player = fetch_by_username(ctx.author.name)['player']
        target_lobby = fetch_by_username(target)['lobby']
    except TypeError: await ctx.send('Нет в лобби!')

    else:
        if ctx.channel.id == target_lobby.channels['protector_text_id'] and\
            author_player in target_lobby and\
            author_player['role'] == 'protector':
                    
                target_lobby.game_data['protected'] = target
                await ctx.send(f'{target} защищён от смерти!')

        elif ctx.channel.id != target_lobby.channels['protector_text_id']: await ctx.send('Неправильный канал!')
        elif author_player not in target_lobby: await ctx.send('Невалидная цель!')


# --- ФУНКЦИИ --- #


@bot.event
async def on_voice_state_update(member:tuple, before, after):

    #Регистрирует заход/выход игроков из голосовых каналов

    first_channel_lobby = fetch_lobby_by_channel(before.channel.id)
    second_channel_lobby = fetch_lobby_by_channel(after.channel.id)

    if second_channel_lobby != None:
        second_channel_lobby.add_player(member)
        if second_channel_lobby.game_stats != None: second_channel_lobby.kill_player(member)
        await bot.get_channel(second_channel_lobby.channels['common_text_id']).set_permissions(member, view_channel=True)
        
    if first_channel_lobby != None:
        first_channel_lobby.remove_player(member)
        await bot.get_channel(first_channel_lobby.channels['voice_channel_id']).set_permissions(member, speak=True)
        await bot.get_channel(first_channel_lobby.channels['common_text_id']).set_permissions(member, send_messages=True)
        await bot.get_channel(first_channel_lobby.channels['common_text_id']).set_permissions(member, view_channel=False)
        await bot.get_channel(first_channel_lobby.channels['mafia_text_id']).set_permissions(member, view_channel=False)
        await bot.get_channel(first_channel_lobby.channels['inspector_text_id']).set_permissions(member, view_channel=False)
        await bot.get_channel(first_channel_lobby.channels['protector_text_id']).set_permissions(member, view_channel=False)
        if len(first_channel_lobby.players)==0: await first_channel_lobby.delete_lobby()


def fetch_by_username(username:int): # берёт ID пользователя, возвращает статы игрока, лобби
    for lobby in lobby_list:
        for player in lobby.players:
            if player['user'].name == username: return {'player':player, 'lobby':lobby}
    return None


def fetch_lobby_by_channel(channel_id:int): # берёт ID голосового канала, возвращает объект привязанного лобби
    for lobby in lobby_list:
        if channel_id in lobby.channels.values(): return lobby
    return None


bot.run(TOKEN)
