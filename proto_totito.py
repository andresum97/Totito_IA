import socketio
import numpy as np
import random

sio = socketio.Client()

class infoGame:
    def __init__(self):
        self.username = ""
        self.tournament_id = ""
        self.game_id = ""
        self.board = []
        self.game_finished = False
        self.player_turn_id = 0
        self.winner_turn_id = 0

@sio.on('connect')
def onConnect():
    print('Connect user: '+infoGame.username)
    sio.emit('signin',{
        'user_name': infoGame.username,
        'tournament_id': infoGame.tournament_id,
        'user_role': 'player'
    })

@sio.event
def conn_error():
    print("Connection failed")

@sio.event
def disconnect():
    print("Disconnected")

@sio.on('ready')
def ready(server):
    movement = []
    infoGame.game_id = server['game_id']
    infoGame.player_turn_id = server['player_turn_id']
    infoGame.game_finished = False
    typeLine = random.randint(0,1)#int(input("0: Horizontal\n 1: Vertical\n"))
    position = random.randint(0,29)#int(input("0-29: "))
    while int(server['board'][typeLine][position]) != 99:
        typeLine = random.randint(0, 1)
        position = random.randint(0, 29)
    movement = [typeLine,position]

    print("Jugada: " + str(movement[0]) + ", " + str(movement[1]))
    
    sio.emit('play',{
        'player_turn_id':infoGame.player_turn_id,
        'tournament_id': infoGame.tournament_id,
        'game_id': infoGame.game_id,
        'movement': movement
    })

def reset():
    row = np.ones(30) * 99
    infoGame.board = [np.ndarray.tolist(row), np.ndarray.tolist(row)]

@sio.on('finish')
def finish(server):
    reset()
    infoGame.game_id = server['game_id']
    infoGame.player_turn_id = server['player_turn_id']
    infoGame.winner_turn_id = server['winner_turn_id']

    if server['player_turn_id'] == server['winner_turn_id']:
        print("Eres el ganador")
    else:
        print("Perdiste")

    infoGame.game_finished = True

    sio.emit('player_ready',{
        'tournament_id': infoGame.tournament_id,
        'game_id': infoGame.game_id,
        'player_turn_id': infoGame.player_turn_id#devolver lo que el arbitro devuelve
    })


infoGame = infoGame()
infoGame.username = input("Ingrese usuario: \n")
infoGame.tournament_id = input("Ingrese el tournament ID: \n")
host = input("Ingrese el host: ")
sio.connect(host)
