from tkinter import *
from tkinter import ttk
from aStarFinal import * 
import pygame
import math
import os
import time

class Context:
    def __init__(self,gridScale,windowDimensions,entities,Map,Grid):
        self.gridScale = gridScale 
        self.windowX = windowDimensions[0]
        self.windowY = windowDimensions[1]
        self.states = {'startSim':False,'pauseSim':False,'stopSim':False,'setStart':False,'setTarget':False,'placeWalls':False,'removeWalls':False,'pathDone':False,'pathActive':False,'allowDiagonals':False}
        self.MapState = Map
        self.GridState = Grid
        self.entityPositions = {}
        self.entityMap = {}
        self.entities = entities
        for i in self.entities:
            self.entityMap[i.tag] = i 
            self.entityPositions[i.getEntityid()] = i.getComponent('transform').position
    
    def getSaveState(self):
        stateString = ""
         
        if(self.MapState == None or self.GridState == None):
            print("Map or grid state is null!")
            return
        
        elif(self.MapState != None and self.GridState != None and self.entityPositions != {}):
            stateString += "gridScale-"
            stateString += str(self.gridScale) + "\n"
            
            stateString += "mapstate-"
            for i in self.MapState.getObstacles():
                stateString += str(i[0])+":"+str(i[1])+","
            stateString = stateString[:-1]
            stateString += "\n"
            
            stateString += "gridstate-"
            for i in self.GridState.getObstacles():
                stateString += str(i[0])+":"+str(i[1])+","
            stateString = stateString[:-1]
            stateString += "\n"
            
            stateString += "entitypositions-"
            for i,j in self.entityPositions.items():
                stateString += str(i)+":"+str(j[0])+","+str(j[1])+"|"
            stateString = stateString[:-1]
            stateString += "\n"
             
        print("Final statestring: ",stateString)
        return stateString

    def resizeMap(self,gridScale):
        #resize - entity meshes, grid and map
        if(self.MapState.getObstacles() != [] and self.GridState.getObstacles() != []):
            Console.log("Clear obstacles before resizing grid",'warning')
            return

        self.gridScale = gridScale
        self.MapState.resize(gridScale)
        self.GridState.resize(gridScale)
        for i in self.entities:
            i.getComponent('mesh').setSize((gridScale,gridScale))
            position = i.getComponent('transform').position
            newPosition = [position[0]//self.gridScale*self.gridScale,position[1]//self.gridScale*self.gridScale]
            i.getComponent('transform').setPosition(newPosition)
        Console.log("Map resized to : "+str(gridScale)+" grid units",'operation')
  
    def getWindowX(self):
        return self.windowX

    def getWindowY(self):
        return self.windowY
    
    def getAppStates(self):
        return self.states
    
    def getEntities(self):
        return self.entities
    
    def getMapState(self):
        return self.MapState
    
    def getGridState(self):
        return self.GridState

    def getGridScale(self):
        return self.gridScale

    def getEntityByTag(self,tag):
        if(tag in self.entityMap.keys()):
            return self.entityMap[tag]
        
    def setAppState(self,stateType,value):
        if(stateType in self.states.keys() and value in [True,False]):
            self.states[stateType] = value
        else:
            print("state type or value not valid!")

    def allowDiagonals(self):
        return self.states['allowDiagonals']
    
    def isPauseSim(self):
        return self.states['pauseSim']
    
    def isStopSim(self):
        return self.states['stopSim']
    
    def isStartSim(self):
        return self.states['startSim']
    
    def isSetStart(self):
        return self.states['setStart']
    
    def isSetTarget(self):
        return self.states['setTarget']
    
    def isPlaceWalls(self):
        return self.states['placeWalls']

    def isRemoveWalls(self):
        return self.states['removeWalls']
    
    def isPathActive(self):
        return self.states['pathActive']
    
    def isPathDone(self):
        return self.states['pathDone']

    
class Console:
    consoleRef = None
    
    def setConsole(UIConsole):
        Console.consoleRef = UIConsole
        Console.consoleRef.tag_config('warning',foreground = 'orange')
        Console.consoleRef.tag_config('error',foreground = 'red')
        Console.consoleRef.tag_config('success',foreground = 'lawn green')
        Console.consoleRef.tag_config('operation',foreground = 'white')

    def clear():
        if(Console.consoleRef != None):
            Console.consoleRef.configure(state = NORMAL)
            Console.consoleRef.delete(1.0,END)
            Console.consoleRef.configure(state = DISABLED)
            
    def log(text,logType):
        logtext = ">> "
    
        if(logType == 'warning'):
            logtext += text + " !\n"
        elif(logType == 'error'):
            logtext += text + " !!\n"
        elif(logType == 'success'):
            logtext += text + ".\n"
        elif(logType == 'operation'):
            logtext += text + "...\n"

        Console.consoleRef.configure(state = NORMAL)
        Console.consoleRef.insert(END,logtext,logType)
        Console.consoleRef.configure(state = DISABLED)
        Console.consoleRef.see("end")
        
#--------------------COMPONENTS-------------------------------------#
class ComponentBase:
    def __init__(self):
        self.type = 'base'
        
class TransformComponent(ComponentBase):
    def __init__(self,position = (0,0)):
        ComponentBase.__init__(self)
        self.type = "transform"
        self.position = position

    def setPosition(self,newPosition):
        self.position = newPosition
        
    def translate(self,translation):
        self.position = (self.position[0] + translation[0],self.position[1] + translation[1])
        
    def rotate(self, amount):
        pass
      
    def scale(self, amount):
        pass
 
class Mesh(ComponentBase):
    def __init__(self,meshType="square",color=(255,0,0),size=(0,0)):
        self.type = meshType
        self.size = size
        self.original = color
        self.color = self.original 
        self.hoverColor = (100,100,100)
        
    def setSize(self,newSize):
        self.size = newSize

class CollisionComponent(ComponentBase):
    def __init__(self,meshTop,meshRight,meshLeft,meshBottom):
        self.type = "collision"
        self.top = meshTop
        self.right = meshRight
        self.left = meshLeft
        self.bottom = meshRight


class AIComponent(ComponentBase):
    def __init__(self):
        self.type = "AI"
        self.goalType = "pathfinding"
        self.TargetEntity = None
        self.start = None
        self.target = None
        self.path = []
        self.findPath = False
    
    def findNext(self):
        #and self.findPath
        if(self.path  == []):
            return True
        return False

    def findPath(self,val):
        if(val in [True,False]):
            self.findPath = val
        
#--------------------COMPONENTS-------------------------------------#
    

#---------------------ENTITIES--------------------------------------#
        
class EntityBase:
    def __init__(self,entityId):
        self.componentList = []
        self.entityId = entityId
        self.tag = "base"
    def getEntityId(self):
        return self.entityId

class PlayerEntity(EntityBase):
    def __init__(self,entityId):
        EntityBase.__init__(self,entityId)
        self.tag = "firstPlayer"

    def addComponent(self,componentType):
        ComponentManager.addComponent(self.entityId,componentType)
        
    def removeComponent(self,componentType):
        ComponentManager.removeComponent(self.entityId, componentType)
        print("removed component: ",componentType)
    
    def hasComponent(self,componentType):
        if(ComponentManager.has(self.entityId,componentType)):
            return True
        return False
    def getEntityid(self):
        return self.entityId
    
    def getComponent(self,componentType):
        return ComponentManager.getComponent(self.entityId,componentType)

#---------------------ENTITIES--------------------------------------#


#-----------------------SYSTEMS-------------------------------------#
class systemBase:
    def __init__(self):
        self.type = "system"
        
    def update(self):
        pass
        
#pathfinder
class AISystem(systemBase):
    def __init__(self,context):
        systemBase.__init__(self)
        self.type = "AI"
        self.currentTarget = None
        self.counter = 0
        self.path = []
        self.delayAmount = 0.2
        self.target = None
        self.context = context
        self.currentTile = None

    def update(self):
        for i in self.context.getEntities():
            if(i.hasComponent("aiComponent") and i.getComponent("aiComponent").goalType == "pathfinding"):
                
                if(i.getComponent("aiComponent").findNext()):
                    
                    aiComp = i.getComponent("aiComponent")
                    self.target = i.getComponent('aiComponent').target
                    
                    startTime = time.time()
                    aiComp.path = self.findPath(aiComp.start,aiComp.target,self.context.getMapState().getNodes())
                    endTime = time.time()
                    elapsed = endTime - startTime
                    
                    if(aiComp.path == -1):
                        aiComp.path = []
                        Console.log("Path does not exit (maybe remove some walls)",'error')
                        self.context.setAppState('startSim',False)
                        return
                    
                    Console.log("Astar finished execution in: "+str(elapsed),'success')
                    Console.log("Path found : "+str(aiComp.path),'success')
                    self.path = aiComp.path
                    self.context.setAppState('pathActive',True)
                    self.context.getGridState().setPathColor(self.path)
                    Console.log("following path",'operation')
                
                else:
                    self.followPath(self.context.getEntityByTag(i.tag),self.context.getGridState())
               
                        
                        
    def followPath(self,entity,grid):
        if(self.path != []):
            entityPos = entity.getComponent('transform').position

            #if the simulation is stopped
            if(self.context.isStopSim()):
                grid.setPathColor(self.path,grid.exitColor)
                entity.getComponent('aiComponent').path = []
                self.path = []
                self.counter =0  
                Console.log("Simulation stopped",'warning')
                self.context.setAppState('stopSim',False)
                self.context.setAppState('startSim',False)
                return
                
            #if the target position has changed then 
            if(self.target != None and self.target != entity.getComponent('aiComponent').target):
                Console.log("target position has changed",'warning')
                grid.setPathColor(self.path,grid.exitColor)
                self.path = []
                self.counter = 0
                entity.getComponent('aiComponent').path = []
                return

            #if target position has been reached 
            if(entityPos == [self.path[-1][0] * grid.dimension[0] ,self.path[-1][1]*grid.dimension[1]]):
                entity.getComponent("aiComponent").path = []
                grid.setPathColor(self.path,grid.exitColor)
                self.path = []
                self.counter = 0
                self.context.setAppState('startSim',False)
                self.context.setAppState('pathActive',False)
                Console.log("Path complete",'success')
                return
            
            if(self.currentTile != None):
                grid.tileColors[grid.tileMap[str(self.currentTile)]] = (255,0,0)

            self.currentTarget = self.path[self.counter]
            entityPosition = [self.currentTarget[0]*grid.dimension[0],self.currentTarget[1]*grid.dimension[1]]
            self.currentTile = entityPosition
            entity.getComponent('transform').setPosition(entityPosition)
            grid.tileColors[grid.tileMap[str(entityPosition)]] = (0,255,0)

            self.counter +=1 
            time.sleep(self.delayAmount)
    
    def findPath(self,start,target,nodes):
        Console.log("Finding path",'operation')
        path = astar(nodes,start,target,self.context.allowDiagonals())  #self.context.allowDiagonals()
        return path
        
class WindowSystem(systemBase):
    def __init__(self,context):
        systemBase.__init__(self)
        self.type = 'window'
        pygame.init()
        self.screenWidth = context.getWindowX()
        self.screenHeight = context.getWindowY()
        self.screen = pygame.display.set_mode((self.screenWidth,self.screenHeight))
        self.clock = pygame.time.Clock()
        self.translationDir = "right"
        self.backgroundColor = (213, 223, 242)
        self.mouseX= None
        self.mouseY = None
        self.mouseDown = False
        self.context = context

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEMOTION:
                self.mouseX = event.pos[0]
                self.mouseY = event.pos[1]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseDown = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseDown = False

    def update(self):
        self.processInput()
        self.drawEntities()
        self.handleEvents()
        self.swapBuffer()
        
        
    def drawEntities(self):
        self.screen.fill(self.backgroundColor)
        for i in self.context.getEntities():
            if(self.mouseOnPos(i.getComponent("transform").position,self.context.getGridScale()) and not self.context.isStartSim()):
                i.getComponent('mesh').color = i.getComponent('mesh').hoverColor
            else:
                i.getComponent('mesh').color = i.getComponent('mesh').original
            if(i.hasComponent("transform") and i.hasComponent("mesh")):
                pygame.draw.rect(self.screen,i.getComponent("mesh").color, tuple(i.getComponent("transform").position) + i.getComponent("mesh").size)
        self.context.getGridState().draw(self.screen)


    def handleEvents(self):
        startEntity = self.context.getEntityByTag('aiControlled')
        targetEntity = self.context.getEntityByTag('targetEntity')

        pos = [self.mouseX//self.context.getGridScale()*self.context.getGridScale(),self.mouseY//self.context.getGridScale()*self.context.getGridScale()]
                
        if(self.mouseX <= self.screenWidth and self.mouseY <= self.screenHeight):
            self.context.getGridState().onHoverTileColor(pos,self.context.getGridState().hoverColor)
        
        if(self.context.isSetStart() and self.mouseDown):
            startEntity.getComponent('transform').setPosition(pos)
            Console.log("Start placed at : "+str(pos),'success')
            
        elif(self.context.isSetTarget() and self.mouseDown):
            targetEntity.getComponent('transform').setPosition(pos)
            Console.log("Target placed at : "+str(pos),'success')

        elif(self.context.isPlaceWalls() and self.mouseDown ):
            if(self.context.isRemoveWalls()):
                Console.log('Disable remove walls before placing','warning')
                return
            if(pos == list(startEntity.getComponent('transform').position) or pos == list(targetEntity.getComponent('transform').position)):
                Console.log("Cannot place wall over entity",'warning')
                return
            self.context.getMapState().addObstacle(pos)
            self.context.getGridState().addObstacle(pos)
            Console.log("Wall placed at: "+str(pos), 'success')
            
        elif(self.context.isRemoveWalls() and self.mouseDown):
            if(self.context.isPlaceWalls()):
                Console.log('Disable place walls before removing','warning')
                return
            if(pos in self.context.getGridState().obstacles):
                self.context.getMapState().removeObstacle(pos)
                self.context.getGridState().removeObstacle(pos)
                Console.log("Wall removed from : "+str(pos),'success') 
        
    def mouseOnPos(self,entityPos,gridScale):
        if(self.mouseX >= entityPos[0] and self.mouseX <= entityPos[0] + gridScale and self.mouseY >= entityPos[1] and self.mouseY <= entityPos[1] + gridScale):
            return True
        return False
        
    def swapBuffer(self):
        self.clock.tick(120)
        pygame.display.flip()

class UISystem(systemBase):
    def __init__(self,context):
        systemBase.__init__(self)
        self.type = 'UI'
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.title("Pathfinder")
        self.context = context
        
        self.embedFrame = Frame(self.root,width = 600, height= 600)
        self.embedFrame.grid(columnspan = 600 , rowspan = 500)
        self.embedFrame.pack(side = LEFT)
        
        os.environ['SDL_WINDOWID'] = str(self.embedFrame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        def _from_rgb(rgb):
            """translates an rgb tuple of int to a tkinter friendly color code
            """
            return "#%02x%02x%02x" % rgb

        self.backgroundColor = _from_rgb((69, 76, 89))
        self.buttonColor = _from_rgb((88, 96, 112))
        self.buttonHoverColor = "light steel blue"
        self.buttonFont = ('helvetica',9,'bold')
        self.buttonText = "white smoke"
        self.labelText = _from_rgb((242, 247, 255)) 
        self.labelFrameFont = ('helvetica',10,'bold')
        self.labelfont = ('helvetica', 9)
        self.entryColor = _from_rgb((135, 145, 161))
        
        
        #'mint cream'
        self.rootFrame = Frame(self.root,width = 200,height = 500)
        self.rootFrame.pack(side = TOP)
        self.root.configure(bg = self.backgroundColor)
        self.rootFrame.configure(bg = self.backgroundColor)
        
        self.buttonPadX = 20
        self.buttonPadY = 10
        
        def startSimulation():
            self.context.setAppState('startSim',True)
            if(self.context.isPauseSim()):
                self.context.setAppState('pauseSim',False)
            
        def pauseSim():
            if(self.context.isStartSim()):
                Console.log('Simulation paused (press start to resume)','warning')
                self.context.setAppState('pauseSim',True)
                self.context.setAppState('startSim',False)

        def stopSim():
            if(self.context.isStartSim()):
                self.context.setAppState('stopSim',True)
            else:
                return

        def setStartLocation():
            if(not self.context.isSetStart()):
                self.context.setAppState('setStart',True)
                self.placeTarget.configure(state = DISABLED)
                self.placeWalls.configure(state = DISABLED)
                self.rmWalls.configure(state = DISABLED)
            else:
                self.context.setAppState('setStart',False)
                self.placeTarget.configure(state = NORMAL)
                self.placeWalls.configure(state = NORMAL)
                self.rmWalls.configure(state = NORMAL)
                
        def setTargetLocation():
            if(not self.context.isSetTarget()):
                self.context.setAppState('setTarget',True)
                self.placeStart.configure(state = DISABLED)
                self.placeWalls.configure(state = DISABLED)
                self.rmWalls.configure(state = DISABLED)
            else:
                self.context.setAppState('setTarget',False)
                self.placeStart.configure(state = NORMAL)
                self.placeWalls.configure(state = NORMAL)
                self.rmWalls.configure(state = NORMAL)
                
        def setRemoveWalls():
            if(not self.context.isRemoveWalls()):
                self.context.setAppState('removeWalls',True)
                Console.log("Remove walls active",'success')
                self.placeStart.configure(state = DISABLED)
                self.placeTarget.configure(state = DISABLED)
                self.placeWalls.configure(state = DISABLED)
            else:
                self.context.setAppState('removeWalls',False)
                Console.log("Remove walls disabled",'warning')
                self.placeStart.configure(state = NORMAL)
                self.placeTarget.configure(state = NORMAL)
                self.placeWalls.configure(state = NORMAL)
                
        def setPlaceWalls():
            if(not self.context.isPlaceWalls()):
                self.context.setAppState('placeWalls',True)
                Console.log("Place walls active",'success')
                self.placeStart.configure(state = DISABLED)
                self.placeTarget.configure(state = DISABLED)
                self.rmWalls.configure(state = DISABLED)
                
            else:
                self.context.setAppState('placeWalls',False)
                Console.log("Place walls disabled",'warning')
                self.placeStart.configure(state = NORMAL)
                self.placeTarget.configure(state = NORMAL)
                self.rmWalls.configure(state = NORMAL)
                
                
        def onHover(button):
            button.configure(bg = self.buttonHoverColor)

        def onLeave(button):
            button.configure(bg = self.buttonColor)

        def clearObstacles():
            if(not self.context.isStartSim()):
                self.context.getGridState().clearObstacles()
                self.context.getMapState().clearObstacles()
                Console.log("Obstacles cleared",'success')

        def saveToFile(filePath):
            if(filePath != "" or filePath != None):
                SaveSystem.saveState(filePath,self.context)
                
                

        def loadFromFile(filePath):
            if(filePath != "" or filePath != None):
                SaveSystem.loadStateFromFile(filePath,self.context)
                
                
        def resizeMap(newSize):
            self.context.resizeMap(newSize)
        
        self.labelFrame1 = LabelFrame(self.rootFrame,text= "Controls:",padx = 10,pady = 10,fg=self.labelText,relief=FLAT,highlightbackground ="gray", highlightthickness=0.5)
        self.labelFrame1.pack()
        self.labelFrame1.configure(bg = self.backgroundColor)
        self.labelFrame1.configure(font = self.labelFrameFont)
        
        self.buttonFrame = Frame(self.labelFrame1)
        self.startButton = Button(self.buttonFrame,text = "START",relief =FLAT,border ="0",command = startSimulation,padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg =self.buttonColor)
        self.startButton.pack(side= LEFT)
        self.startButton.bind('<Enter>',lambda a : onHover(self.startButton))
        self.startButton.bind('<Leave>',lambda a : onLeave(self.startButton))
        self.startButton.configure(font = self.buttonFont)
        self.pauseButton = Button(self.buttonFrame,text = "PAUSE",relief =FLAT,border ="0",command = pauseSim,padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg = self.buttonColor)
        self.pauseButton.pack(side= LEFT)
        self.pauseButton.bind('<Enter>',lambda a : onHover(self.pauseButton))
        self.pauseButton.bind('<Leave>',lambda a : onLeave(self.pauseButton))
        self.pauseButton.configure(font = self.buttonFont)
        self.stopButton = Button(self.buttonFrame,text = "STOP",relief =FLAT,border ="0",command = stopSim,padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg = self.buttonColor)
        self.stopButton.pack(side= LEFT)
        self.stopButton.bind('<Enter>',lambda a : onHover(self.stopButton))
        self.stopButton.bind('<Leave>',lambda a : onLeave(self.stopButton))
        self.stopButton.configure(font = self.buttonFont)
        self.buttonFrame.pack(side = TOP)
    
        self.checkBoxFrame = Frame(self.labelFrame1,pady = 0,bg = self.backgroundColor)
        self.allowLabel = Label(self.checkBoxFrame,text="Allow diagonal movement: ",fg = self.labelText,bg = self.backgroundColor)
        self.allowLabel.pack(side = LEFT)
        self.allow = IntVar()
        self.allowDiagonals = Checkbutton(self.checkBoxFrame,bg = self.backgroundColor,variable=self.allow,activeforeground='black',activebackground=self.backgroundColor,onvalue = 1, offvalue = 0)
        self.allowDiagonals.pack(side = LEFT)
        self.checkBoxFrame.pack(side = BOTTOM)
        
        
        self.clearButton = Button(self.buttonFrame,text="CLEAR",relief =FLAT,border ="0",padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg = self.buttonColor,command= clearObstacles)
        self.clearButton.pack(side=LEFT)
        self.clearButton.bind('<Enter>',lambda a: onHover(self.clearButton))
        self.clearButton.bind('<Leave>',lambda a: onLeave(self.clearButton))
        self.clearButton.configure(font = self.buttonFont)
        self.buttonFrame.pack(side= TOP)
        self.buttonFrame.configure(bg = self.backgroundColor)

        self.settings = LabelFrame(self.rootFrame,text = "Settings:",padx=10,pady=10,fg=self.labelText,relief=FLAT,highlightbackground ="gray", highlightthickness=0.5)
        self.settings.pack()
        self.settings.configure(bg = self.backgroundColor)
        self.settings.configure(font = self.labelFrameFont)
        
  
        self.startAndTarget = Label(self.settings,text = "Start and target: ",bg=self.backgroundColor,fg=self.labelText)
        self.startAndTarget.configure(font = self.labelfont)
        self.startAndTarget.grid(row=0,column=0)
        self.placeStart = Button(self.settings, text= "Place start" ,relief =FLAT,border ="0",command = setStartLocation,padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg =self.buttonColor)
        self.placeStart.grid(row=0,column=1)
        self.placeStart.bind('<Enter>',lambda a : onHover(self.placeStart))
        self.placeStart.bind('<Leave>',lambda a : onLeave(self.placeStart))
        self.placeStart.configure(font = self.buttonFont)
        self.placeTarget = Button(self.settings, text= "Place target" ,relief =FLAT,border ="0",command = setTargetLocation,padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg =self.buttonColor)
        self.placeTarget.grid(row=0,column=2)
        self.placeTarget.bind('<Enter>',lambda a : onHover(self.placeTarget))
        self.placeTarget.bind('<Leave>',lambda a : onLeave(self.placeTarget))
        self.placeTarget.configure(font = self.buttonFont)


        self.separator1 = ttk.Separator(self.settings,orient= HORIZONTAL)
        self.separator1.grid(row=1)

        self.walls = Label(self.settings,text = "Obstacles: ",bg=self.backgroundColor,fg=self.labelText)
        self.walls.configure(font = self.labelfont)
        self.walls.grid(row=2,column=0,sticky=W)
        self.placeWalls = Button(self.settings, text = "Place walls" ,relief =FLAT,border ="0",command =setPlaceWalls,padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg =self.buttonColor)
        self.placeWalls.grid(row=2,column=1)
        self.placeWalls.bind('<Enter>',lambda a : onHover(self.placeWalls))
        self.placeWalls.bind('<Leave>',lambda a : onLeave(self.placeWalls))
        self.placeWalls.configure(font = self.buttonFont)
        self.rmWalls = Button(self.settings, text = "Remove walls" ,relief =FLAT,border ="0",command = setRemoveWalls,padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg =self.buttonColor)
        self.rmWalls.grid(row=2,column=2)
        self.rmWalls.bind('<Enter>',lambda a : onHover(self.rmWalls))
        self.rmWalls.bind('<Leave>',lambda a : onLeave(self.rmWalls))
        self.rmWalls.configure(font = self.buttonFont)

        self.separator2 = ttk.Separator(self.settings,orient= HORIZONTAL)
        self.separator2.grid(row=3)

        self.setGridScale = Label(self.settings, text = "Set grid scale: ",bg = self.backgroundColor,fg=self.labelText)
        self.setGridScale.configure(font = self.labelfont)
        self.setGridScale.grid(row =4 ,column=0,sticky= W)
        self.slider = Scale(self.settings,from_ = 10,to = 60,resolution = 10,showvalue = 0,orient = HORIZONTAL,highlightthickness=0.1,sliderlength = 15,bg = self.buttonColor,troughcolor = self.backgroundColor,relief = FLAT)
        self.slider.grid(row =4 , column =1)
        self.setGridScale = Button(self.settings, text = "Set scale",relief =FLAT,border ="0",padx = self.buttonPadX,pady = self.buttonPadY,fg=self.buttonText,bg = self.buttonColor,command = lambda : resizeMap(int(self.slider.get())))
        self.setGridScale.grid(row =4,column =2)
        self.setGridScale.bind('<Enter>',lambda a: onHover(self.setGridScale))
        self.setGridScale.bind('<Leave>',lambda a: onLeave(self.setGridScale))
        self.setGridScale.configure(font = self.buttonFont)

        self.separator3 = ttk.Separator(self.settings,orient = HORIZONTAL)
        self.separator3.grid(row = 5)
        
        self.saveMap = Label(self.settings,text="Save map: ",bg =self.backgroundColor,fg=self.labelText)
        self.saveMap.configure(font= self.labelfont)
        self.saveMap.grid(row=6,column=0,sticky=W)
        self.E1 = Entry(self.settings,bg=self.entryColor)
        self.E1.grid(row=6,column=1)
        self.save = Button(self.settings,text="Save",relief =FLAT,border ="0",command= lambda: saveToFile(self.E1.get()),padx = self.buttonPadX,fg=self.buttonText,bg=self.buttonColor)
        self.save.grid(row=6,column=2)
        self.save.bind('<Enter>',lambda a : onHover(self.save))
        self.save.bind('<Leave>',lambda a : onLeave(self.save))
        self.save.configure(font = self.buttonFont)
        
        self.separator4 = ttk.Separator(self.settings,orient= HORIZONTAL)
        self.separator4.grid(row=7)

        self.loadMap = Label(self.settings,text="Load map: ",bg =self.backgroundColor,fg=self.labelText)
        self.loadMap.configure(font = self.labelfont)
        self.loadMap.grid(row=8,column=0,sticky=W)
        self.E2 = Entry(self.settings,bg=self.entryColor)
        self.E2.grid(row=8,column=1)
        self.load = Button(self.settings,text="Load",relief =FLAT,border ="0",command= lambda: loadFromFile(self.E2.get()),padx = self.buttonPadX,fg=self.buttonText,bg=self.buttonColor)
        self.load.grid(row=8,column=2)
        self.load.bind('<Enter>',lambda a : onHover(self.load))
        self.load.bind('<Leave>',lambda a : onLeave(self.load))
        self.load.configure(font = self.buttonFont)
        
        self.consoleLog = LabelFrame(self.rootFrame, text = "Console log",fg=self.labelText,bg = self.backgroundColor,relief=FLAT,highlightbackground ="gray", highlightthickness=0.5)
        self.consoleLog.pack()
        self.consoleLog.configure(font = self.labelFrameFont)

        self.console = Text(self.consoleLog,width = 40,height= 16,padx =5,state= DISABLED,pady=5,bg=self.backgroundColor)
        self.console.grid(row=0,column=0)
        
        self.scrollbar = Scrollbar(self.consoleLog, command = self.console.yview,bg=self.backgroundColor,troughcolor=self.backgroundColor)
        self.scrollbar.grid(row=0,column=1,sticky="nsew")
        self.console['yscrollcommand'] = self.scrollbar.set

    def getConsole(self):
        return self.console
        

    def getSpeed(self):
        return int(self.speed.get())

    def update(self):
        if(self.context.isStartSim()):
            self.startButton.configure(fg = "black")
        else:
            self.startButton.configure(fg = "white")
        if(self.context.isPlaceWalls()):
            self.placeWalls.configure(fg= "black")
        else:
            self.placeWalls.configure(fg = "white")

        if(self.context.isRemoveWalls()):
            self.rmWalls.configure(fg = "black")
        else:
            self.rmWalls.configure(fg = "white")

        if(self.context.isSetStart()):
            self.placeStart.configure(fg = "black")
        else:
            self.placeStart.configure(fg = "white")

        if(self.context.isSetTarget()):
            self.placeTarget.configure(fg = "black")
        else:
            self.placeTarget.configure(fg = "white")
        self.context.setAppState('allowDiagonals',int(self.allow.get()))
        self.root.update()

class SaveSystem:
    @staticmethod
    def saveState(saveFileName,currentContext):
        if(saveFileName != ""):
            with open(saveFileName,"w+") as f:
                data = currentContext.getSaveState()
                f.write(data)
                Console.log("Map saved to file: "+str(saveFileName),'success')
        Console.log("Please enter a file name",'warning')
            
    @staticmethod
    def retrieveState(string,context):
        states = string.split("\n")
        gridScale = 0 
        stateMap = {}
        appStates = {}
        mapState = []
        gridState = []
        entityPositions = {}
        
        for i in states:
            statePair = i.split("-")
            if(len(statePair) > 1):
                stateMap[statePair[0]] = statePair[1]

        for i,j in stateMap.items():
            if(i == 'gridScale'):
                gridScale = int(j)
                
            elif(i == 'mapstate'):
                for k in j.split(","):
                    state = k.split(":")
                    mapState.append([int(state[0]),int(state[1])])

            elif(i == 'gridstate'):
                for k in j.split(","):
                    state = k.split(":")
                    gridState.append([int(state[0]),int(state[1])])
                                     
            elif(i ==  'entitypositions'):
                for k in j.split("|"):
                    state = k.split(":")
                    entityPositions[int(state[0])] = [int(i) for i in state[1].split(",")]

        context.resizeMap(gridScale)
        context.getMapState().setObstacles(mapState)
        context.getGridState().setObstacles(gridState)
                    
    @staticmethod
    def loadStateFromFile(filePath,currentContext):
        data = None
        if(filePath != ""):
            with open(filePath,'r') as f:
                data = f.read()
            if(data != None):
                SaveSystem.retrieveState(data,currentContext)
                Console.log("Map successfully loaded from file: "+str(filePath),'success')
        else:
            Console.log("Please enter a file name",'warning')
            
        
#-----------------------SYSTEMS-------------------------------------#


#----------------------MANAGERS-------------------------------------#

class ComponentManager:
    ComponentList = []
    ComponentMap = {}
    currentIndex = 0

    def loadState():
        pass
    
    #@staticmethod
    def addComponent(entityId,componentType):
        #if entity exists add the component 
        if(ComponentManager.exists(entityId)):
            # check if the component is already present 
            if(ComponentManager.has(entityId,componentType)):
                print("this component is already present")
                return
            ComponentManager.ComponentList.append(ComponentManager.createComponent(componentType))
            index = len(ComponentManager.ComponentList) - 1 
            ComponentManager.ComponentMap[entityId][componentType] = index 
        #if it does not exist, add it to the component map 
        else:
            print("Entity id :", entityId)
            ComponentManager.ComponentMap[entityId] = {}
            ComponentManager.ComponentList.append(ComponentManager.createComponent(componentType))
            index = len(ComponentManager.ComponentList) - 1
            ComponentManager.ComponentMap[entityId][componentType] = index
        return

    def getComponent(entityId,componentType):
        if(ComponentManager.has(entityId,componentType)):
            return ComponentManager.ComponentList[ComponentManager.ComponentMap[entityId][componentType]]
        print("Entity with id: ",entityId," does not have this component!!")
        return 0
    
    def isEmpty(componentList):
        if(componentList == []):
            return True
        return False
    
    def has(entityId,componentType):
        if(componentType in ComponentManager.ComponentMap[entityId].keys()):
            return True
        return False
    
    def createComponent(componentType):
        if(componentType == "transform"):
            c = TransformComponent()
            print("added component transform")
            return c
        elif(componentType == "mesh"):
            print("added component mesh")
            c = Mesh()
            return c
        elif(componentType == "collision"):
            print("added component collision")
            c = CollisionComponent()
            return c
        elif(componentType == "aiComponent"):
            print("added component ai")
            c = AIComponent()
            return c 
        else:
            print("please enter a valid coponent type")
        return 0
    
    def exists(entityId):
        if(entityId in ComponentManager.ComponentMap.keys()):
            return True
        return False
    
    def removeComponent(entityId,componentType):
        if(ComponentManager.has(entityId,componentType)):
            del ComponentManager.ComponentList[ComponentManager.ComponentMap[entityId][componentType]]
            del ComponentManager.ComponentMap[entityId][componentType]

       
class EntityManager:
    entityMap = {}
    entCurrent = 0
    entityList = []

    def loadState():
        pass
    
    def createEntity():
        EntityManager.entCurrent += 1
        p = PlayerEntity(EntityManager.entCurrent)
        EntityManager.entityMap[EntityManager.entCurrent] = p
        EntityManager.entityList.append(p)
        return p 
    
    def getEntities():
        return EntityManager.entityList
        
    def destroyEntity(entityId):
        if(EntityManager.entityMap[entityId] != None):
            if(ComponentManager.exists(entityId)):
                for i in ComponentManager.ComponentMap[entityId].keys():
                    ComponentManager.removeComponent(entityId,i)
            del EntityManager.entityMap[entityId]

        
class SystemManager:
    def __init__(self,gridScale,windowDimensions,entities,Map,Grid):
        self.systems = {}
        self.context = Context(gridScale,windowDimensions,entities,Map,Grid)
        self.systems['ui']= UISystem(self.context)
        self.systems['window'] = WindowSystem(self.context)
        self.systems['ai'] = AISystem(self.context)
        
    def getCurrentContext(self):
        return self.context
    
    def updateSystems(self):
        for i,j in self.systems.items():
            if(i == 'ai'and self.context.isStartSim()):
                for i in self.context.getEntities():
                    if(i.tag == "aiControlled"):
                        currentPosition = i.getComponent('transform').position
                        targetPosition = i.getComponent('aiComponent').TargetEntity.getComponent('transform').position

                        currentPosition = (int(currentPosition[0]/self.context.getGridScale()),int(currentPosition[1]/self.context.getGridScale()))
                        targetPosition = (int(targetPosition[0]/self.context.getGridScale()),int(targetPosition[1]/self.context.getGridScale()))
                        
                        i.getComponent('aiComponent').start = currentPosition
                        i.getComponent('aiComponent').target = targetPosition
                j.update()

            elif(i == 'window' or i == 'ui'):
                j.update()
             
                

#----------------------MANAGERS-------------------------------------#

class Map:
    def __init__(self,gridScale,windowDimensions):
        self.gridScale = gridScale
        self.windowDimensions = windowDimensions
        self.nodes = [[0 for i in range(int(windowDimensions[0]/gridScale))] for j in range(int(windowDimensions[1]/gridScale))]
        self.obstacles = []
        
    def getNodes(self):
        return self.nodes
    
    def resize(self,newSize):
        if(self.obstacles == []):
            self.gridScale = newSize
            self.nodes = [[0 for i in range(int(self.windowDimensions[0]/newSize))] for j in range(int(self.windowDimensions[1]/newSize))]
        
        
    def addObstacle(self,position):
        x = position[0]//self.gridScale
        y = position[1]//self.gridScale
        Console.log(str(position),'operation')
        Console.log("current gridScale :"+str(self.gridScale),'operation')
        self.nodes[x][y] = 1
        Console.log("map node: "+str([x,y])+"="+str(self.nodes[x][y]),'operation')
        self.obstacles.append([x,y])

    def getObstacles(self):
        return self.obstacles
    
    def setObstacles(self,obstacles):
        if(obstacles != [] or obstacles != None):
            self.clearObstacles()
            self.obstacles = obstacles
            for i in self.obstacles:
                self.nodes[i[0]][i[1]] = 1
        
    def clearObstacles(self):
        if(len(self.obstacles) >= 1):
            for i in self.obstacles:
                self.nodes[i[0]][i[1]] = 0
            self.obstacles = []
    
    def removeObstacle(self,position):
        x = int(position[0]/self.gridScale)
        y = int(position[1]/self.gridScale)
        self.nodes[x][y] = 0


class Grid:
    def __init__(self,gridScale,windowDimensions):
        self.color= (0, 229, 255)
        self.color1 = (136,219,149)
        self.color2 = (128, 216, 255)
        self.hoverColor = (255,255,255)
        self.exitColor = (184, 196, 219)
        self.colors = [(0, 229, 255),(184, 196, 219),(136,219,149),(128, 216, 255)]
        self.tilePositions = []
        self.tileMap = {}
        self.tileColors = []
        self.obstacles = []
        self.obstacleColor = (184, 101, 18)
        self.dimension = (gridScale,gridScale)
        self.windowDimensions = windowDimensions
        self.oldHoverTile = [0,0]
        self.resized = False
        
    def getHoverColor(self):
        return self.hoverColor
    
    def init(self):
        Count = 0 
        for i in range(0,self.windowDimensions[0],self.dimension[0]):
            for j in range(0,self.windowDimensions[1],self.dimension[1]):
                tileColor = self.colors[1]
                self.tileColors.append(tileColor)
                self.tilePositions.append([i,j])
                self.tileMap[str([i,j])] = Count
                Count += 1 

    def setPathColor(self,path,color=(255,0,0)):
        for i in path:
            i = [i[0]*self.dimension[0],i[1]*self.dimension[1]]
            self.tileColors[self.tileMap[str(i)]] = color

    def draw(self,screen):
        for i in range(len(self.tilePositions)):
            pygame.draw.rect(screen, self.tileColors[i],tuple(self.tilePositions[i])+self.dimension,1)
        if(self.obstacles != []):
            for i in self.obstacles:
                pygame.draw.rect(screen, self.obstacleColor,tuple(i)+self.dimension,0)
            
    def onHoverTileColor(self,position,newColor):
        if(self.oldHoverTile == position):
            self.tileColors[self.tileMap[str(position)]] = newColor
        else:
            if(self.resized):
                self.oldHoverTile = [self.oldHoverTile[0]//self.dimension[0] * self.dimension[0],self.oldHoverTile[1]//self.dimension[1]*self.dimension[1]]
            self.tileColors[self.tileMap[str(self.oldHoverTile)]] = self.exitColor
        self.oldHoverTile = position

    def addObstacle(self,position):
        self.obstacles.append(position)

    def removeObstacle(self,position):
        self.obstacles.remove(position)

    def setObstacles(self,newObstacles):
        self.obstacles = newObstacles

    def clearObstacles(self):
        if(len(self.obstacles) >= 1):
            self.obstacles = []
    
    def getObstacles(self):
        return self.obstacles
    
    def resize(self,newDimension):
        if(self.obstacles == []):
            self.resized = True
            Count = 0 
            self.dimension = (newDimension,newDimension)
            self.tileColors = []
            self.tilePositions = []
            self.tileMap = {}
            for i in range(0,self.windowDimensions[0],newDimension):
                for j in range(0,self.windowDimensions[1],newDimension):
                    tileColor = self.colors[1]
                    self.tileColors.append(tileColor)
                    self.tilePositions.append([i,j])
                    self.tileMap[str([i,j])] = Count
                    Count += 1

''' TODO -
1.)add multiple ai entities and create multiple targets enable entities to sense walls 
'''

def main():
    gridScale = 30
    windowDimensions = [600,600]
    entities = EntityManager.getEntities()
    
    M = Map(gridScale,windowDimensions)
    g = Grid(gridScale,windowDimensions)
    g.init()

    p1 = EntityManager.createEntity()
    p1.tag = "aiControlled"
    p1.addComponent("transform")
    p1.addComponent("mesh")
    p1.getComponent("mesh").setSize((gridScale,gridScale))
    p1.addComponent("aiComponent")
    p1.getComponent("mesh").original = (97, 142, 255)
    p1.getComponent("transform").translate([5*gridScale,5*gridScale])
    
    p2 = EntityManager.createEntity()
    p2.tag = "targetEntity"
    p2.addComponent("transform")
    p2.addComponent("mesh")
    p2.getComponent("mesh").setSize((gridScale,gridScale))
    p2.getComponent("mesh").original = (255,0,0)
    
    p1.getComponent("aiComponent").TargetEntity = p2
  
    Sys = SystemManager(gridScale,windowDimensions,entities,M,g)

    Console.setConsole(Sys.systems['ui'].getConsole())

    clock = pygame.time.Clock()
    while(True):
        Sys.updateSystems()
        clock.tick(60)
main()
        
        
