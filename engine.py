import chess_lib as cl
import chess 
import opening_database
import time
import random

piece_values = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
}

game_vars = {
    "in_opening": True,
    "opening_move": None,
    "opening_type": None,
    "debug_mode": False
}

opening_moves = []

white_material = 0
black_material = 0

white_captured_pieces = []
black_captured_pieces = []

engine_opening_preferences = {
    "e2e4": {
        opening_database.Ruy_lopez,
        opening_database.vienna_game
    },
    "d2d4": {
        opening_database.queens_gambit
    }
}

opening_database = {
    "e2e4": {"ruy_lopez": opening_database.Ruy_lopez,
           "vienna_game": opening_database.vienna_game},
    
    "d2d4": {"queens_gambit": opening_database.queens_gambit}
    
}

class node:
    def __init__(self):
        self.value = None
        self.left = None
        self.right = None
        
def variation_search():
    pass

def narrow_variation_search():
    pass

def deep_opening_search():
    pass

def main_opening_search(last_move):
    opening_moves.append(last_move)
    debug_mode = game_vars["debug_mode"]
    if not game_vars["opening_move"]:
        game_vars["opening_move"] = last_move  
        #preference opening search
        if game_vars["opening_move"] in engine_opening_preferences:   
            game_vars["opening_type"] = opening_database[game_vars["opening_move"]]       
        elif game_vars["opening_move"] in opening_database:
            pass
        else:
            print("\nopening not in database, starts engine") 
            
    #debug....
    if debug_mode:
        print("\n",last_move)
    if game_vars["opening_type"] == None:
        if debug_mode:
            print("\nError, no openingtype")
        return
        
    #main_search
    opening_type = game_vars["opening_type"]
    available_moves = []
    for opening in opening_type: 
        if debug_mode:
            print(opening_type[opening].name)
            
        opening = opening_type[opening].root
        next_move = opening
        selected_move = None
        #search
        for i in opening_moves:
            if i in next_move.children:
                if len(next_move.children) > 1:
                    next_move = next_move.children[random.choice(next_move.children)] #random opening variation
                else:
                    next_move = next_move.children[i]
                    selected_move = next_move
            else:
                selected_move = None
                next_move = None
                break
        
        if selected_move:
            available_moves.append(selected_move)
        
        if debug_mode:
            print("\nAvailable legal moves", available_moves)
    
    if len(available_moves) < 1: #didnt find any opening move
        return
    
    selected_move = random.choice(available_moves)
    
    if selected_move: #double check so it doesnt select a move already played.
        if selected_move.move == last_move:
            selected_move = None
            if debug_mode:
                print("chose last move!!")
        else:
            opening_moves.append(selected_move.move)
            
    return selected_move #selected uci move

def eval():
    pass
       
def run(last_move):
    move = None
    if game_vars["in_opening"]:
        time.sleep(0.25)
        
        move = main_opening_search(last_move)
        if not move:
            game_vars["in_opening"] = False
            
    #start engine
            
    return move#Returns a move

            
    #start engine
            
    return move#Returns a move
