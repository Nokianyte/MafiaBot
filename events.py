from play import *
import time


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
