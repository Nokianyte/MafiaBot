from players import *

class Lobby:
  def __init__(self, players: list, until_next_phase: int, game_in_process: bool, max_player_count: int, mafia_count: int): #мб ещё дописать
    self.players = players   
    self.until_next_phase = until_next_phase
    self.game_in_process = game_in_process
    self.max_player_count = max_player_count
    self.mafia_count = mafia_count    

  def start_game():
    self.game_in_process = True
    distribution(self.players)
    # вывести сообщение, что игра началась
    
  def tick():  #вызывается в main
    self.until_next_phase -= 1
    if self.until_next_phase == 1:
      pass #вывести сообщение, что осталось 10 сек
    elif self.until_next_phase == 0:
      phase_shift(self.current_phase)

  def phase_shift(current_phase: str): # дописать
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

def create_lobby(host, classic_gamemode: bool, max_players_count: int):
  lobby_list.append(Lobby(players = [add_player(host)], until_next_phase = 12, game_in_process = False, max_player_count = max_players_count))
