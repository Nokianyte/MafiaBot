from discord.ext import commands, tasks

from lobby import *



class Timer(commands.Cog): 
    
    # система тактов

    def __init__(self):
        self.trigger.start()

    def stop(self):
        self.trigger.cancel()

    @tasks.loop(seconds=10.0) # триггерится каждые 10 сек
    async def trigger(self):
        for lobby in lobby_list:
            if lobby.game_stats != None:
                lobby.game_stats['timer'] -= 1
                if lobby.game_stats['timer'] == 1: 
                    await bot.get_channel(lobby.channels['common_text_id']).send('Осталось 10 секунд!')
                if lobby.game_stats['timer'] == 0: 
                    await phase_shift(lobby)



async def phase_shift(lobby):

    target_player = None
    for player in lobby.players:
      if lobby.game_stats['target'] == player['user'].name:
        target_player = player
        break         
    if target_player != None and lobby.game_stats['protected'] != lobby.game_stats['target']:
        target_player['alive'] = False
        await kill_player(lobby, target_player['user'])
        await bot.get_channel(lobby.channels['common_text_id']).send(f'{target_player['user'].name} был убит!')      

    ranking = [0] * len(lobby.players)
    for player in lobby.players:
        if player['voted_for'] != None:
            for index in range(len(lobby.players)):
                if lobby.players[index]['user'].name == player['voted_for']:
                    ranking[index] += 1
    if ranking.index(max(ranking)) == ranking.index(max(ranking), -1, 0):
        await bot.get_channel(lobby.channels['common_text_id']).send('Голоса разделились!')
    else:
        lobby.players[ranking.index(max(ranking))]['alive'] = False
        await kill_player(lobby, lobby.players[ranking.index(max(ranking))]['user'])
        await bot.get_channel(lobby.channels['common_text_id']).send(f'{lobby.players[ranking.index(max(ranking))]['user'].name} был выгнан!')

    inspected_player = None
    for player in lobby.players:
        if lobby.game_stats['inspected'] == player['user'].name:
            inspected_player = player
            break  
    if inspected_player != None:
        if inspected_player['alive'] == True:
            if inspected_player['role'] == 'mafia' or inspected_player['role'] == 'killer':
                await bot.get_channel(lobby.channels['inspector_text_id']).send(f'{inspected_player['user']} работает на мафию!')
            else:
                await bot.get_channel(lobby.channels['inspector_text_id']).send(f'{inspected_player['user']} НЕ работает на мафию!')

    if sum([1 for player in lobby.players if ((player['role'] == "mafia" or player['role'] == "killer") and player['alive'])]) > sum([1 for player in lobby.players if player['alive']])/2:
        await bot.get_channel(lobby.channels['common_text_id']).send('Победила мафия')
        await reset(lobby)
    elif sum([1 for player in lobby.players if ((player['role'] == "mafia" or player['role'] == "killer") and player['alive'])]) == 0:
        await bot.get_channel(lobby.channels['common_text_id']).send('Победили мирные!')
        await reset(lobby)



async def reset(lobby):
    lobby.game_stats = None
    for player in lobby.players:
        player = {'user':player['user'],
                  'role':None,
                  'alive':False,
                  'voted_for':None
                }
        
        await bot.get_channel(lobby.channels['voice_channel_id']).set_permissions(player['user'], speak=True)
        await bot.get_channel(lobby.channels['common_text_id']).set_permissions(player['user'], send_messages=True)
        await bot.get_channel(lobby.channels['mafia_text_id']).set_permissions(player['user'], send_messages=True, view_channel=False)
        await bot.get_channel(lobby.channels['inspector_text_id']).set_permissions(player['user'], send_messgaes=True, view_channel=False)
        await bot.get_channel(lobby.channels['protector_text_id']).set_permissions(player['user'], send_messgaes=True, view_channel=False)
        
    

async def kill_player(lobby, user):
    await bot.get_channel(lobby.channels['voice_channel_id']).set_permissions(user, speak=False)
    await bot.get_channel(lobby.channels['common_text_id']).set_permissions(user, send_messages=False)
    await bot.get_channel(lobby.channels['mafia_text_id']).set_permissions(user, send_messages=False)
    await bot.get_channel(lobby.channels['inspector_text_id']).set_permissions(user, send_messgaes=False)
    await bot.get_channel(lobby.channels['protector_text_id']).set_permissions(user, send_messgaes=False)

async def revive_player(lobby, user):
    await bot.get_channel(lobby.channels['voice_channel_id']).set_permissions(user, speak=True)
    await bot.get_channel(lobby.channels['common_text_id']).set_permissions(user, send_messages=True)
    await bot.get_channel(lobby.channels['mafia_text_id']).set_permissions(user, send_messages=True)
    await bot.get_channel(lobby.channels['inspector_text_id']).set_permissions(user, send_messgaes=True)
    await bot.get_channel(lobby.channels['protector_text_id']).set_permissions(user, send_messgaes=True)

