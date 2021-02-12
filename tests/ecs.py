import pygame
from tkinter import *
from aStarFinal import *


gridScale = 10

root = Tk()
leftFrame = Frame(root,width=100,height=100)
upS = Button(leftFrame,text="start: up")
upS.pack(side = LEFT)
downS = Button(leftFrame,text="start: down")
downS.pack(side = LEFT)
leftS = Button(leftFrame,text="start: left")
leftS.pack(side = LEFT)
rightS = Button(leftFrame,text="start: right")
rightS.pack(side = LEFT)
leftFrame.pack(side = TOP)

rightFrame = Frame(root,width=100,height=100)
upT = Button(rightFrame,text="target: up")
upT.pack(side = LEFT)
downT = Button(rightFrame,text="target: down")
downT.pack(side = LEFT)
leftT = Button(rightFrame,text="target: left")
leftT.pack(side = LEFT)
rightT = Button(rightFrame,text="target: right")
rightT.pack(side = LEFT)
rightFrame.pack(side = TOP)

bottomFrame = Frame(root, width=100,height= 100)
slider1 = Scale(bottomFrame, from_ = 1 ,to=10)
slider1.pack()
bottomFrame.pack(side=BOTTOM)
translation = None

#--------------------COMPONENTS-------------------------------------#

class ComponentBase:
    def __init__(self):
        self.type = 'base'
        
class TransformComponent(ComponentBase):
    def __init__(self,position = (0,0)):
        ComponentBase.__init__(self)
        self.type = "transform"
        self.position = position

    def setPosition(newPosition):
        position = newPosition
        
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
        self.color = color 

class CollisionComponent(ComponentBase):
    def __init__(self,meshTop,meshRight,meshLeft,meshBottom):
        self.type = "collision"
        self.top = meshTop
        self.right = meshRight
        self.left = meshLeft
        self.bottom = meshRight
        
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
        print("SUCCESS!")

    def hasComponent(self,componentType):
        if(ComponentManager.ComponentMap[self.entityId][componentType] != None):
            return True
        return False

    def getComponent(self,componentType):
        return ComponentManager.getComponent(self.entityId,componentType)

#---------------------ENTITIES--------------------------------------#



#-----------------------SYSTEMS-------------------------------------#
  

class WindowSystem:
    def __init__(self,width,height):
        pygame.init()
        self.screenWidth = width
        self.screenHeight = height
        self.screen = pygame.display.set_mode((self.screenWidth,self.screenHeight))
        self.clock = pygame.time.Clock()
        self.done = False
        self.grid = Grid()
        self.grid.init()
        self.translationDir = "right"

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            

    def draw(self,entities):
            self.grid.draw(self.screen)
            for i in entities:
                if(i.hasComponent("transform") and i.hasComponent("mesh")):
                    pygame.draw.rect(self.screen,i.getComponent("mesh").color, tuple(i.getComponent("transform").position) + i.getComponent("mesh").size)
            
                            
    def update(self,entities):
        for i in entities:
            if(i.tag == "start"):
                if(self.translationDir == "right"):
                    i.getComponent("transform").translate([slider1.get()/10,0])
                elif(self.translationDir == "left"):
                    i.getComponent("transform").translate([-slider1.get()/10,0])
                elif(self.translationDir == "up"):
                    i.getComponent("transform").translate([0,-slider1.get()/10])
                elif(self.translationDir == "down"):
                    i.getComponent("transform").translate([0,slider1.get()/10])
        

        
    def mainLoop(self,entities,path):
        i = 0
        print("This is the path: ",path)
        
        while(not self.done):
            self.processInput() 
            self.screen.fill((128, 216, 255))
            currentTarget = path[i]
            Pos = entities[0].getComponent("transform").position

            if((int(Pos[0]/gridScale),int(Pos[1]/gridScale)) == path[-1]):
                break
            if((int(Pos[0]/gridScale),int(Pos[1]/gridScale)) == currentTarget):
                i+=1
                currentTarget = path[i]
                
                if(currentTarget[0] - int(Pos[0]/gridScale) > 0):
                    self.translationDir = "right"
                elif(currentTarget[0] - int(Pos[0]/gridScale) < 0):
                    self.translationDir = "left"
                elif(currentTarget[1] - int(Pos[1]/gridScale) > 0):
                    self.translationDir = "down"
                elif(currentTarget[1] - int(Pos[1]/gridScale) < 0):
                    self.translationDir = "up"
                
                    
            self.update(entities)
            self.draw(entities)
            root.update()
            self.clock.tick(120)
            self.swapbuffer()
            
    def swapbuffer(self):
        pygame.display.flip()
        
