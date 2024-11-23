from random import choice as ch # не импортировать ВЕСЬ модуль
from events import Lobby

class Player:
  def __init__(self, user, name, role, alive, text_channel_id, voice_channel_id):
    self.user = user
    self.name = name
    self.role = role
    self.alive = alive
    # self.doctor = doctor
    self.text_channel_id = text_channel_id
    self.voice_channel_id = voice_channel_id

  def kill(user):
    self.alive = False
  
  def Action(self, role, choose_player):
    if role == 'Doctor':
      player_list[choose_player].alive = True
    if role == 'Mafia':
      player_list[choose_player].alive = False
    if role == 'Inspector':
      # инспектору нужно показать, является ли choose_player мафией или нет
  '''
  def die():
    pass
  def quit():
    pass
  def tick():
    pass
'''
  
lobbies_list = []

'''
def join_lobby(player, number):
  player.text_
'''

 # number - номер группы
def add_player(user, number):
  lobbies_list[number].player_list.append(Player(user=user, name=name, role=None, alive=True, text_channel_id=text_channel_id, voice_channel_id=voice_channel_id))

def remove_player(user, number):
  for i in range(lobbies_list[number]):
    if lobbies_list[number][i].user == user:
      lobbies_list[number].pop(i)
  # поменять канал у чувака, чтобы он вышел
  # player_list.pop(find_player(user)) 


def message(number): #поменять
  bot.get_channel(player_list[find_player(number)].text_channel_id)

# раздача ролей, после игры меняем все роли на None и добавляем новых игроков
def distribution(number):
  count = len(lobbies_list[number])
  cmafia = round(count / 3)
  cpeaceful = count - cmafia - 2
  roles = ['Mafia'] * cmafia
  roles.append('Doctor')
  roles.append('Inspector')
  roles.extend(['Peaceful'] * count_peaceful)
    
  for i in range(count):
    role = random.ch(roles)
    lobbies_list[number][i].role = role
    roles.remove(role)

