import pygame
from tkinter import *
import os


class UI:
    def __init__(self):
        self.root = Tk()
        
        self.embedFrame = Frame(self.root,width = 600, height= 600)
        self.embedFrame.grid(columnspan = 600 , rowspan = 500)
        self.embedFrame.pack(side = BOTTOM)
        
        self.buttonFrame = Frame(self.root,width = 75,height = 500)
        self.buttonFrame.pack(side = RIGHT)
        
        self.button1 = Button(self.buttonFrame,text = "button1")
        self.button1.pack(side= LEFT)
        
        os.environ['SDL_WINDOWID'] = str(self.embedFrame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

    def update(self):
        self.root.update()

ui = UI()
screen = pygame.display.set_mode((600,600))
screen.fill(pygame.Color(255,255,255))

pygame.display.init()

pygame.draw.circle(screen, (0,0,0), (250,250), 125)



         
