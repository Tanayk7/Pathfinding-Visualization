
class handleEvents:
    def __init__(self):
        self.handlers = {}
        self.handlers['event1'] = self.onEventType1
        self.handlers['event2'] = self.onEventType2
        self.handlers['event3'] = self.onEventType3
        self.handlers['event4'] = self.onEventType4
    
    def onEventType1(self):
        print("event 1 happened!!!")
    
    def onEventType2(self):
        print("event 2 happened!!!")

    def onEventType3(self):
        print("event 3 happened!!!")

    def onEventType4(self):
        print("event 4 happened!!!")
    
    def notify(self,eventType):
        self.handlers[eventType]()

    

class EventSystem:
    def __init__(self,EntityList):
        self.Entities = EntityList

    def invokeEvent(self,eventType):
        for i in self.Entities:
            i.notify(eventType)


class Entity(handleEvents):
    def __init__(self):
        handleEvents.__init__(self)

    def onEventType3(self):
        print("cusotm event 3")
    def onEventType4(self):
        print("custom event 4")

if(__name__ == '__main__'):
    def main():
        E1 = Entity()
        E2 = Entity()
        EntityList = [E1,E2]
        eventSys = EventSystem(EntityList)
        eventSys.invokeEvent('event4')
        eventSys.invokeEvent('event3')
    
    main()
        
