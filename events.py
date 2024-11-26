class Lobby:
  def __init__(self, players: list, channels: dict, game_stats: dict, game_in_process: bool, max_player_count: int):

    self.players = players
    self.channels = channels 
    self.game_stats = game_stats
    self.game_in_process = game_in_process
    self.max_player_count = max_player_count   

  def start_game(self):
    self.game_in_process = True
    #distribution(self.players)
    self.game_stats = {
      'until_next_phase':15,
      'target':None,
      'inspected':None
    }
    # вывести сообщение, что игра началась
    
  def add_player(self, user):
    self.players.append({
      'user':user, 
      'role':None, 
      'alive':False, 
      'voted_for':None
    })

  def remove_player(self, user):
    for player in self.players:
      if player['user'] == user: self.players.remove(player)

  def tick(self):  #вызывается в main
    self.until_next_phase -= 1
    if self.until_next_phase == 1:
      pass #вывести сообщение, что осталось 10 сек
    elif self.until_next_phase == 0:
      self.phase_shift(self.current_phase)

  def phase_shift(self, current_phase: str): # дописать
    self.until_next_phase == 12
    #убить игрока, на которого нацелилась мафия
    #убить игрока, за которого проголосовало большинство города
    #активировать способность доктора
    #сказать о проверке шерифу
  
# -1 означает, что еще не конец
# 0 означает, что мафия выйграла
# 1 означает, что мирные выйграли
'''
def have_end(number) -> int:
  mk = sum([1 for i in groups_list[number] if i.role == "Mafia" and i.alive]) # кол-во мафии
  ma = sum([1 for i in groups_list[number] if i.alive]) # кол-во живых
  if mk * 2 >= ma:
    return 1
  if mk == 0:
    return 2
  return -1
'''

lobby_list = []

def create_lobby(voice_channel_id: int, common_text_id: int, mafia_text_id: int, inspector_text_id: int, max_players_count: int):
  lobby_list.append(Lobby(
    players = [], 
    channels = {
      'voice_channel_id':voice_channel_id, 
      'common_text_id':common_text_id, 
      'mafia_text_id':mafia_text_id, 
      'inspector_text_id':inspector_text_id
    }, 
    game_stats = None,
    game_in_process = False, 
    max_player_count = max_players_count
  ))

def fetch_by_user(user): # берёт ID пользователя, возвращает статы игрока, лобби
  output = None
  for lobby in lobby_list:
    for player in lobby.players:
      if player['user'] == user: output = {'player':player, 'lobby':lobby}
  return output #!Переделать это тк будут вылетать ошибки

def fetch_lobby_by_channel(channel_id): # берёт ID голосового канала, возвращает объект привязанного лобби
  output = None
  for lobby in lobby_list:
    if channel_id in lobby.channels.values(): output = lobby
  return output
