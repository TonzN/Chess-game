import pygame
import math
import random
import time
import os
import numpy as np

Bools = {
    "CD": False
}

fps = pygame.time.Clock()

def LinearSearch(l, n):
    # l = list
    for i, v in enumerate(l):
        if v == n:
            return i
    return False

ScreenSize = None

def endPygame():
    pygame.quit()
    exit()

class Folder:
    def __init__(self):
        self.Objs = {}
        self.Size = len(self.Objs)
    def Clear(self):
        self.Objs = {}

class RenderQueue:
    def __init__(self, Queue=None):
        if Queue is None:
            Queue = []  # Create a new list if Queue is not provided
        self.Queue = Queue
    
    def Push(self, n):
        self.Queue.append(n)        
                    
    def add_queue(self, queue):
        for i in queue.Queue:
            self.Push(i)
    
    def Pop(self):
        if self.Queue:
          del self.Queue[0]
        
    def Remove(self, n):
        item = LinearSearch(self.Queue, n)
        if item:
            self.Queue.pop(item)
            
MainRenderQueue = RenderQueue()

class NewWindow:
    def __init__(self, Name = "MyGame", TargetFps = 60, BGColor = (60,60,60), Size = (800,600)):
        pygame.init()
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        self.screen = pygame.display.set_mode(Size)
        self.prev_time = time.time()
        self.Target_fps = TargetFps
        self.Size = Size
        self.CDdel = time.time()
        self.BGColor = BGColor
        self.mousepos = False
        self.Running = True
        pygame.display.set_caption(Name)
    
    def reSizeScreen(self, size):
        self.screen = pygame.display.set_mode(size)
        
    def RenderObjects(self, Layers = None):
        layer_queue = RenderQueue()
        for i in MainRenderQueue.Queue:
            i.Redraw()
        if Layers:
            for queue in Layers:
                layer_queue.add_queue(queue)
            for i in layer_queue.Queue:
                i.Redraw()
        
    def NextFrame(self, Layers = None):
        self.Running = EventHandler()
        self.mousepos = mouseP = pygame.mouse.get_pos()
        if self.Running == False:
           endPygame()
        
        self.screen.fill(self.BGColor)
        self.RenderObjects(Layers)
        pygame.display.flip()
        
      #  if time.time() - self.CDdel >= 0.05: 
       ##    Bools["CD"] = False
        #-------FPS--------#
        
        fps.tick(self.Target_fps)
       
    
    def rightclick(self):
        click  = pygame.mouse.get_pressed()
        if click[2] == 1 :
            if Bools["CD"] == False:
                Bools["CD"] = True
                return True
    
    def leftclick(self):
        click  = pygame.mouse.get_pressed()
        if click[0] == 1:
            if Bools["CD"] == False:
                Bools["CD"] = True
                return True

def runEvents(Objects = False): #Runs object functions. 
    #Objects er bare en array med alle objektene som har events so skal kjøres
    if Objects:
        for i in Objects:
            i.CheckEvents()

def EventHandler(): #Finder hendelser for vinduet
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            return False
        if e.type == pygame.MOUSEBUTTONUP:
            Bools["CD"] = False
            
    return True

