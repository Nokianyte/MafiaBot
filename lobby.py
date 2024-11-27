import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='$', intents=intents)

from random import choice as ch

'''
Сводка по функциям:

  Lobby:
    start_game - начать игру в лобби
    add_player (user) - добавить игрока
    remove_player (user) - удалить игрока

  create_lobby (channel id) - создать лобби (на вход подаются айди созданных каналов)
  fetch_by_username (user.name) - берёт имя пользователя - возвращает его лобби и статы игрока в dict
  fetch_lobby_by_channel (channel_id) - берёт ID канала, возвращает лобби, к которому он принадлежит
  delete_lobby - удалить лобби и связанные каналы
  kill_player (user) - забрать доступ игрока к голосовому, текстовым каналам лобби
  revive_player (user) - восстановить доступ игрока к голосовому, текстовым каналам лобби

  on_voice_state_update - триггерится при перемещении пользователей между голосовыми каналами. Нужно чтобы удалять/добавлять игроков в лобби при посещении соответствующего голосового канала)
'''
class Lobby:
  def __init__(self, players: list, channels: dict, game_stats: dict, max_player_count: int):

    self.players = players
    self.channels = channels 
    self.game_stats = game_stats
    self.max_player_count = max_player_count

  async def start_game(self):
    self.game_in_process = True
    self.game_stats = {
      'timer':15,
      'target':None,
      'inspected':None,
      'protected':None
    }
    count = len(self.players)
    cmafia = round(count / 4)
    cpeaceful = count - cmafia - 3
    roles = ['mafia'] * cmafia
    roles.append('protector')
    roles.append('inspector')
    roles.append('killer')
    roles.extend(['peaceful'] * cpeaceful)
    for player in self.players:
      role = ch(roles)
      player['role'] = role
      roles.remove(role)
    for player in self.players:
      if player['role'] == 'mafia':
        await bot.get_channel(self.channels['mafia_text_id']).set_permissions(player['user'], view_channel=True)
      elif player['role'] == 'killer':
        await bot.get_channel(self.channels['mafia_text_id']).set_permissions(player['user'], view_channel=True)
      elif player['role'] == 'inspector':
        await bot.get_channel(self.channels['inspector_text_id']).set_permissions(player['user'], view_channel=True)
      elif player['role'] == 'protector':
        await bot.get_channel(self.channels['protector_text_id']).set_permissions(player['user'], view_channel=True)
    
  def add_player(self, user):
    self.players.append({
      'user':user, 
      'role':None, 
      'alive':False, 
      'voted_for':None
    })

  def remove_player(self, user):
    for player in self.players:
      if player['user'] == user: 
        self.players.remove(player)
        break

lobby_list = []

def create_lobby(voice_channel_id: int, common_text_id: int, mafia_text_id: int, inspector_text_id: int, protector_text_id: int, max_players_count: int):
  lobby_list.append(Lobby(
    players = [], 
    channels = {
      'voice_channel_id':voice_channel_id, 
      'common_text_id':common_text_id, 
      'mafia_text_id':mafia_text_id, 
      'inspector_text_id':inspector_text_id,
      'protector_text_id':protector_text_id
    }, 
    game_stats = None,
    max_player_count = max_players_count
  ))

def fetch_by_username(username): # берёт ID пользователя, возвращает статы игрока, лобби
  for lobby in lobby_list:
    for player in lobby.players:
      if player['user'].name == username: return {'player':player, 'lobby':lobby}
  return None #!Переделать это тк будут вылетать ошибки

def fetch_lobby_by_channel(channel_id): # берёт ID голосового канала, возвращает объект привязанного лобби
  for lobby in lobby_list:
    if channel_id in lobby.channels.values(): return lobby
  return None

