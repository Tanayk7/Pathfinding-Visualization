from tkinter import *
from aStarFinal import * 
import pygame
import math
import os
import time

#firstInit = True
gridScale = 30
windowX = 600
windowY = 600
pathDone = False
pathActive = False
startSim = False
setStart = False
setTarget = False
placeWalls = False
removeWalls = False
        
class Context:
    def __init__(self,gridScale,windowDimensions,mousePosition,Map=None,Grid=None):
        self.gridScale = gridScale 
        self.windowX = windowDimensions[0]
        self.windowY = windowDimensions[1]
        self.mousePos = mousePosition
        self.states = {'startSim':False,'setStart':False,'setTarget':False,'placeWalls':False,'removeWalls':False,'pathDone':False}
        self.MapState = Map
        self.GridState = Grid
        self.entityPositions = {}
        self.tilePositions = self.GridState.getTilePositions()
        self.entities = EntityManager.getEntities()
        
        for i in self.entities:
            self.entityPositions[i.getEntityid()] = i.getComponent('transform').position
            
        
    def getSaveState(self):
        #Scale = str(self.gridScale)
        stateString = ""
        
        for i,j in self.states.items():
            stateString += "appstates-"
            if j == True:
                stateString += str(i)+":1,"
            else:
                stateString += str(i)+":0,"
        stateString += "\n"
        
        if(self.MapState == None or self.GridState == None):
            print("Map or grid state is null!")
            return
        
        elif(self.MapState != None and self.GridState != None and self.entityPositions != {}):
            stateString += "mapstate-"
            for i in self.MapState.getNodes():
                stateString += str(i[0])+":"+str(i[1])+","
            stateString += "\n"

            stateString += "gridstate-"
            for i in self.GridState.getObstacles():
                stateString += str(i[0])+":"+str(i[1])+","
            stateString += "\n"
            
            stateString += "entitypositions-"
            for i,j in self.entityPositions.items():
                stateString += str(i)+":"+str(j[0])+","+str(j[1])+","
            stateString += "\n"
        return stateString
    
    def setGridHoverColor(self,mousePosition):
        for i in self.tilePositions:
            pass
        
    
    def getMousePos(self):
        return self.mousePosition
    
    def getMapState(self):
        return self.MapState
    
    def getGridState(self):
        return self.GridState
         
    def setAppState(self,stateType,value):
        if(stateType in self.states.keys() and value in [True,False]):
            self.states[stateType] = value

    def isStartSim(self):
        return self.state['startSim']
    
    def isSetStart(self):
        return self.states['setStart']
    
    def isSetTarget(self):
        return self.states['setTarget']
    
    def isPlaceWalls(self):
        return self.states['placeWalls']

    def isRemoveWalls(self):
        return self.states['removeWalls']
    
    def isPathDone(self):
        return self.states['pathDone']
    
    def updateEnvState(self,Map,Grid):
        self.MapState = Map
        self.GridState = Grid
    

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
        # rotate by amount on each axis
    def scale(self, amount):
        pass
        # scale by amount on each axis
 
class Mesh(ComponentBase):
    def __init__(self,meshType="square",color=(255,0,0),size=(gridScale,gridScale)):
        self.type = meshType
        self.size = size
        self.original = color
        self.color = self.original 
        self.hoverColor = (100,100,100)

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
    
    def findNext(self):
        if(self.path  == []):
            return True
        return False
        
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

