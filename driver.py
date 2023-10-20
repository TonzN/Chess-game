import ui
import chess_lib as cl
import chess
import engine
import time
import opening_database
import timeit
#DEMO

window = ui.NewWindow()
window_size = (480,480)
window.reSizeScreen(window_size)
window.Target_fps = 60

screen = window.screen

board = chess.Board()
engine.game_vars["board"] = board

grid = ui.grid(window_size, 60)
grid.generate(screen)

game = cl.Game(screen)
game.setup(grid.grid, 60, False)
game.loadPawns()
game.loadPieces()
engine.game_vars["debug_move"] = False
engine.game_vars["game"] = game

select_layer = ui.RenderQueue()
run = True
selected_piece = None
new_turn = False

#backend game vars
move = None
player = True
promotion = False
enable_eval = True

promotion_table = {
    "queen": "q",
    "rook": "r",
    "knight": "n",
    "bishop": "b"
}
selected_promotion = False

while run:
    window.NextFrame([select_layer])
    if not player == board.turn:
        move = engine.run(game.last_move_uci, board)
        engine.transposition_table = {}
        if move:
            if board.is_check():
                engine.game_vars["is_check"] = True
            else:
                engine.game_vars["is_check"] = False
            uci_move = chess.Move.from_uci(move)
            game.capture(board, uci_move, move[2:4])
            game.en_passant(board, uci_move)

            if len(move) == 5:
                game.engine_promotion(board, move)
            else:
                game.move(move)

            game.last_move = move[:2]
            
            board.push(chess.Move.from_uci(move))   
            engine.played_moves.append(uci_move)
            game.last_move_uci = uci_move   
            move = None
            engine.pre_compute(board, -1)
            print("\nEngine eval", engine.eval(board), "Color:", board.turn)

            if board.is_repetition():
                print("repetition")
                ui.endPygame()
                        
            if board.is_stalemate():
                print("Stalemate")
                ui.endPygame()
            
            if board.is_checkmate():
                if board.turn:
                    print("Black won")
                else:
                    print("White won")
                    
                ui.endPygame()

    
    if window.leftclick() == True: #Select
        if selected_piece: 
            new_uci_pos = game.grid_pos_to_uci(game.round_to_grid(window.mousepos))
            new_pos = game.Positions[new_uci_pos]
            is_legal_move = False
            #Check if the move is legal
            legal_moves = list(board.legal_moves)
            for i in legal_moves:
                if selected_piece+new_uci_pos == str(i):
                    is_legal_move = True
                elif game.promoteable(board, new_uci_pos, game.pieces[selected_piece].piece_type):
                    is_legal_move = True
            
            if is_legal_move == True: 
                move = selected_piece+new_uci_pos  #assigns move   
                uci_move = chess.Move.from_uci(move)    
                #checks what kind of move you did
                game.capture(board, uci_move, new_uci_pos)
                game.en_passant(board, uci_move)          
                game.castle(board, uci_move)
                game.move(move)
                promotion_data = game.pawn_promotion(board, uci_move, move, game.pieces[new_uci_pos].piece_type)
                
                selected_piece = None
                select_layer.Queue = []
                if not promotion_data:
                    ui.MainRenderQueue.Push(game.pieces[new_uci_pos].img) #adds piece back to mainrenderqueue
                else:
                    promotion = promotion_data
                game.last_move = new_uci_pos
                game.last_move_uci = move
            
        elif not promotion:
            selected_piece = game.select_piece(window.mousepos)
        
        elif promotion:
            grid = promotion[0].grid
            for piece in range(4):
                if grid[piece][0].Click(True):
                    selected_promotion = [promotion_table[promotion[1][piece].piece_type], promotion[1][piece]]
                    
            if selected_promotion:
                promotion[0].delete_obj()
                for i in promotion[1]:
                    ui.MainRenderQueue.Remove(i.img)
    
    if window.rightclick() == True and selected_piece: #Deselect
        #Snapback piece to original position
        game.move_to_original_pos(selected_piece)
        select_layer.Pop()
        ui.MainRenderQueue.Push(game.pieces[selected_piece].img)
        
        selected_piece = None
         
    if selected_piece:
        if ui.LinearSearch(ui.MainRenderQueue.Queue, game.pieces[selected_piece].img):
            ui.MainRenderQueue.Remove(game.pieces[selected_piece].img)
            select_layer.Push(game.pieces[selected_piece].img)
        
        game.follow_cursor(selected_piece, window.mousepos)
    
    if selected_promotion:
        if board.turn:
            team = "white"
        else:
            team = "black"
        promotion_move = chess.Move.from_uci(game.last_move_uci+selected_promotion[0]) 
        board.push(promotion_move) 
        engine.played_moves.append(promotion_move)
        game.pieces[game.last_move] =  cl.Piece(team, selected_promotion[1].piece_type, game.last_move, game.Positions[game.last_move], screen)
        selected_promotion = None
        promotion = None
        move = None
        selected_piece = None
        select_layer.Queue = []
      
    if move and not promotion: #BACKEND 
        uci_move = chess.Move.from_uci(move)
        board.push(uci_move)
        engine.played_moves.append(uci_move)
        move = None
        
        if game.debugMode:
            print(board)
    
        white_material = engine.white_material
        black_material = engine.black_material
        print("\nWhite captured material {white} | Black captured material {black}".format(white = white_material, black = black_material))
        
        if white_material > black_material:
            print("\nWhite: +{advantage}".format(advantage=white_material-black_material))
        elif black_material > white_material:
            print("\nBlack: +{advantage}".format(advantage=black_material-white_material))
        
        print("\nWhite captured pieces: ", engine.white_captured_pieces)
        print("Black captured pieces: ", engine.black_captured_pieces)
        
        if enable_eval:
            team_legal_moves = []
            engine.pre_compute(board, -1)
            print("\nPlayer eval:", engine.eval(board), "Color:",board.turn)
           
        if board.is_repetition():
            print("repetition")
            ui.endPygame()
                        
        if board.is_stalemate():
            print("Stalemate")
            ui.endPygame()
        
        if board.is_checkmate():
            if board.turn:
                print("Black won")
            else:
                print("White won")
                
            ui.endPygame()

