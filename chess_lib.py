import ui
import math
import engine

white = "White"
black = "Black"

piecesimg = {
    "pawn":     ["chesspieces\WhitePawn.png", "chesspieces\BlackPawn.png"],
    "knight":   ["chesspieces\WhiteKnight.png", "chesspieces\BlackKnight.png"],
    "bishop":   ["chesspieces\WhiteBishop.png", "chesspieces\BlackBishop.png"],
    "rook":     ["chesspieces\WhiteRook.png", "chesspieces\BlackRook.png"],
    "queen":    ["chesspieces\WhiteQueen.png", "chesspieces\BlackQueen.png"],
    "king":     ["chesspieces\WhiteKing.png", "chesspieces\BlackKing.png"],
}

files = {
    1: "a",
    2: "b",
    3: "c",
    4: "d",
    5: "e",
    6: "f",
    7: "g",
    8: "h",
}
flipped_files = {value: key for key, value in files.items()}

class Piece():
    def __init__(self, team, piece_type, startpos, game_pos, screen):
        self.pos = startpos
        self.starting_pos = True
        self.piece_type = piece_type
        self.name = "{team}_{type}".format(type=piece_type,team=team)
        if team.lower() == "white":
            self.img = ui.image(screen, piecesimg[piece_type][0], list(game_pos))
        elif team.lower() == "black": #gives appropriate value 
            self.img = ui.image(screen, piecesimg[piece_type][1], list(game_pos))
        #print(self.team, self.val)

class Player:
    def __init__(self):
        self.team = None
        self.selected_piece = None