#-----------------------SYSTEMS-------------------------------------#


#----------------------MANAGERS-------------------------------------#

class ComponentManager:
    ComponentList = []
    ComponentMap = {}
    currentIndex = 0
    
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
            c = Mesh()
            return c
        elif(componentType == "collision"):
            c = CollisionComponent()
            return c
        else:
            print("please enter a valid coponent type")
        return 0
    
    def exists(entityId):
        if(entityId in ComponentManager.ComponentMap.keys()):
            return True
        return False
    
    def removeComponent(entityId,componentType):
        if(ComponentManager.has(entityID,componentType)):
            del ComponentManager.ComponentList[ComponentManager.ComponentMap[entityId][componentType]]
            del ComponentManager.ComponentMap[entityId][componentType]
            
        
    

class EntityManager:
    entities = {}
    entCurrent = 0
    
    def getEntity():
        EntityManager.entCurrent += 1
        p = PlayerEntity(EntityManager.entCurrent)
        EntityManager.entities[EntityManager.entCurrent] = p 
        return p
    
    def removeEntity(entityId):
        if(EntityManager.entities[entityId] != None):
            if(ComponentManager.exists(entityId)):
                for i in ComponentManager.ComponentMap[entityId].keys():
                    ComponentManager.removeComponent(entityId,i)
            del EntityManager[entityId]

        
class SystemManger:
    def __init__(self,x,y):
        self.windX =  x
        self.windY = y 
        self.systems = {}
        self.systems['window'] = WindowSystem(self.windX,self.windY)
        self.systems['ai'] = AISystem()
    
        
    
    


#----------------------MANAGERS-------------------------------------#



class Grid:
    def __init__(self):
        self.color= (0, 229, 255)
        self.color1 = (1, 87, 155)
        self.color2 = (128, 216, 255)
        self.tilePositions = []
        self.dimension = (gridScale,gridScale)
    def init(self):
        for i in range(0,601,self.dimension[0]):
            for j in range(0,601,self.dimension[1]):
                self.tilePositions.append([i,j])
    def draw(self,screen):
        for i in self.tilePositions:
            pygame.draw.rect(screen, self.color1,tuple(i)+self.dimension,1)
        
                
            
        



def setTranslation(entity,translation):
    entity.getComponent("transform").translate(translation)
    
if(__name__ == '__main__'):
    def main():

        stepSize = gridScale
        maze = [ [0 for i in range(int(600/gridScale))] for j in range(int(600/gridScale))]
        for i in maze:
            print(i)
        
        p = PlayerEntity(1)
        p.addComponent("transform")
        p.addComponent("mesh")
        p.tag = "start"
        p.getComponent("transform").translate([15*gridScale,15*gridScale])
        
        p2 = PlayerEntity(2)
        p2.tag = "end"
        p2.addComponent("transform")
        p2.getComponent("transform").translate([10*gridScale,10*gridScale])
        p2.addComponent("mesh")
        p2.getComponent("mesh").color = (0,255,0)

        start = p.getComponent("transform").position
        end = p2.getComponent("transform").position

        start = (int(start[1]/stepSize),int(start[0]/stepSize))
        end = (int(end[1]/stepSize),int(end[0]/stepSize))

        print("start: ",start)
        print("end: ",end)
        
        path = astar(maze, start, end)

        print(path)
        
        
        
        upS.config(command = lambda: setTranslation(p,[0,-gridScale]))
        downS.config(command = lambda: setTranslation(p,[0,gridScale]))
        leftS.config(command = lambda: setTranslation(p,[-gridScale,0]))
        rightS.config(command = lambda: setTranslation(p,[gridScale,0]))

        upT.config(command = lambda: setTranslation(p2,[0,-gridScale]))
        downT.config(command = lambda: setTranslation(p2,[0,gridScale]))
        leftT.config(command = lambda: setTranslation(p2,[-gridScale,0]))
        rightT.config(command = lambda: setTranslation(p2,[gridScale,0]))

        entityList = []
        entityList.append(p)
        entityList.append(p2)
        Window = WindowSystem(600,600)
        Window.mainLoop(entityList,path)
        
    main()
    