#pathfinder
class AISystem:
    def __init__(self):
        self.type = "aiSystem"
        self.currentTarget = None
        self.counter = 0
        self.path = []
        self.delayAmount = 0.02
        
    def update(self,entities,Map,Grid):
        global pathActive
        for i in entities:
            if(i.hasComponent("aiComponent")):
                if(i.getComponent("aiComponent").goalType == "pathfinding"):
                    if(i.getComponent("aiComponent").findNext()):
                        aiComp = i.getComponent("aiComponent")
                        aiComp.path = self.findPath(aiComp.start,aiComp.target,Map.getNodes())
                        self.path = aiComp.path
                        pathActive = True
                        Grid.setPathColor(self.path)
                    else:
                        self.followPath2(i,Grid)
                        
    def setMovementSpeed(self,speed):
        self.speed = speed

    def followPath2(self,entity,Grid):
        global startSim
        if(self.path != []):
            entityPos = entity.getComponent('transform').position
            if(entityPos == [self.path[-1][0] * gridScale,self.path[-1][1]*gridScale]):
                entity.getComponent("aiComponent").path = []
                Grid.setPathColor(self.path,Grid.exitColor)
                self.path = []
                self.counter = 0
                print("Path Complete!!")
                startSim = False
                pathActive = False
                return 
               
            self.currentTarget = self.path[self.counter]
            print(len(self.path)," ",self.counter)
            entity.getComponent('transform').setPosition([self.currentTarget[0]*gridScale,self.currentTarget[1]*gridScale])
            self.counter +=1 
            time.sleep(self.delayAmount)
            
            
    def followPath(self,entity):
        global startSim
        if(self.path != []):
            entityPos = entity.getComponent("transform").position
            entityPos = (int(entityPos[0]/gridScale),int(entityPos[1]/gridScale))

            self.currentTarget = self.path[self.counter]
            
            # check if the end of the path has been completed
            if(entityPos == entity.getComponent('aiComponent').target):
                entity.getComponent("aiComponent").path = []
                self.path = []
                self.counter = 0
                print("path complete")
                startSim = False
                return 
                
            # check if the current position is equal to the current target location 
            if(entityPos == self.currentTarget):
                self.counter += 1
                
            # translate the entity in the appropriate direction
            if(self.path[self.counter][0] - entityPos[0] > 0):
                entity.getComponent("transform").translate([0.3 * self.speed,0])
                
            elif(self.path[self.counter][0] - entityPos[0] < 0):
                entity.getComponent("transform").translate([-0.3 * self.speed,0])
                
            elif(self.path[self.counter][1] - entityPos[1] > 0):
                entity.getComponent("transform").translate([0,0.3 * self.speed])
                
            elif(self.path[self.counter][1] - entityPos[1] < 0):
                entity.getComponent("transform").translate([0,-0.3 * self.speed])
        
    
    def findPath(self,start,target,nodes):
        path = astar(nodes,start,target)
        print('start: ',start, ' target: ',target)
        return path
        
        

class WindowSystem:
    def __init__(self,width,height):
        pygame.init()
        self.screenWidth = width
        self.screenHeight = height
        self.screen = pygame.display.set_mode((self.screenWidth,self.screenHeight))
        self.clock = pygame.time.Clock()
        self.translationDir = "right"
        self.backgroundColor = (128,200,255)
        self.backgroundImage = pygame.image.load("bgFinal.png")
        self.mouseX= None
        self.mouseY = None
        self.mouseDown = False
    
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

    def update(self,Context):
        startEntity = Context.getEntityByTag('aiControlled')
        targetEntity = Context.getEntityByTag('targetEntity')

        Context.setGridHoverColor(Context.getMousePos())
        
        if(Context.isSetStart() and self.mouseDown):
            placePosition = [self.mouseX/gridScale,self.mouseY/gridScale]
            startEntity.getComponent('transform').setPosition(placePosition)
            Context.setAppState('setStart',False)
            
        elif(Context.isSetTarget() and self.mouseDown):
            placePosition = [self.mouseX/gridScale,self.mouseY/gridScale]
            targetEntity.getComponent('transform').setPosition(placePosition)
            Context.setAppState('setTarget',False)

        elif(Context.isPlaceWalls() and self.mouseDown):
            placePosition = [self.mouseX/gridScale,self.mouseY/gridScale]
            Context.getMapState().addObstacle(placePosition)
            Context.getGridState().addObstacle([self.mouseX,self.mouseY])
            
        elif(Context.isRemoveWalls() and self.mouseDown):
            placePosition = [self.mouseX/gridScale,self.mouseY/gridScale]
            Context.getMapState().removeObstacle(placePosition)
            Context.getGridState().removeObstacle([self.mouseX,self.mouseY])
        
        elif(Context.isPathActive()):
            Context.getGridState().setPathColor(startEntity.getComponent('aiComponent').path)

        self.screen.blit(self.backgroundImage,(0,0))
        Context.drawGrid() # ***IMPLEMENT***
        Context.drawAll()  # ***IMPLEMENT***
        
        
    def update(self,entities,grid,Map):
        global setStart,setTarget
        #self.screen.fill(self.backgroundColor)
        startEntity = None
        targetEntity = None
        for i in entities:
            if(i.tag == 'aiControlled'):
                startEntity = i
            elif(i.tag == 'targetEntity'):
                targetEntity = i
    
        for i in grid.tilePositions:
            if(self.mouseOnPos(i)):
                grid.onHoverTileColor(i,grid.hoverColor)
                
                if(setStart and self.mouseDown):
                    for j in entities:
                        if(j.tag == 'aiControlled'):
                            j.getComponent('transform').setPosition(i)
                            print('start set at : ',j.getComponent('transform').position)
                            setStart = False
                            
                elif(setTarget and self.mouseDown):
                    for j in entities:
                        if(j.tag == 'targetEntity'):
                            j.getComponent('transform').setPosition(i)
                            print('target set at : ',j.getComponent('transform').position)
                            setTarget = False
                            
                elif(placeWalls and self.mouseDown):
                    Map.addObstacle(i)
                    grid.addObstacle(i)
                    
                elif(removeWalls and self.mouseDown):
                    if(i in grid.obstacles):
                        Map.removeObstacle(i)
                        grid.removeObstacle(i)
                        
            else:
                grid.onExitTileColor(i,grid.exitColor)
        if(pathActive):
                grid.setPathColor(startEntity.getComponent('aiComponent').path)
                
        self.screen.blit(self.backgroundImage,(0,0))
        
        for i in entities:
            if(self.mouseOnPos(i.getComponent("transform").position) and not startSim):
                i.getComponent('mesh').color = i.getComponent('mesh').hoverColor
            else:
                i.getComponent('mesh').color = i.getComponent('mesh').original
                
            if(i.hasComponent("transform") and i.hasComponent("mesh")):
                pygame.draw.rect(self.screen,i.getComponent("mesh").color, tuple(i.getComponent("transform").position) + i.getComponent("mesh").size)
        grid.draw(self.screen)
        
    
    def mouseOnPos(self,entityPos):
        if(self.mouseX >= entityPos[0] and self.mouseX <= entityPos[0] + gridScale and self.mouseY >= entityPos[1] and self.mouseY <= entityPos[1] + gridScale):
            return True
        return False

        
    def swapBuffer(self):
        self.clock.tick(120)
        pygame.display.flip()


