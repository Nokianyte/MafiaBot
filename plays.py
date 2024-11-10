import random

class Player:
  role = None
  def __init__(self, user, name, alive, text_channel_id, voice_channel_id):
    self.user = user
    self.name = name
    self.alive = alive
    self.text_channel_id = text_channel_id
    self.voice_channel_id = voice_channel_id

  def kill(user):
    self.alive = False
  
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
        # показать роль инспектору выбранного игрока
        #
  
  def die():
    pass
  def quit():
    pass
  def tick():
    pass

'''
# добавить группы
class Group:
  count_group = 0
  # в param будет идти сначала text_channel, затем voice_channel
  # тогда если нужно узнать text_channel_id n-ого игрока то это индекс 2 * n
  # если нужно узнать voice_channel_id n-ого игрока то это индекс 2 * n + 1
  # number - номер группы, а count_group именно статический счетчик групп
  # count - кол-во игроков
  def ___init__(self, count, *param):
    Group.count_group += 1
    self.number = count_group
    self.count = count
    self.group = []
    count_mafia = round(count / 4)
    count_doctor = count_inspector = round(count / 10)
    count_peaceful = count - count_mafia - count_doctor - count_inspector
    roles = ['Doctor'] * count_doctor
    roles.extend(['Mafia'] * count_mafia)
    roles.extend(['Inspector'] * count_inspector)
    roles.extend(['Peaceful'] * count_peaceful)
    
    for i in range(count):
      # нужно знать user и text_channel_id и voice_channel_id
      role = random.choise(roles)
      players_list.append(Player(user=user, number=len(players_list), role=None, alive=True, text_channel_id=param[2 * i], voice_channel_id=param[2 * i + 1]))
      players_list.remove(role)
'''
groups_list = []

# учитывать тактовую систему перед добавлением игрока
# не добавляем игрока, пока не закончится раунд
def add_player(user, text_channel_id, voice_channel_id, number):
  # number является глобальным счетчиком групп, чтобы добавлять новые группы
  if number == len(groups_list):
    groups_list.append([Player(user=user, number=number, alive=True, text_channel_id=text_channel_id, voice_channel_id=voice_channel_id)])
  groups_list[number].append(Player(user=user, alive=True, text_channel_id=text_channel_id, voice_channel_id=voice_channel_id))

# соблюдаем такты
def remove_player(user, number):
  for i in range(groups_list[number]):
    if groups_list[number][i].user == user:
      groups_list[number].pop(i)
  #player_list.pop(find_player(user)) 

def message(number): #поменять
  bot.get_channel(player_list[find_player(number)].text_channel_id)


# создать отдельно класс раунда
class Round:
  def __init__(self, number_group):
    self.number_group = number_group
    

round_counter = [] #кол-во раундов у отдельной группы

