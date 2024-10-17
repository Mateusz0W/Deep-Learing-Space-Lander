import pygame
import math

class Particle:
    def __init__(self,x,y,lander):
        self.x=x
        self.y=y
        self.color=[255,255,255]
        self.radius=3
        self.speed=1000
        self.lifetime=100
        self.lander=lander
    def draw(self,screen):
        if self.lifetime>0:
            pygame.draw.circle(screen,self.color,(self.x,self.y),self.radius)
    def Update(self,angle,time):
        lander_x_velocity=self.lander.speed*math.cos(self.lander.angle)
        lander_y_velocity=self.lander.speed*math.sin(self.lander.angle)

        self.x+=(self.speed*math.cos(angle)+lander_x_velocity)*time *-1
        self.y+=(self.speed*math.sin(angle)+lander_y_velocity)*time
        self.color=[max(c-17,0) for c in self.color]
        self.lifetime-=6
    def delete(self):
        if self.lifetime==0:
            del self