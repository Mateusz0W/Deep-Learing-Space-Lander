import pygame
import random

class asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        scale = random.uniform(0.2, 0.5)
        rotation = random.randint(0, 360)
        self.image = pygame.transform.rotozoom(self.image, rotation, scale)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.rect_lines=[
            ((self.rect.left,self.rect.top),(self.rect.right,self.rect.top)), #top side
            ((self.rect.right,self.rect.top),(self.rect.right,self.rect.bottom)), #right side
            ((self.rect.right,self.rect.bottom),(self.rect.left,self.rect.bottom)), #bottom side
            ((self.rect.left,self.rect.bottom),(self.rect.left,self.rect.top)) #left side
        ]

    def Draw(self,screen):
        for lines in self.rect_lines:
             pygame.draw.line(screen,(255,0,120),lines[0],lines[1],3)

    