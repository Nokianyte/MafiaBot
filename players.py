import random

class Player:
  def __init__(self, user, number, role, alive, text_channel_id, voice_channel_id):
    self.user = user
    self.name = name
    self.number = number
    self.role   = role
    self.alive = alive
    self.text_channel_id = text_channel_id
    self.voice_channel_id = voice_channel_id
  
  def Action(self, role, choose_player, step):
    #choose_player - выбор игрока, над которым происходит действие
    #step - выбор шага инспектора (0 или 1)
    
    if role == 'Doctor':
      # игрок должен выбрать другого игрока, чтобы оживить
      player_list[choose_player].alive = True
    
    if role == 'Mafia':
      player_list[choose_player].alive = False
    
    if role == 'Inspector':
      # если идет первая ночь, то только проверка мафии
      if step == 0:
        player_list[choose_player].alive = False
      else:
        #показать роль инспектору выбранного игрока
        
  
  def die():
    pass
  def quit():
    pass
  def tick():
    pass
    

play_list = [] # все игры


# добавить группы
class Group:
  # в param будет идти сначала 
  def ___init__(self, count, *):
    self.count = count
    self.players_list = []
    count_mafia = round(count / 4)
    count_doctor = count_inspector = round(count / 10)
    count_peaceful = count - count_mafia - count_doctor - count_inspector
    roles = ['Doctor'] * count_doctor
    roles.extend(['Mafia'] * count_mafia)
    roles.extend(['Inspector'] * count_inspector)
    roles.extend(['Peaceful'] * count_peaceful)
    
    for i in range(count):
      # нужно знать user и channel
      role = random.choise(roles)
      player_list.append(Player(user=user, number=len(player_list)+1, role=role, alive=True, text_channel_id=channel, voice_channel_id=None))
      player_list.remove(role)

    
        
'''
def add_player(user,channel, role):
  player_list.append(Player(user=user, number=len(player_list)+1, role=None, alive=True, text_channel_id=channel, voice_channel_id=None))
'''

def remove_player(user):
  player_list.pop(find_player(user)) 

def message(number): #поменять
  bot.get_channel(player_list[find_player(number)].text_channel_id)
