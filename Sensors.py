import math
import pygame


GREEN=(0,255,0)
BLUE=(0,0,255)

class Sensor:
    def __init__(self,lander):
        self.lander=lander
        self.rayCount=10
        self.rayLenght= 100
        self.raySpread= math.pi*2
        self.thickness=2
        self.rays=[]
        self.splitPoints=[]
        self.offsets=[0]*self.rayCount
        
    def Draw(self,screen):     
        if self.splitPoints:
            #stores the points closest to lander
            splitPoints = [None if all(points[i] is None for points in self.splitPoints) else min(points[i] for points in self.splitPoints if points[i] is not None) for i in range(len(self.splitPoints[0]))]
            self.offsets=[1-offset[2] if offset is not None else 0 for offset in splitPoints]
            for ray,splitPoint in zip(self.rays,splitPoints):
                if splitPoint is None:
                    pygame.draw.line(screen,GREEN,ray[0],ray[1],self.thickness)
                else:
                    pygame.draw.line(screen,GREEN,ray[0],splitPoint[0:2],self.thickness)
                    pygame.draw.line(screen,BLUE,splitPoint[0:2],ray[1],self.thickness)
        self.splitPoints.clear()
        
    
    def Update(self,screen,asteroids,ground_lines):
        self.rays.clear()
        angle=self.raySpread/(self.rayCount)
        
        #Creating and updating lines position 
        for i in range(self.rayCount):
            StartPoint=self.lander.rect.center
            EndPoint=(StartPoint[0]+self.rayLenght*math.cos(math.pi/2+i*angle),StartPoint[1]+self.rayLenght*math.sin(math.pi/2+i*angle))
            self.rays.append((StartPoint,EndPoint))
    

        for asteroid in asteroids:
            if math.sqrt((self.lander.rect.centerx-asteroid.rect.centerx)**2 + (self.lander.rect.centery-asteroid.rect.centery)**2) <=self.rayLenght+60:
                #asteroid.Draw(screen)
                #stores all points that can intersect with asteroid
                self.splitPoints.append(self.Detection(asteroid.rect_lines))
                #lander collision with asteroid
                if asteroid.rect.colliderect(self.lander.rect): 
                    self.lander.collision_with_asteroid=True
        self.splitPoints.append(self.Detection(ground_lines))
        self.ColissionWithGround(ground_lines)
        self.lander.fit()
        self.Draw(screen)

        
  
    
    @staticmethod
    def lerp(A,B,t):
        return A +(B-A)*t
    
    def Get_Intersection(self,A,B,C,D):
        t_top=(D[0]-C[0])*(A[1]-C[1])-(D[1]-C[1])*(A[0]-C[0])
        u_top=(C[1]-A[1])*(A[0]-B[0])-(C[0]-A[0])*(A[1]-B[1])
        bottom=(D[1]-C[1])*(B[0]-A[0])-(D[0]-C[0])*(B[1]-A[1])

        if bottom !=0 :
           t=t_top/bottom
           u=u_top/bottom
           if 0<=t<=1 and 0<=u<=1:
               return   (self.lerp(A[0],B[0],t),
                            self.lerp(A[1],B[1],t),
                            t) #t = offset
        return None
    
    def Detection(self,rect_lines):
        splitPoints=[]
        for ray in self.rays:
            readings = [r for r in [self.Get_Intersection(ray[0],ray[1],line[0],line[1]) for line in rect_lines] if r is not None]
          
            #Find thd closest point
            if readings:
                splitPoints.append(min(readings,key=lambda x:x[2]))
            else:
                splitPoints.append(None)
                
       
        return splitPoints
    
    def ColissionWithGround(self,ground_lines):
        for line in ground_lines:
            intersection = self.Get_Intersection(self.lander.rect.topleft, self.lander.rect.bottomright, line[0], line[1])

            if intersection:
                self.lander.collision_with_ground=True
                break
           
    
         
