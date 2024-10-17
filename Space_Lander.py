import pygame
import math
from Particles import Particle
from Sensors import Sensor
from engine import Engine

class SpaceLander(pygame.sprite.Sprite) :
    def __init__(self,x,y,m,image_path,Center_of_landing_point):
        super().__init__()
        self.image=pygame.image.load(image_path).convert_alpha()
        self.image=pygame.transform.scale_by(self.image, 0.6)
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.mass=m
        self.speed=0.0
        self.acceleration=0.0
        self.Engines=[Engine(0,self,'LEFT'),Engine(90,self,'LOWER'),Engine(180,self,'RIGHT')]
        self.last_particle_time=0

        self.collision_with_asteroid=False
        self.collision_with_ground=False
        self.outside_border=False
        self.Center_of_landing_point=Center_of_landing_point
        self.distance=[self.normalisation(cord,0,1000) for cord in self.DistanceToLandingPoint()]
        self.velocity=[0,0]
        self.sensors=Sensor(self)
        self.angle=0
        
        #data for velocity normalization
        self.max_velocity=[0.1,0.1]
        self.min_velocity=[0,0]

        self.reward=0
        self.top_rewards=[0,0]
        self.last_offsets=[]
        self.last_distance=math.sqrt(self.DistanceToLandingPoint()[0]**2+self.DistanceToLandingPoint()[1]**2)

    def Gravity(self,g):
        return self.mass*g
              
    def Final_Force(self,g,time):
        Force_x=0.0
        Force_y=self.Gravity(g)

        for engine in self.Engines:
            if engine.thrust != 0:
                engine.EngineForce()
                Force_x+=engine.force[0]
                Force_y+=engine.force[1]

        Final_Force=math.sqrt(Force_x**2 + Force_y**2)
        if Force_x!=0:
            angle=math.atan2(Force_y,Force_x)
        else:
            angle = math.pi / 2 if Force_y > 0 else -math.pi / 2
    
        return (Final_Force/self.mass,angle)
    
    def Update(self,time,g):
        self.acceleration,angle=self.Final_Force(g,time)
        
        dx=self.rect.x +self.speed*math.cos(angle)*time + 0.5*self.acceleration * time**2 *-1
        dy=self.rect.y +self.speed*math.sin(angle)*time + 0.5*self.acceleration * time**2 *-1
            
        self.speed=self.speed + self.acceleration*time
        self.rect.x=dx
        self.rect.y=dy

        self.distance=[self.normalisation(cord,0,1000) for cord in self.DistanceToLandingPoint()]
        
        #setting max and min of velocity values for normalisation

        #x velocity
        if self.max_velocity[0]<self.speed*math.cos(angle):
            self.max_velocity[0]=self.speed*math.cos(angle)
        elif self.min_velocity[0]>self.speed*math.cos(angle):
            self.max_velocity[0]=self.speed*math.cos(angle)
        #y velocity
        if self.max_velocity[1]<self.speed*math.sin(angle):
            self.max_velocity[1]=self.speed*math.sin(angle)
        elif self.min_velocity[1]>self.speed*math.sin(angle):
            self.max_velocity[1]=self.speed*math.sin(angle)

        self.velocity[0]=self.normalisation(self.speed*math.cos(angle),self.min_velocity[0],self.max_velocity[0])
        self.velocity[1]=self.normalisation(self.speed*math.sin(angle),self.min_velocity[1],self.max_velocity[1])
        
        self.angle=angle

        self.IsOutsideBorder()
                         
    def Activate(self,actions):
        for i in range(3):
                self.Engines[i].thrust=actions[i]
                self.Engines[i].SetAngle(actions[i+3])
    
    def DistanceToLandingPoint(self):
            return [math.sqrt((self.Center_of_landing_point[0]-self.rect.x)**2),math.sqrt((self.Center_of_landing_point[1]-self.rect.y)**2)]
    
    @staticmethod
    def normalisation(x,min,max):
        return (x-min)/(max-min)
    
    def Reset(self,x,y):
        self.rect.center=(x,y)
        self.speed=0.0
        self.acceleration=0.0
        self.Engines=[Engine(0,self,'LEFT'),Engine(90,self,'LOWER'),Engine(180,self,'RIGHT')]
        self.last_particle_time=0

        self.collision_with_asteroid=False
        self.collision_with_ground=False
        self.outside_border=False
        self.velocity=[0,0]
        
        self.angle=0
        self.reward=0

        self.last_offsets=[]
        self.last_distance=math.sqrt(self.DistanceToLandingPoint()[0]**2+self.DistanceToLandingPoint()[1]**2)
        self.sensors=Sensor(self)

    def fit(self):

        #self.reward-= self.speed*math.sin(self.angle)
        
        if self.collision_with_asteroid or self.outside_border:
            self.reward-=2000
        elif self.collision_with_ground:
            self.reward-=1000
        
        x_dist,y_dist=self.DistanceToLandingPoint()
        dist=math.sqrt(x_dist**2 + y_dist**2)

        self.reward-=dist/10
        self.reward+=self.last_distance-dist
        self.last_distance=dist
       
        if self.SuccesfullLanding():
            self.reward+=1e9

        #reward for avoiding asteroids
        if len(self.last_offsets) != 0:
            for i,ofssets in enumerate(self.sensors.offsets):
                if self.last_offsets[i] is None and ofssets is not None:
                    self.reward-=ofssets*100
                elif self.last_offsets[i] is not None and ofssets is None:
                    self.reward+=self.last_ofssets[i]*100
                elif self.last_offsets[i] is not None and ofssets is not None:
                    self.reward+= (self.last_offsets[i] -ofssets) *100
        self.last_offsets=self.sensors.offsets

        if self.reward>self.top_rewards[0]:
            self.top_rewards[0]=self.reward
        elif self.reward<self.top_rewards[1]:
            self.top_rewards[1]=self.reward
        
    def IsOutsideBorder(self):
        screen_width=1000
        screen_height=850
        x,y=self.rect.center

        if  not -10<=x<=screen_width+10:
            self.outside_border=True
        elif not -10<=y<=screen_height:
            self.outside_border=True

    def SuccesfullLanding(self):
        length_of_landing_point=50
        x1=self.Center_of_landing_point[0]-(length_of_landing_point/2)
        x2=self.Center_of_landing_point[0]+(length_of_landing_point/2)
        y=self.Center_of_landing_point[1]

        if x1-5<=self.rect.centerx<=x2+5 and y-10<self.rect.bottom <y+10:
            return True
        
    def State(self):
        return self.sensors.offsets+self.velocity+self.distance,self.reward,(self.collision_with_asteroid or self.collision_with_ground or self.outside_border)

    def WriteInfo(self,screen,font):
        current_reward=f"Reward: {int(self.reward)}"
        best_reward=f"Best Reward: {int(self.top_rewards[0])}"
        worst_reward=f"Worst Reward: {int(self.top_rewards[1])}"
        distances=self.DistanceToLandingPoint()
        x_dist=f"X Distance: {int(distances[0])}"
        y_dist=f"Y Distance: {int(distances[1])}"
        engines=[f"Engine: {str(engine.name)} thrust: {int(engine.thrust)} angle: {int(engine.GetAngle())} " for engine in self.Engines]
        texts=[current_reward,best_reward,worst_reward,x_dist,y_dist] + engines
        x=900
        y=10
        for text in texts:
            textobj=font.render(text,True,(255,0,0))
            textrect = textobj.get_rect()
            textrect.center=(x,y)
            screen.blit(textobj, textrect)
            y+=10



