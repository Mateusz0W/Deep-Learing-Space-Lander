import pygame
import sys
import random
from Space_Lander import SpaceLander
from Asteroid import asteroid
from Flag import flag
from tqdm import tqdm
from keras import models

from DDPG2 import DDPGAgent


GRAVITY=73.2
Running=True
EPISODES=100_000


pygame.init()

screen_width=1000
screen_height=850
screen=pygame.display.set_mode((screen_width,screen_height))

pygame.display.set_caption('Space Lander')

clock=pygame.time.Clock()

font = pygame.font.SysFont(None, 15)
#drawing map

ground=[(0,screen_height)] #starting points
new_x=random.randint(10,screen_width-155)
new_y=random.randint(screen_height-100,screen_height-50)
landing_point=[(new_x,new_y),(new_x+150,new_y)]
new_x=0
while True:
    new_x=random.randint(new_x,new_x+50)
    new_y=random.randint(new_y-30,new_y+30)
    if new_y>screen_height:
        new_y-=30
    elif new_y<screen_height-200:
        new_y+=30
    if landing_point[0][0]<=new_x<=landing_point[1][0] :
        ground+=landing_point
        new_x=landing_point[1][0]+1
    else:
        ground.append((new_x,new_y))
    if ground[-1][0]>=screen_width-10:
        break

ground.append((screen_width,screen_height))
ground.append((0,screen_height))

ground_lines=[(ground[i-1],ground[i]) for i in range(len(ground))]

left_Flag=flag(landing_point[0],"Flag.png")
right_Flag=flag(landing_point[1],"Flag.png",flip=True,bottomleft=False)

Center_of_landing_point=((landing_point[1][0]+landing_point[0][0])/2,landing_point[0][1])

x=random.uniform(30,screen_width-30)
lander=SpaceLander(x,35,6.5,'SpaceLander.png',Center_of_landing_point) 
asteroids=[asteroid(random.uniform(10,screen_width-10),random.uniform(200,screen_height-300),'Asteroid.png') for _ in range(random.randint(4,8))]#8 12

agent=DDPGAgent((14,),14,6)

episod_reward=0
step=1

current_state,reward,done=lander.State()
done=False

progress_bar = tqdm(total=EPISODES, desc="Training Progress", unit="step")

t=0.02

while Running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0,0,0))
    

    pygame.draw.polygon(screen,(200,130,0),ground)   

    screen.blit(left_Flag.image,left_Flag.rect)
    screen.blit(right_Flag.image,right_Flag.rect)
   
    action=agent.policy(current_state)
    
    lander.Activate(action)
    lander.Update(t,GRAVITY)
    lander.sensors.Update(screen,asteroids,ground_lines)

    for engine in lander.Engines:
        engine.GasAnimation(screen,t)
    
    screen.blit(lander.image, lander.rect.topleft)      
    lander.WriteInfo(screen,font)

    new_state,reward,done=lander.State()
    agent.update_replay_memory((current_state,action,reward,new_state,done))

    step+=1
    progress_bar.update(1)
        
        
    for asteroid in asteroids:
        screen.blit(asteroid.image,asteroid.rect.topleft)

    if step%10==0 and step>100:
        agent.train()
        agent.UpdateTarget(agent.target_actor,agent.actor_model)
        agent.UpdateTarget(agent.target_critic,agent.critic_model)
        
    current_state=new_state
        
    if done:
        lander.Reset(x,35)

    if EPISODES<step:
        # Zapisujemy model w formacie TensorFlow
        agent.model.save('trained_model.keras')
        break 
        
        
    pygame.display.flip()
    clock.tick(60)
progress_bar.close()
   
