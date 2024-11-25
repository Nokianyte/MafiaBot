from random import choice as ch

class Player:
  def __init__(self, user, role, alive, voted_for): #дописать функционал
    self.user = user
    self.role = role
    self.alive = alive
    self.voted_for = voted_for

# раздача ролей, после игры меняем все роли на None
def distribution(_players: list):
  count = len(_players)
  cmafia = round(count / 3)
  cpeaceful = count - cmafia - 2
  roles = ['Mafia'] * cmafia
  roles.append('Doctor')
  roles.append('Inspector')
  roles.extend(['Peaceful'] * count_peaceful)
    
  for i in range(count):
    role = random.ch(roles)
    _players[i].role = role
    roles.remove(role)

