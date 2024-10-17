import math
import time
from Particles import Particle

class Engine:
    def __init__(self,angle,lander,name):
        self.thrust=0
        self.angle=math.radians(angle)
        self.force=0
        self.particles=[]
        self.last_particle_time=0
        self.lander=lander
        self.name=name

    def EngineForce(self):
        self.force= (self.thrust*math.cos(self.angle),-self.thrust*math.sin(self.angle))

    def GasStartingPosition(self):
        x,y=self.lander.rect.center
        if self.name=='LEFT':
            x=self.lander.rect.left
        elif self.name=='RIGHT':
            x=self.lander.rect.right
        elif self.name=='LOWER':
            y=self.lander.rect.bottom
        return x,y
        
    def GasAnimation(self,screen,t):
        current_time=time.time()
        if self.thrust !=0:
            TimeBeetwenParticles=50/self.thrust
            if current_time-self.last_particle_time >=TimeBeetwenParticles:
                x,y=self.GasStartingPosition()
                self.particles.append(Particle(x,y,self.lander))
                self.last_particle_time=current_time
        for particle in self.particles:
            particle.draw(screen)
            particle.Update(self.angle,t)
            particle.delete()

    def SetAngle(self,angle):
        if self.name=='LEFT':
            self.angle=math.radians(angle)
        elif self.name =='LOWER':
            self.angle=math.radians(90+angle)
        elif self.name=='RIGHT':
            self.angle=math.radians(180+angle)

    def GetAngle(self):
        if self.name=='LEFT':
            return math.degrees(self.angle)
        elif self.name =='LOWER':
            return 90-math.degrees(self.angle)
        elif self.name=='RIGHT':
            return 180-math.degrees(self.angle)