class UISystem:
    def __init__(self):
        self.root = Tk()
        self.root.resizable(False, False)
        
        self.embedFrame = Frame(self.root,width = 600, height= 600)
        self.embedFrame.grid(columnspan = 600 , rowspan = 500)
        self.embedFrame.pack(side = LEFT)
        
        os.environ['SDL_WINDOWID'] = str(self.embedFrame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.backgroundColor = 'mint cream'
        self.rootFrame = Frame(self.root,width = 200,height = 500)
        self.rootFrame.pack(side = TOP)
        self.root.configure(bg = self.backgroundColor)
        self.rootFrame.configure(bg = self.backgroundColor)
        
        self.buttonPadX = 20
        self.buttonPadY = 10
        
        def startSimulation():
            global startSim
            startSim = True

        def stopSim():
            global startSim
            startSim = False

        def setStartLocation():
            global setStart
            setStart = True
            
        def setTargetLocation():
            global setTarget
            setTarget = True

        def setRemoveWalls():
            global removeWalls
            if(removeWalls):
                removeWalls = False
            else:
                removeWalls = True
                
                    
        
        def setPlaceWalls():
            global placeWalls
            if(placeWalls):
                placeWalls = False
            else:
                placeWalls = True
                
        def onHover(button):
            button.configure(bg = 'ghost white')

        def onLeave(button):
            button.configure(bg = 'azure')
        
        self.labelFrame1 = LabelFrame(self.rootFrame,text= "Controls")
        self.labelFrame1.pack(side=TOP)
        self.labelFrame1.configure(bg = self.backgroundColor)

        self.settings = LabelFrame(self.rootFrame,text = "Settings")
        self.settings.pack(side=BOTTOM)
        self.settings.configure(bg = self.backgroundColor)
        
        self.buttonFrame = Frame(self.labelFrame1)
        
        self.startButton = Button(self.buttonFrame,text = "START",command = startSimulation,padx = self.buttonPadX,pady = self.buttonPadY,bg ="azure")
        self.startButton.pack(side= LEFT)
        self.startButton.bind('<Enter>',lambda a : onHover(self.startButton))
        self.startButton.bind('<Leave>',lambda a : onLeave(self.startButton))
        
        self.stopButton = Button(self.buttonFrame,text = "STOP",command = stopSim,padx = self.buttonPadX,pady = self.buttonPadY,bg = "azure")
        self.stopButton.pack(side= LEFT)
        self.stopButton.bind('<Enter>',lambda a : onHover(self.stopButton))
        self.stopButton.bind('<Leave>',lambda a : onLeave(self.stopButton))
        
        self.buttonFrame.pack(side= TOP)
        self.buttonFrame.configure(bg = self.backgroundColor)


        self.placeSettings = Frame(self.settings)
        
        self.startAndTarget = Label(self.placeSettings,text = "Start and target: ",bg=self.backgroundColor)
        self.startAndTarget.pack(side= LEFT)
        
        self.placeStart = Button(self.placeSettings, text= "Place start" ,command = setStartLocation,padx = self.buttonPadX,pady = self.buttonPadY,bg ="azure")
        self.placeStart.pack(side = LEFT)
        self.placeStart.bind('<Enter>',lambda a : onHover(self.placeStart))
        self.placeStart.bind('<Leave>',lambda a : onLeave(self.placeStart))
        
        self.placeTarget = Button(self.placeSettings, text= "Place target" ,command = setTargetLocation,padx = self.buttonPadX,pady = self.buttonPadY,bg ="azure")
        self.placeTarget.pack(side = LEFT)
        self.placeTarget.bind('<Enter>',lambda a : onHover(self.placeTarget))
        self.placeTarget.bind('<Leave>',lambda a : onLeave(self.placeTarget))
        
        self.placeSettings.pack(side = TOP)
        self.placeSettings.configure(bg = self.backgroundColor)

        self.wallSettings = Frame(self.settings)
        
        self.walls = Label(self.wallSettings,text = "Obstacles: ",bg=self.backgroundColor)
        self.walls.pack(side= LEFT)
        self.placeWalls = Button(self.wallSettings, text = "Place walls" , command = setPlaceWalls,padx = self.buttonPadX,pady = self.buttonPadY,bg ="azure")
        self.placeWalls.pack(side = LEFT)
        self.placeWalls.bind('<Enter>',lambda a : onHover(self.placeWalls))
        self.placeWalls.bind('<Leave>',lambda a : onLeave(self.placeWalls))
        
        self.rmWalls = Button(self.wallSettings, text = "Remove walls" , command = setRemoveWalls,padx = self.buttonPadX,pady = self.buttonPadY,bg ="azure")
        self.rmWalls.pack(side = LEFT)
        self.rmWalls.bind('<Enter>',lambda a : onHover(self.rmWalls))
        self.rmWalls.bind('<Leave>',lambda a : onLeave(self.rmWalls))
        
        self.wallSettings.pack(side = BOTTOM)
        self.wallSettings.configure(bg = self.backgroundColor)


        
    def getSpeed(self):
        return int(self.speed.get())

    def update(self):
        self.root.update()

class SaveSystem:
    #Map
    #grid
    #entities (with entityIds) and their components.
    
    @staticmethod
    def saveState(saveFileName,currentContext): 
        with open(saveFileName,"w+") as f:
            data = currentContext.getSaveState()
            f.write(data)
            print(data)

    @staticmethod
    def retrieveState(string,context):
        states = string.split("\n")
        stateMap = {}
        appStates = {}
        mapState = []
        gridState = []
        entityPositions = []
        
        for i in states:
            statePair = i.split("-")
            if(len(statePair) > 1):
                stateMap[statePair[0]] = statePair[1]
                
        for i,j in stateMap.items():
            print(j)
            if(i == 'appstates'):
                for k in j.split(","):
                    print(k)
                    appStatePair = k.split(":")
                    appStates[appStatePair[0]] = appStatePair[1]
              
            elif(i == 'mapstate'):
                for k in j.split(","):
                    state = k.split(":")
                    mapState.append([state[0],state[1]])
        
            elif(i == 'gridstate'):
                for k in j.split(","):
                    state = k.split(":")
                    gridState.append([state[0],state[1]])
                    
            elif(i ==  'entitypositions'):
                for k in j.split(","):
                    state = k.split(":")
                    entityPositions.append([state[0],state[1]])
                    
        context.states = appStates
        context.MapState = mapState
        context.GridState = gridState
        context.entityPositions = entityPositions
                    
    @staticmethod
    def LoadStateFromFile(filePath,currentContext):
        data = None
        with open("filePath",r) as f:
            data = f.read()
        if(data != None):
            SaveSystem.retrieveState(data,currentContext)
        
            
            
    

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
    def __init__(self,x,y):
        self.windX =  x
        self.windY = y 
        self.systems = {}
        self.Context = None
        self.systems['ui']= UISystem()
        self.systems['window'] = WindowSystem(self.windX,self.windY)
        self.systems['ai'] = AISystem()
        #self.systems['saveSystem'] = SaveSystesm()

    def createContext(self,gridScale,windowDimensions,Map,Grid):
        self.Context = context(gridScale,windowDimensions,Map,Grid)
    
    def updateSystems(self,entities,grid,Map):
        for i,j in self.systems.items():
            
            if(i == 'ai' and startSim):
                player = None
                target = None
                
                for i in entities:
                    if(i.tag == 'aiControlled'):
                        player = i

                currentPosition = player.getComponent('transform').position
                targetPosition = player.getComponent('aiComponent').TargetEntity.getComponent('transform').position
                    
                currentPosition = (int(currentPosition[0]/gridScale),int(currentPosition[1]/gridScale))
                targetPosition = (int(targetPosition[0]/gridScale),int(targetPosition[1]/gridScale))
                    
                player.getComponent('aiComponent').start = currentPosition
                player.getComponent('aiComponent').target = targetPosition
                
                j.update(entities,Map,grid)
  
            elif(i == 'ui'):
                j.update()
                
            elif(i == 'window'):
                j.processInput()
                j.update(entities,grid,Map)
                j.swapBuffer()
            
        

#----------------------MANAGERS-------------------------------------#


class Map:
    def __init__(self):
        self.nodes = [[0 for i in range(int(windowX/gridScale))] for j in range(int(windowY/gridScale))]
        
    def getNodes(self):
        return self.nodes
    
    def resize(self):
        pass
        
    def addObstacle(self,position):
        x = int(position[0]/gridScale)
        y = int(position[1]/gridScale)
        self.nodes[x][y] = 1

    def removeObstacle(self,position):
        x = int(position[0]/gridScale)
        y = int(position[1]/gridScale)
        self.nodes[x][y] = 0
    
        

class Grid:
    def __init__(self):
        self.color= (0, 229, 255)
        self.color1 = (136,219,149)
        self.color2 = (128, 216, 255)
        self.hoverColor = (255,255,255)
        self.exitColor = (136,219,149)
        self.colors = [(0, 229, 255),(136,219,149),(128, 216, 255)]
        self.tilePositions = []
        self.tileMap = {}
        self.tileColors = []
        self.obstacles = []
        self.obstacleColor = (230,160,112)
        self.dimension = (gridScale,gridScale)
        
    def init(self):
        for i in range(0,601,self.dimension[0]):
            for j in range(0,601,self.dimension[1]):
                tileColor = self.colors[1]
                self.tileColors.append(tileColor)
                self.tilePositions.append([i,j])
                key =  str([i,j])
                self.tileMap[key] = [i,j]
                
        print(self.tileMap)
                
    def setPathColor(self,path,color=(0,0,255)):
        for i in path:
            for j in range(len(self.tilePositions)):
                if([i[0]*gridScale,i[1]*gridScale] == self.tilePositions[j]):
                    self.tileColors[j] = color
    
            
    def draw(self,screen):
        for i in range(len(self.tilePositions)):
            pygame.draw.rect(screen, self.tileColors[i],tuple(self.tilePositions[i])+self.dimension,1)
        if(self.obstacles != []):
            for i in self.obstacles:
                pygame.draw.rect(screen, self.obstacleColor,tuple(i)+self.dimension,0)
            
    def onHoverTileColor(self,position,newColor):
        for i in range(len(self.tilePositions)):
            if(self.tilePositions[i] == position):
                self.tileColors[i] = newColor

    def addObstacle(self,position):
        self.obstacles.append(position)

    def removeObstacle(self,position):
        self.obstacles.remove(position)
        
    def onExitTileColor(self,position,newColor):
        for i in range(len(self.tilePositions)):
            if(self.tilePositions[i] == position):
                self.tileColors[i] = newColor
                
    def getTilePositions(self):
        return self.tilePositions
    
    def getObstacles(self):
        return self.obstacles

        
def main():

    Sys = SystemManager(windowX,windowY)
    
    g = Grid()
    g.init()
    
    p1 = EntityManager.createEntity()
    p1.tag = "aiControlled"
    p1.addComponent("transform")
    p1.addComponent("mesh")
    p1.addComponent("aiComponent")
    p1.getComponent("mesh").original = (0,255,0)
    p1.getComponent("transform").translate([60,120])
    

    p2 = EntityManager.createEntity()
    p2.tag = "targetEntity"
    p2.addComponent("transform")
    p2.addComponent("mesh")
    p2.getComponent("mesh").original = (255,0,0)
    p2.getComponent("transform").translate([60,60])
    
    entities = EntityManager.getEntities()
    
    M = Map()

    c = Context(gridScale,[600,600],M,g)
    SaveSystem.saveState("saveState.txt",c)
    print("context saved!!")
    
    p1.getComponent("aiComponent").TargetEntity = p2
    
    while(True):
        Sys.updateSystems(entities,g,M)
            
main()
        
        
