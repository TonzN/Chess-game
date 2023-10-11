import ui
import chess_lib as cl
import chess
#DEMO

window = ui.NewWindow()
window_size = (480,480)
window.reSizeScreen(window_size)
window.Target_fps = 60

screen = window.screen

board = chess.Board()

grid = ui.grid(window_size, 60)
grid.generate(screen)

game = cl.Game(screen)
game.setup(grid.grid, 60, False)
game.loadPawns()
game.loadPieces()

select_layer = ui.RenderQueue()

run = True
selected_piece = None
new_turn = False

#backend game vars
move = None

while run:
    window.NextFrame([select_layer])
    
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
            
           if is_legal_move == True: 
                move = selected_piece+new_uci_pos  #assigns move   
                uci_move = chess.Move.from_uci(move)    
               
                #checks what kind of move you did
                game.capture(board, uci_move, new_uci_pos)
                game.en_passant(board, uci_move)          
                game.castle(board, uci_move)
                game.move(move)
                
                selected_piece = None
                select_layer.Queue = []
                ui.MainRenderQueue.Push(game.pieces[new_uci_pos].img) #adds piece back to mainrenderqueue
                game.last_move = new_uci_pos
            
        else:
            selected_piece = game.select_piece(window.mousepos)
    
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
        
    if move: #BACKEND
