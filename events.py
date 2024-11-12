from play import *
import time

# player должен запустить функцию
def create_group(player=Player):
  # player вводит число игроков (до 14 включительно) и запишем это число в переменную count   
  if count > 14 or count < 6:
    # вывести в игроку сообщение об ошибке (можно не делать, если трудно)
    return
  
  groups_list.append([Player(user=user, name=name, role=None, alive=True, text_channel_id=text_channel_id, voice_channel_id=voice_channel_id)])


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

# тактовая система
tact = 10

def night():
  

def day():
  

  
# лобби создает один игрок, который будет главным
# у главног игрока должен быть способ создания лобби (кнопка или /lobby)
def create_lobby(number):
  # создать единого voice_channel и text_channel для группы
  # чуваки из группы автоматически подключаются к одному каналу
  
# начало игры
def allPlay_(user):
  # 
  distribution(number)
  time.sleep(tact)
  while have_end(number) == -1:
    night()
    day()
  if have_end == 0:
    # Вывод о победе мирных
  else:
    # Вывод о победе мафии
