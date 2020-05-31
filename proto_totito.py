import socketio
import numpy as np
import random
import math

sio = socketio.Client()

def heuristica(boardOriginal,playerN,move):
    board = list(map(list,boardOriginal))
    EMPTY = 99
    FILL = 0
    FILLEDP11 = 1
    FILLEDP12 = 2
    FILLEDP21 = -1
    FILLEDP22 = -2
    N = 6

    punteoInicial = 0
    punteoFinal = 0

    acumulador = 0
    contador = 0

    for i in range(len(board[0])):
        if ((i+1)% N) != 0:
            if board[0][i] != EMPTY and board[0][i + 1] != EMPTY and board[1][contador + acumulador] != EMPTY and board[1][contador + acumulador + 1] != EMPTY:
                 punteoInicial = punteoInicial + 1
            acumulador = acumulador + N
        else:
            contador = contador + 1
            acumulador = 0

    board[move[0]][move[1]] = FILL

    acumulador = 0
    contador = 0

    for i in range(len(board[0])):
        if ((i + 1) % N) != 0:
            if board[0][i] != EMPTY and board[0][i + 1] != EMPTY and board[1][contador + acumulador] != EMPTY and board[1][contador + acumulador + 1] != EMPTY:
                punteoFinal = punteoFinal + 1
            acumulador = acumulador + N
        else:
            contador = contador + 1
            acumulador = 0
        
    return punteoFinal - punteoInicial

def minimax(board,pos,depth,alpha,beta,isMax):
    if depth == 0 or 99 not in np.asarray(board).reshape(-1):
        return heuristica(infoGame.board,infoGame.player_turn_id, pos)
    
    if(isMax):
        bestScore = -math.inf
        for i in range(0,2):
            for j in range(0,30):
                if board[i][j] == 99:
                    board[i][j] = infoGame.player_turn_id
                    scoreMax = minimax(board, (i,j),depth-1, alpha, beta, False)
                    board[i][j] = 99

                    bestScore = max(bestScore, scoreMax)
                    print("El best score ",str(bestScore))
                    alpha = max(alpha, scoreMax)
                    if beta <= alpha:
                        break
        return bestScore
    else:
        worstScore = math.inf
        for i in range(0,2):
            for j in range(0,30):
                if board[i][j] == 99:
                    board[i][j] == infoGame.oponent_turn_id
                    scoreMin = minimax(board, (i,j), depth-1,alpha,beta,True)
                    board[i][j] = 99
                    worstScore = min(worstScore, scoreMin)
                    print("El worst score ",str(worstScore))
                    beta = min(beta,scoreMin)
                    if beta <= alpha:
                        break
        return worstScore
                    

def bestMove(board):
    bestScore = -math.inf
    for i in range(0,2):
        for j in range(0,30):
            if board[i][j] == 99:
                board[i][j] = infoGame.player_turn_id
                score = minimax(board,(i,j),3,-math.inf,math.inf,False)
                board[i][j] = 99
                if(score > bestScore):
                    bestScore = score
                    move = (i,j)
    return move

def probar(move):

    if move == []:
        return False
    
    if move[0] < 0 or move[0] > 1:
        return False

    if move[1] < 0 or move[1] > 29:
        return False

    return True


class infoGame:
    def __init__(self):
        self.username = ""
        self.tournament_id = ""
        self.game_id = ""
        self.board = []
        self.game_finished = False
        self.player_turn_id = 0
        self.winner_turn_id = 0
        self.oponent_turn_id = 0

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
    print("Llego al ready")
    movement = []
    infoGame.game_id = server['game_id']
    infoGame.player_turn_id = server['player_turn_id']
    infoGame.board = server['board']
    infoGame.game_finished = False
    while probar(movement) != True:
        print("llego al ciclo")
        move = bestMove(infoGame.board)
        movement = [move[0],move[1]]
        print("move es igual"+str(movement[0])+","+str(movement[1]))
	
    #typeLine = random.randint(0,1)#int(input("0: Horizontal\n 1: Vertical\n"))
    #position = random.randint(0,29)#int(input("0-29: "))
    # while int(server['board'][typeLine][position]) != 99:
    #     typeLine = random.randint(0, 1)
    #     position = random.randint(0, 29)
    #movement = [typeLine,position]

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

    if(infoGame.player_turn_id == 1):
        infoGame.oponent_turn_id = 2
    else:
        infoGame.oponent_turn_id = 1

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
