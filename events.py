from play import *
import time

class Lobby(self, players: list, current_phase: str, until_next_phase: int, game_in_process: bool, max_player_count: int, mafia_count: int): #мб ещё дописать
  self.players = players
  self.current_phase = current_phase
  self.until_next_phase = until_next_phase
  self.game_in_process = game_in_process
  self.max_player_count = max_player_count
  self.mafia_count = mafia_count

# -1 означает, что еще не конец
# 0 означает, что мафия выйграла
# 1 означает, что мирные выйграли
def have_end(number) -> int:
  mk = sum([1 for i in groups_list[number] if i.role == "Mafia" and i.alive]) # кол-во мафии
  ma = sum([1 for i in groups_list[number] if i.alive]) # кол-во живых
  if mk * 2 >= ma:
    return 1
  if mk == 0:
    return 2
  return -1

def tick():
  
  global until_next_shift
  global current_phase
  
  until_next_shift -= 1
  if until_next_shift == 1:
    pass #вывести сообщение, что осталось 10 сек
  elif until_next_shift == 0:
    phase_shift(current_phase)

def phase_shift(current_phase: str):
  match current_phase:
    case 'speaking'

def speaking_phase(current_speaker: int, time: int):
  pass

def voting_phase(candidates: list):
  pass

def night_phase():
  pass
  
# тактовая система
tact = 10


def create_lobby(user):
  # создать единого voice_channel и text_channel для группы
  #скорее всего стоит перенести в main
  

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