class Rect:
    def __init__(self, screen, x, y, width, height, c1, c2 = False, Render = True): #innehold til en Ui
        self.pos     = [x,y]
        self.RQ = MainRenderQueue
        self.width  = width
        self.height = height
        self.c1     = c1
        self.c2     = c2
        self.Render = Render
        self.borderThickness = 1
        self.Border = False
        self.BorderColor = (200,200,200)
        self.screen = screen
        self.autoScale = False#AutoScale
        self.AddToRenderQueue(self.RQ)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        if Render:
            if self.autoScale:
                self.AutoScale()
            pygame.draw.rect(screen, c1, self.rect)

    def Click(self): #finner mus klikk op posisjonen returnerer True viss du klikker
        mouseP = pygame.mouse.get_pos()
        click  = pygame.mouse.get_pressed()
        if self.Render:
            if self.pos[0] + self.width > mouseP[0] > self.pos[0] and self.pos[1] + self.height > mouseP[1] > self.pos[1]:  
                # Hvis mus x og y kordnitaer er riktig/ peker på knappen
                pygame.draw.rect(self.screen, self.c1, (self.pos[0], self.pos[1], self.width, self.height))
                if click[0] == 1 and Bools["CD"] == False:
                    Bools["CD"] = True
                    return True
                return False

    def AutoScale(self): #In %
        self.width, self.height = (ScreenSize[0]/100)*self.width, (ScreenSize[1]/100)*self.height

    def Redraw(self):
       if self.Render:         
            pygame.draw.rect(self.screen, self.c1, (self.pos[0], self.pos[1], self.width, self.height))
            if self.Border:
                pygame.draw.rect(self.screen, self.BorderColor, self.rect, self.borderThickness)
    
    def AddText(self, tC, tT, tS):
        font = pygame.font.Font('freesansbold.ttf', tS) #font
        text = font.render(tT, self.Render, tC)
        textRect = text.get_rect()
        textRect.center = (self.pos[0] + (self.width // 2), self.pos[1] + (self.height // 2)) #plasserer teksten i midten
        self.screen.blit(text, textRect)

    def AddToRenderQueue(self, queue = MainRenderQueue):
        queue.Push(self)
    
    def Collision(self):
        pass

class Ball():
    def __init__(self, screen, x, y, radius, color1, Render = True):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color1
        self.Visible = Render
        self.Screen = screen
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    
    def AddToRenderQueue(self, RQ = MainRenderQueue):
        RQ.Push(self)
    
    def Redraw(self):
       # print(self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(self.Screen, self.color, (self.x, self.y), self.radius)
       
class TextLabel():
        #Info om varibaler
        #c1/c2 = color1/color2
        def __init__(self, screen, x, y, width, height, tC = None, tT = None, tS = None, Render = True):
            self.tC = tC #TextColor
            self.tS = tS #tSize
            self.width = width
            self.height = height
            self.pos = [x,y]
            self.screen = screen
            self.Render = Render
            self.tT = tT #tType
            MainRenderQueue.Push(self)

        def Redraw(self):
            if self.tT:
                font = pygame.font.Font('freesansbold.ttf', self.tS) #font
                text = font.render(self.tT, self.Render, self.tC)
                textRect = text.get_rect()
                textRect.center = (self.pos[0] + (self.width // 2), self.pos[1] + (self.height // 2)) #plasserer teksten i midten
                self.screen.blit(text, textRect)
    
class Button(Rect):
        def __init__(self,screen, x, y, width, height, c1, c2, Event = False, Input = False, Render = True):
            self.Event = Event #Hendelse etter du trykker
            self.Input = Input #Input = funksjon input
            super().__init__(screen, x, y, width, height, c1, c2, Render)

        def CheckEvents(self): #Methods Uten return
            hit = self.Click()
            MEvent = False
            if hit :
                MEvent = True
                if self.Event:
                    if self.Input:
                        self.Event(self.Input)
                    else:
                        self.Event()
          
        def runEvent(self, event, input = False):#Method som returner 
            Hit = self.Click()
            if Hit and event:
                Output = None
                if input:
                    Output = event(input)
                else:
                    Output = event()
                return Output
            else:
                return False

class Frame(Rect):
    def __init__(self,screen, x, y, width, height, c1 ):
        super().__init__(screen,x, y, width, height, c1)    

class image():
    def __init__(self, screen, img, pos, width = 60, height = 60):
        self.img = pygame.image.load(img)
        self.img = pygame.transform.scale(self.img, (width-2.5,height))
        self.size = [width, height]
        screen.blit(self.img, pos)
        self.screen = screen
        self.pos = pos
        MainRenderQueue.Push(self)

    def Redraw(self):
        self.screen.blit(self.img, self.pos)

class grid: 
    def __init__(self, size, cellsize, pattern = True):
        self.colors = [
            (255,255,255),
            (222,184,135)
        ]
        self.pattern = pattern
        self.cellSize = cellsize
        self.border = False 
        self.borderThickness = 2 
        self.spacing = 0 #spacing between each cell
        self.borderColor = (20,20,20)
        self._screenW = int(np.floor(size[0]/cellsize))
        self._screenH = int(np.floor(size[1]/cellsize))
        self._pos = np.zeros((self._screenW, self._screenH))
        self.renderqueue = MainRenderQueue
        self.rounded_edges = False
        self.render = True

        self.grid = [[] for i in range(int(np.floor(size[1]/cellsize)))] #makes the grid layout
        self.grid_data = {} # Data for grid management 

        self.colorHistory = [] 

        self.regionColorHistory = {}  #Access regions color history

    def generate(self, screen, type = "Button", textdata = None):
        for i in range(self._screenH):
            for z in range(self._screenW):
                color = self.colors[0]
                if (i+z)%2==0 and self.pattern == True: #makes checker patternsS
                    color = self.colors[1]

               #Type = Button
                block = Button(screen, z*self.cellSize + (1+z)*self.spacing, i*self.cellSize + (1+i)*self.spacing, self.cellSize, self.cellSize, color, color)
                block.Render = self.render
                if self.border:
                    block.Border = True
                    block.BorderColor = self.borderColor
                    block.borderThickness = self.borderThickness

                if self.rounded_edges:
                    block.rounded_edges = True
        
                if type == "TextButton":
                    block.AddText(textdata[0], textdata[1], textdata[2])

            
                self.grid[i].append(block)
    
    def colorRegion(self, region, colour): #For manually changing a region of colors
        for x in range(region[1][0], region[1][1]):
            for z in range(region[0][0], region[0][1]): #on the x axis
                self.grid[x][z].c1 = colour
        self.colorHistory.append(region)
    
    def colorBlock(self, pos, colour): #pos gotta be the indexes of the grid formated in a tuple
        self.grid[pos[1]][pos[0]].c1 = colour


    def refreshColours(self):
        for region in self.colorHistory:
          for x in range(region[1][0], region[1][1]): #Y axis
            for z in range(region[0][0], region[0][1]): #on the x axis
                self.grid[x][z].c1 = (self.colors[0])
        
        self.colorHistory = []
    
    def refreshRegion(self, region, oldColors = False): #refresh a region of cells region --> key 
        if not oldColors: #so you can revert to default colorS
            oldColors = (self.colors[0])
        for i in self.regionColorHistory[region]:
            self.grid[i[1]][i[0]].c1 = (oldColors) 
    
    def refreshBlock(self, pos):    
        self.grid[pos[1]][pos[0]].c1 = (self.colors[0])

    def get_zero_grid(self, fill = False):
        empty_grid = np.zeros((len(self.grid[0]), len(self.grid)))
                   
        return empty_grid
