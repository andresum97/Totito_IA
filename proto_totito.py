import socketio
import numpy as np
import random
import math

sio = socketio.Client()
#Metodo para verificar movimientos disponibles en el tablero
def possibleMoves(board):
    movements = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if int(board[i][j]) == 99:
                movements.append((i,j))
    return movements

#Metodo para calcular Heuristica, basado en el contador de puntos del arbitro del server
#y revisa la cantidad de cuadros, antes y luego de realizar una jugada y muestra los puntos
#que pueden ser 0,+-1,+-2. La heuristica se basa en la cantidad de cuadros que cambian luego de una jugadas
def heuristica(boardOriginal,move,playerN, player):
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
    resultado = 0

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
     
    if(player):
        resultado = punteoFinal - punteoInicial
    else:
        resultado = (-1)*(punteoFinal - punteoInicial)

    return resultado

#Algoritmo de minimax con alpha,beta y lookahead de 2. Basado en algoritmo del video Algorithms Explain - minimax and alpha-beta pruning
def minimax(board,pos,depth,play,myId,alpha,beta):
    #Verificacion de si esta jugando max o min, (yo o el contrincante)
    if(play):
        playerPlaying = myId
    else:
        playerPlaying = (myId%2)+1
    valorH =  heuristica(board,pos,playerPlaying, not play)
    #Ultimo return cuando llega a la raiz de arbol
    if depth == 0 or valorH != 0:
        return heuristica(board,pos,playerPlaying,not play)
    
    #Recibe las posiciones en donde se pueden realizar jugadas
    board[pos[0]][pos[1]]= 0
    possibleMove = possibleMoves(board)
    #Max
    if(play):
        bestScore = -math.inf
        
        for move in possibleMove:
            scoreMax = minimax(board,move,depth-1,False,playerPlaying,alpha,beta)
            bestScore = max(bestScore,scoreMax)
            alpha = max(alpha, scoreMax)
            if beta <= alpha:
                 break
        board[pos[0]][pos[1]] = 99
        return bestScore
    #Min
    else:
        worstScore = math.inf
        for move in possibleMove:
            scoreMin = minimax(board,move,depth-1,True,playerPlaying,alpha,beta)
            worstScore = min(worstScore,scoreMin)
            beta = min(beta,scoreMin)

        board[pos[0]][pos[1]] = 99
        return worstScore
                    
#Metodo que obtiene las mejores jugadas y elige una de forma aleatoria
def bestMove(board,myId):
    bestScore = -math.inf
    possibleM = []

    possible = possibleMoves(board)
    for movimiento in possible:
        score = minimax(board, movimiento,2, False, int(myId), -math.inf, math.inf)

        if score > bestScore:
            bestScore = score
            possibleM.clear()

        if score >= bestScore:
            possibleM.append(movimiento)

    return random.choice(possibleM)

#Metodo para dibujar el tablero
def humanBoard(board):
    resultado = ''
    acumulador = 0

    for i in range(int(len(board[0])/5)):
        if board[0][i] == 99:
            resultado = resultado + '*   '
        else:
            resultado = resultado + '* - '
        if board[0][i+6] == 99:
            resultado = resultado + '*   '
        else:
            resultado = resultado + '* - '
        if board[0][i+12] == 99:
            resultado = resultado + '*   '
        else:
            resultado = resultado + '* - '
        if board[0][i+18] == 99:
            resultado = resultado + '*   '
        else:
            resultado = resultado + '* - '
        if board[0][i+24] == 99:
            resultado = resultado + '*   *\n'
        else:
            resultado = resultado + '* - *\n'

        if i != 5:
            for j in range(int(len(board[1])/5)):
                if board[1][j + acumulador] == 99:
                    resultado = resultado + '    '
                else:
                    resultado = resultado + '|   '
            acumulador = acumulador + 6
            resultado = resultado + '\n'

    return resultado

#============================================================================================
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

    if(infoGame.player_turn_id == 1):
       infoGame.oponent_turn_id = 2
    else:
       infoGame.openent_turn_id = 1

    print(humanBoard(server['board']))
    move = bestMove(infoGame.board, infoGame.player_turn_id)
    movement = [move[0],move[1]]
    print("Jugada: "+str(movement))
    
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
