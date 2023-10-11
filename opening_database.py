import chess_lib as cl
import chess 
import opening_database
import time

piece_values = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
}

game_vars = {
    "in_opening": True,
    "opening_move": None
}

opening_moves = []

white_material = 0
black_material = 0

white_captured_pieces = []
black_captured_pieces = []

opening_database = {
    "ruy_lopez": opening_database.Ruy_lopez
}

class node:
    def __init__(self):
        self.value = None
        self.left = None
        self.right = None
        
def opening_eval(last_move):
    opening_moves.append(last_move)
    if not game_vars["opening_move"]:
        game_vars["opening_move"] = last_move
    #Kings pawn openings--------------------------------
    #---------------RUY LOPEZ-----------------#
    ruy_lopez_start = opening_database["ruy_lopez"].root
    next_move = ruy_lopez_start
    for i in opening_moves:
        if i in next_move.children:
            next_move = next_move.children[i]
        else:
            next_move = None
            break
    
    if next_move:
        if next_move.move == last_move:
            next_move = None
        else:
            opening_moves.append(next_move.move)
        
    return next_move

        
def run(last_move):
    move = None
    if game_vars["in_opening"]:
        time.sleep(0.2)
        
        move = opening_eval(last_move)
        if not move:
            game_vars["in_opening"] = False
            
    #start engine
            
    return move#Returns a move
