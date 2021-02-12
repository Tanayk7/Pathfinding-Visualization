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
    def __init__(self,meshType="square",color=(255,0,0),size=(30,30)):
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
        pass

    def update(self,entities):
        pass
    
        
    def mainLoop(self,entities,path):
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
    @staticmethod
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
        
        
    

class EntityManager:
    def __init__(self):
        pass

        
class SystemManger:
    def __init__(self):
        pass


#----------------------MANAGERS-------------------------------------#
