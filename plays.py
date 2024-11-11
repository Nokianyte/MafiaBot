import random # не импортировать ВЕСЬ модуль

class Player:
  def __init__(self, user, name, role, alive, text_channel_id, voice_channel_id):
    self.user = user
    self.name = name
    self.role = role
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

groups_list = []

def find_group_with_friends(user) -> int:
  for i in len(groups_list):
    for j in groups_list[i]:
      if j.user == user:
        return i

# учитывать тактовую систему перед добавлением игрока
# не добавляем игрока, пока не закончится раунд
def add_player(user, text_channel_id, voice_channel_id, user_friend):
  number = find_group_with_friends(user_friend)
  if len(groups_list[number]) 
  # number - номер группы
  groups_list[number].append(Player(user=user, name=name, role=None, alive=True, text_channel_id=text_channel_id, voice_channel_id=voice_channel_id))


def remove_player(user, number):
  for i in range(groups_list[number]):
    if groups_list[number][i].user == user:
      groups_list[number].pop(i)
  # поменять канал у чувака, чтобы он вышел
  # player_list.pop(find_player(user)) 


def message(number): #поменять
  bot.get_channel(player_list[find_player(number)].text_channel_id)

# раздача ролей, после игры меняем все роли на None и добавляем новых игроков
def distribution(number):
  count = len(grours_list[number])
  count_mafia = round(count / 4)
  count_doctor = count_inspector = round(count / 10)
  count_peaceful = count - count_mafia - count_doctor - count_inspector   
  roles = ['Doctor'] * count_doctor
  roles.extend(['Mafia'] * count_mafia)
  roles.extend(['Inspector'] * count_inspector)
  roles.extend(['Peaceful'] * count_peaceful)
    
  for i in range(count):
    role = random.choise(roles)
    groups_list[number][i].role = role
    roles.remove(role)

round_counter = [] #кол-во раундов у отдельной группы

