import chess_lib as cl
import chess 
import opening_database
import time
import timeit
import random

engine_piece_values = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
    "k": 200
}

piece_values = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
}

game_vars = {
    "in_opening": True,
    "in_opening_book": True,
    "opening_move": None,
    "opening_type": None,
    "debug_mode": False,
    "game": None,
    "is_check": False,
    "pieces": [[],[]]
}

center = {
    "d4": 0.05,
    "d5": 0.05,
    "e4": 0.05,
    "e5": 0.05,
}

center_pawns_white = {}
center_pawns_black = {}
legal_piece_moves_white = {
    6: [],
    5: [],
    4: [],
    3: [],
    2: [],
    1: []
}
legal_piece_moves_black = {
    6: [],
    5: [],
    4: [],
    3: [],
    2: [],
    1: []
}

opening_moves = []
played_moves = []

white_material = 0
black_material = 0

white_captured_pieces = []
black_captured_pieces = []

cached_material_white = {}
cached_material_black = {}

knight_preffered_positions ={
    "d4": 0.2,
    "d5": 0.2,
    "e4": 0.2,
    "e5": 0.2,
    "f3": 0.1,
    "c3": 0.1,
    "f6": 0.1,
    "c6": 0.1
}

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

def material_count(board, team): #returns material for chosen team 
    material = 0
    for square, piece in board.piece_map().items():
        piece = str(piece)
        if piece is not None:
            if piece.isupper() and team == True:
                material += engine_piece_values[piece.lower()]
            elif piece.islower() and team == False:
                material += engine_piece_values[piece.lower()]
                
    return material

def pre_compute(board):
    for i in legal_piece_moves_white:
        legal_piece_moves_white[i] = []
        legal_piece_moves_black[i] = []
    
    original_turn = board.turn
    board.turn = True
    center_pawns_black = {}
    center_pawns_white = {}
    
    for move in list(board.legal_moves):
        piece = board.piece_at(move.from_square)
        move_uci = move.uci()
        legal_piece_moves_white[piece.piece_type].append(move_uci)
        if piece.piece_type == 1:
            if move_uci[:2] == "e4" or "e5" or "d5" or "d4":
                center_pawns_white[move_uci[:2]] = move_uci[:2]

    board.turn = False
    for move in list(board.legal_moves):
        piece = board.piece_at(move.from_square)
        move_uci = move.uci()
        legal_piece_moves_black[piece.piece_type].append(move_uci)
        if piece.piece_type == 1:
            if move_uci[:2] == "e4" or "e5" or "d5" or "d4":
                center_pawns_black[move_uci[:2]] = move_uci[:2]
    
    board.turn = original_turn
        
    
    #precomputes gamevars
    game_vars["pieces"] = [[],[]]
    for square, piece in board.piece_map().items():
        if piece.color == True:
            game_vars["pieces"][0].append(piece)
        else:
            game_vars["pieces"][1].append(piece) 
    
def mobility(board, team):
    mobility_score = 0
    legal_moves = legal_piece_moves_white
    center_pawn = center_pawns_white
    if team == False:
        legal_moves = legal_piece_moves_black
        center_pawn = center_pawns_black
                
    if game_vars["is_check"] == True:
        mobility_score -= 0.25
        
    #relative piece mobility score
    mobility_score += 0.01 * len(legal_moves[1]) + len(center_pawn) * 0.1
    mobility_score += 0.03 * len(legal_moves[2])
    for move in legal_moves[2]:
        if move[:2] in knight_preffered_positions:
            mobility_score += knight_preffered_positions[move[:2]]
            if move[2:] in center:
                mobility_score += center[move[2:]]
            
    mobility_score += 0.03 * len(legal_moves[3])
    if game_vars["in_opening"] == False:
        mobility_score += 0.035 * len(legal_moves[4])
        
    mobility_score += 0.045 * len(legal_moves[5])
   # mobility_score += 0.0 * legal_moves[6]
    
    return mobility_score
        
def eval(board):
    #get scores
    original_turn = board.turn
    len_pieces = len(game_vars["game"].pieces)
    material_white = 0
    material_black = 0
    
    #cached material 
    if not len_pieces in cached_material_white  or not len_pieces in cached_material_black:
        material_white = material_count(board, True)
        material_black = material_count(board, False)
        cached_material_white[len_pieces] = material_white
        cached_material_black[len_pieces] = material_black
    else:
        material_white = cached_material_white[len_pieces]
        material_black = cached_material_black[len_pieces]
     
    mobility_white = mobility(board,True)
    mobility_black = mobility(board, False)
    
    board.turn = original_turn
    
    #calculate
    who_2_move = 1
    if not board.turn: 
        who_2_move = -1
        
    material_score = material_white-material_black
    mobility_score = mobility_white-mobility_black
        
    Eval = (material_score+mobility_score)*who_2_move

    return Eval

def run(last_move, board):
    move = None
    pre_compute(board)
  #  time.sleep(0.25)
    
    if len(opening_moves) > 12:
        game_vars["in_opening"] = False
        
    if game_vars["in_opening_book"]:
        move = main_opening_search(last_move)
        if not move:
            game_vars["in_opening_book"] = False
        
    def code_to_time():
        #pre_compute(board)
        eval(board)
         
    time_taken = timeit.timeit(code_to_time, number=1)
    print("Elapsed time:", time_taken, "seconds")
    eval_score = eval(board) *-1 #no move has been pushed, flips

    #start engine
            
    return move#Returns a move
