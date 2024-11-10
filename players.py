class Player:
  def __init__(self, user, number, role, alive, text_channel_id, voice_channel_id):
    self.user = user
    self.name = name
    self.number = number
    self.role = role
    self.alive = alive
    self.text_channel_id = text_channel_id
    self.voice_channel_id = voice_channel_id
  
  def Action(self, role, choose_player):
    if role == 'Врач':
      #игрок должен выбрать другого игрока, чтобы оживить
      player_list[choose_player].alive = True
    if role == 'Мафия1' or role == 'Мафия2':
      player_list[choose_player].alive = False
    if role == 'Инспектор':
      #если идет первая ночь, то только проверка мафии
      if 
  
  
  def die():
    pass
  def quit():
    pass
  def tick():
    pass
    

player_list = []

def add_player(user,channel):
  player_list.append(Player(user=user, number=len(player_list)+1, role=None, alive=True, text_channel_id=channel, voice_channel_id=None))

def remove_player(user):
  player_list.pop(find_player(user)) 

def message(number): #поменять
  bot.get_channel(player_list[find_player(number)].text_channel_id)


# добавить группы