class Game:
    def __init__(self, screen):
        self.debugMode = False
        self.curr_plr = None    
        self.selected_piece = None 
        self.last_move = None
        self.last_move_uci = None
        #meta gamedata
        self.screen = screen

        self.Positions = {
        }

        self.pieces = {
        }
    
    def promoteable(self, board, target, piece_type):
        can_promote = False
        if piece_type == "pawn":
            if board.turn:
                if self.Positions[target][1] == 0:
                    if self.debugMode:
                        print("promotion time for white")
                    can_promote = True
                    
            else:
                if self.Positions[target][1] == 480:
                    if self.debugMode:
                        print("prmotion for black")
                    can_promote = True
        
        return can_promote
        
    def pawn_promotion(self, board, uci_move, move, piece_type):
        grid_pos = self.Positions[move[2:]]
        can_promote = False
        piece_img = []
        team = None
        if piece_type == "pawn":
            if board.turn and move[2:] in self.pieces:
                if self.pieces[move[2:]].img.pos[1] == 0:
                    if self.debugMode:
                        print("promotion time for white")
                    can_promote = True
                    team = "white"
                    
            elif move[2:] in self.pieces:
                if self.pieces[move[2:]].img.pos[1] == 480:
                    if self.debugMode:
                        print("prmotion for black")
                    can_promote = True
                    team = "black"

        if can_promote:
            choice_list = ui.grid((60, 240), 60, False)
            choice_list.border = True
            choice_list.borderThickness = 1
            choice_list.borderColor = (0,0,0)
            choice_list.generate_at((grid_pos[0], grid_pos[1]), self.screen)
            piece_img.append(Piece(team, "queen", None, choice_list.grid[0][0].pos, self.screen))
            piece_img.append(Piece(team, "rook", None, choice_list.grid[1][0].pos, self.screen))
            piece_img.append(Piece(team, "knight", None, choice_list.grid[2][0].pos, self.screen))
            piece_img.append(Piece(team, "bishop", None, choice_list.grid[3][0].pos, self.screen))
            
            return [choice_list, piece_img]
      #
    
    def move(self, uci):
        new_uci = uci[2:]
        curr_uci = uci[:2]
        self.pieces[new_uci] = self.pieces[curr_uci]
        self.pieces[new_uci].img.pos = self.Positions[new_uci]
        self.pieces[new_uci].pos = curr_uci
        print(self.pieces[new_uci].pos)
        self.pieces[new_uci].game_pos = self.Positions[new_uci]
        del self.pieces[curr_uci]
    
    def capture(self, board, uci_move, new_uci_pos):
        if board.piece_at(uci_move.to_square):
            piece_type = self.pieces[new_uci_pos].piece_type
            if board.turn:           
                engine.white_material += engine.piece_values[piece_type]
                engine.white_captured_pieces.append(piece_type)
            else:
                engine.black_material += engine.piece_values[piece_type]
                engine.black_captured_pieces.append(piece_type)
                
            ui.MainRenderQueue.Remove(self.pieces[new_uci_pos].img)
            del self.pieces[new_uci_pos]
            
    def en_passant(self, board, uci):
        if board.is_en_passant(uci):
            ui.MainRenderQueue.Remove(self.pieces[self.last_move].img)
     
    def castle(self, board, uci_move):
        if board.is_castling(uci_move):
            new_file = flipped_files[str(uci_move)[2]]
            curr_file = flipped_files[str(uci_move)[0]]
            #castling dir
            if new_file > curr_file: #kingside
                if board.turn:
                    self.move("h1f1")
                else:
                    self.move("h8f8")
            else: #queenside
                if board.turn:
                    self.move("a1d1")
                else:
                    self.move("a8d8")
            
    def grid_pos_to_uci(self, pos):
        if self.flipped_board:
            x = pos[1]
            file = files[9-pos[0]]
        else:
            x = 9-pos[1]
            file = files[pos[0]]
            
        return "{file}{x}".format(file = file, x=x)

    def uci_to_grid_pos(self, uci):
        if uci[0] in flipped_files:
            idx = flipped_files[uci[0]]
            x = abs(int(uci[1])-9)
            if self.flipped_board:
                x = 9-int(uci[1])
            return (idx,x) 
        else:
            print("incompatible syntax")
    
    def move_to_original_pos(self, uci_pos):
        img = self.pieces[uci_pos].img
        img.pos = self.Positions[uci_pos]
        
    def round_to_grid(self, pos):
        return (math.floor(pos[0]/60)+1, math.floor(pos[1]/60)+1) 
    
    def select_piece(self, pos):
        grid_pos = self.round_to_grid(pos) #rounds to nearest cell
        uci_pos = self.grid_pos_to_uci(grid_pos)
        
        if uci_pos in self.pieces:
            if self.debugMode:
                print(self.pieces[uci_pos].name, pos, grid_pos, uci_pos)
            self.selected_piece = self.pieces[uci_pos]
            return uci_pos
    
    def follow_cursor(self, uci_pos, mouse_pos):
        img = self.pieces[uci_pos].img
        img.pos = list(mouse_pos)
        img.pos[0] -= img.size[0]/2 
        img.pos[1] -= img.size[1]/2 
    
    def setup(self, grid, cellsize, flipped_board=False):
        self.flipped_board = flipped_board
        grid_len = len(grid)
        for column in range(grid_len):
            for row in range(grid_len):
                if not self.flipped_board:
                    self.Positions[files[row+1]+str(column+1)] = (row*cellsize, (grid_len-1-column)*cellsize) # Access positions with chess syntax
                else:
                    self.Positions[files[row+1]+str(column+1)] = ((7-row)*cellsize, (column)*cellsize)
        if self.debugMode == True:
            print(self.Positions)
            print("Successfully loaded gameboard")

    def loadPawns(self, load_white=True, load_black=True):
        #WhitePawns
        teams = ["white", "black"]
        
        if load_white:
            for i in range(1,9):
                pos = files[i]+"2"
                self.pieces[pos] = Piece(teams[0], "pawn", pos, self.Positions[pos], self.screen)

        if load_black:
            #BlackPawns
            for i in range(1,9):
                pos = files[i]+"7"
                self.pieces[pos] = Piece(teams[1], "pawn", pos, self.Positions[pos], self.screen)

    def loadPieces(self, load_white=True, load_black=True):
        teams = ["white", "black"]
        
        if load_white:
            self.pieces[files[2]+"1"]  = Piece(teams[0], "knight", files[2]+"1", self.Positions[files[2]+"1"], self.screen)
            self.pieces[files[7]+"1"]  = Piece(teams[0], "knight", files[7]+"1", self.Positions[files[7]+"1"], self.screen)
            self.pieces[files[3]+"1"]  = Piece(teams[0], "bishop", files[3]+"1", self.Positions[files[3]+"1"], self.screen)
            self.pieces[files[6]+"1"]  = Piece(teams[0], "bishop", files[6]+"1", self.Positions[files[6]+"1"], self.screen)
            self.pieces[files[1]+"1"]  = Piece(teams[0], "rook", files[1]+"1", self.Positions[files[1]+"1"], self.screen)
            self.pieces[files[8]+"1"]  = Piece(teams[0], "rook", files[8]+"1", self.Positions[files[8]+"1"], self.screen)
            self.pieces[files[4]+"1"]  = Piece(teams[0], "queen", files[4]+"1", self.Positions[files[4]+"1"], self.screen)
            self.pieces[files[5]+"1"]  = Piece(teams[0], "king", files[5]+"1", self.Positions[files[5]+"1"], self.screen)
    
        if load_black:
            self.pieces[files[2]+ "8"]  = Piece(teams[1], "knight", files[2]+"8", self.Positions[files[2]+"8"], self.screen)
            self.pieces[files[7]+ "8"]  = Piece(teams[1], "knight", files[7]+"8", self.Positions[files[7]+"8"], self.screen)
            self.pieces[files[3]+ "8"]  = Piece(teams[1], "bishop", files[3]+"8", self.Positions[files[3]+"8"], self.screen)
            self.pieces[files[6]+ "8"]  = Piece(teams[1], "bishop", files[6]+"8", self.Positions[files[6]+"8"], self.screen)
            self.pieces[files[1]+ "8"]  = Piece(teams[1], "rook", files[1]+"8", self.Positions[files[1]+"8"], self.screen) 
            self.pieces[files[8]+ "8"]  = Piece(teams[1], "rook", files[8]+"8", self.Positions[files[8]+"8"], self.screen)
            self.pieces[files[4]+ "8"]  = Piece(teams[1], "queen", files[4]+"8", self.Positions[files[4]+"8"], self.screen)
            self.pieces[files[5]+ "8"]  = Piece(teams[1], "king", files[5]+"8", self.Positions[files[5]+"8"], self.screen)
        
    def loadGame(self):
        self.loadPawns()
        if self.debugMode == True:
            print("Successfully loaded pawns")
        self.loadPieces()
        if self.debugMode == True:
            print("Successfully loaded pieces")
    
