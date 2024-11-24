from players import *

class Lobby:
  def __init__(self, players: list, classic_gamemode: bool, current_phase: str, speaker_queue: list, until_next_phase: int, game_in_process: bool, max_player_count: int, mafia_count: int): #мб ещё дописать
    self.players = players
    self.classic_gamemode = classic_gamemode
    self.current_phase = current_phase

'''
Фазы:
  День - игроки говорят по очереди, могут пользоваться чатом, выставлять на голосование
  Голосование - голосование; если поровну, игроки говорят по 30 сек
  Вечер - речь того, кого выкинули
  Ночь
'''
   
  self.speaker_queue = speaker_queue
  self.until_next_phase = until_next_phase
  self.game_in_process = game_in_process
  self.max_player_count = max_player_count
  self.mafia_count = mafia_count

  def night_time_counter():
    # мафии даем минуту, доктору и инспектору по полминуты
    # итого 2 минуты
    self.until_next_phase = 20
    for _ in range(20):
      tick()
    
  def day_time_counter():
    # озвучивание событий за ночь
    if classic_gamemode:
      
    else:
      

  def start_game():
    self.game_in_process = True
    distribution(self.players)
    # вывести сообщение, что игра началась
    night_time_counter()
    
  def tick():  #вызывается в main
    self.until_next_phase -= 1
    if self.until_next_phase == 1:
      pass #вывести сообщение, что осталось 10 сек
    elif self.until_next_phase == 0:
      phase_shift(self.current_phase)

  def phase_shift(current_phase: str): # дописать
    match current_phase:
      case 'day':
        night_time_counter()
      case 'night':
        day_time_counter()

  def speaking_phase(current_speaker: int, time: int):
    pass

  def voting_phase(candidates: list):
    pass

  def night_phase():
    pass
  
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
  lobby_list.append(Lobby(players = [add_player(host)], classic_gamemode = classic_gamemode, current_phase = None, speaker_queue = [], until_next_phase = 0, game_in_process = False, max_player_count = max_players_count))





 ''' 
# начало игры
def allPlay_(user): #где number?
  # 
  distribution(number)
  #time.sleep(tact)
  while have_end(number) == -1:
    night()
    day()
  if have_end == 0:
    # Вывод о победе мирных
  else:
    # Вывод о победе мафии
    ''' #игровым циклом я займусь, перепишу
