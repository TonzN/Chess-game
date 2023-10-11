import ui
import math

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

def player(board):
    pass

class Piece():
    def __init__(self, team, piece_type, startpos, game_pos, screen):
        self.pos = startpos
        self.starting_pos = True
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
        #meta gamedata
        self.screen = screen

        self.Positions = {
        }

        self.pieces = {
        }
    
    def move(self, uci):
        new_uci = uci[2:]
        curr_uci = uci[:2]
        self.pieces[new_uci] = self.pieces[curr_uci]
        self.pieces[new_uci].img.pos = self.Positions[new_uci]
        del self.pieces[curr_uci]
        
    def capture(self, board, uci_move, new_uci_pos):
        if board.piece_at(uci_move.to_square):
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
            print("is castling")
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

    def loadPawns(self):
        #WhitePawns
        teams = ["white", "black"]
            
        for i in range(1,9):
            pos = files[i]+"2"
            self.pieces[pos] = Piece(teams[0], "pawn", pos, self.Positions[pos], self.screen)

        #BlackPawns
        for i in range(1,9):
            pos = files[i]+"7"
            self.pieces[pos] = Piece(teams[1], "pawn", pos, self.Positions[pos], self.screen)

    def loadPieces(self):
        teams = ["white", "black"]
            
        self.pieces[files[2]+"1"]  = Piece(teams[0], "knight", files[2]+"1", self.Positions[files[2]+"1"], self.screen)
        self.pieces[files[7]+"1"]  = Piece(teams[0], "knight", files[7]+"1", self.Positions[files[7]+"1"], self.screen)
        self.pieces[files[3]+"1"]  = Piece(teams[0], "bishop", files[3]+"1", self.Positions[files[3]+"1"], self.screen)
        self.pieces[files[6]+"1"]  = Piece(teams[0], "bishop", files[6]+"1", self.Positions[files[6]+"1"], self.screen)
        self.pieces[files[1]+"1"]  = Piece(teams[0], "rook", files[1]+"1", self.Positions[files[1]+"1"], self.screen)
        self.pieces[files[8]+"1"]  = Piece(teams[0], "rook", files[8]+"1", self.Positions[files[8]+"1"], self.screen)
        self.pieces[files[4]+"1"]  = Piece(teams[0], "queen", files[4]+"1", self.Positions[files[4]+"1"], self.screen)
        self.pieces[files[5]+"1"]  = Piece(teams[0], "king", files[5]+"1", self.Positions[files[5]+"1"], self.screen)
    

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
    
