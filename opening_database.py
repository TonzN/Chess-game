import chess_lib

class Node:
    def __init__(self, move, piece_type = ""):
        self.move = move
        self.values = {
            "description": {"open_game": True}   
        }
        self.children = {}
        self.piece_type = piece_type
        
    def print_tree(self, depth=0):
        indentation = "  " * depth
        print(f"{indentation}{self.move} {self.piece_type}{self.move[2:]}")
        for child in self.children.values():
            child.print_tree(depth + 1)

class Tree:
    def __init__(self, move):
        self.root = Node(move)

##################################||||RUY LOPEZ||||#############################################33
Ruy_lopez = Tree("e2e4")
Ruy_lopez.root.children["e2e4"] = Node("e7e5")
Ruy_lopez.root.children["e2e4"].children["e7e5"] = Node("g1f3", "Kn")
Ruy_lopez.root.children["e2e4"].children["e7e5"].children["g1f3"] = Node("b8c6", "Kn")
Ruy_lopez.root.children["e2e4"].children["e7e5"].children["g1f3"].children["b8c6"] = Node("f1b5", "B")
Ruy_lopez_position = Ruy_lopez.root.children["e2e4"].children["e7e5"].children["g1f3"].children["b8c6"] 

##################################||||Vienna game||||#############################################
vienna_game = Tree("e2e4")
vienna_game.root.children["e2e4"] = Node("e7e5")
vienna_game.root.children["e2e4"].children["e7e5"] = Node("b1c3", "Kn")
vienna_game.root.children["e2e4"].children["e7e5"].children["b1c3"] = Node("g8f6", "Kn")
vienna_game.root.children["e2e4"].children["e7e5"].children["b1c3"].children["g8f6"] = Node("f2f4")
vienna_game.root.children["e2e4"].children["e7e5"].children["b1c3"].children["g8f6"].children["f2f4"] = Node("d7d5")
vienna_game = vienna_game.root.children["e2e4"].children["e7e5"].children["b1c3"].children["g8f6"]

################################||||Queens gambit||||###############################################
queens_gambit = Tree("d2d4")
queens_gambit.root.children["d2d4"] = Node("d7d5")
queens_gambit.root.children["d2d4"].children["d7d5"] = Node("c2c4")
#queens_gambit.root.children["e2e4"].children["e7e5"].children["b1c3"] = Node("g8f6", "Kn")

queens_gambit = queens_gambit.root.children["d2d4"].children["d7d5"]
