import pygame

class flag:
    def __init__(self,landing_point,image_path,flip=False,bottomleft=True):
        super().__init__()
        self.image=pygame.transform.scale_by(pygame.image.load("flag.png").convert_alpha(), 0.6)
        self.rect=self.image.get_rect()
        if flip:
            self.image=pygame.transform.flip(self.image,True,False)
        if bottomleft:
            self.rect.bottomleft=landing_point
        else:
            self.rect.bottomright=landing_point
  
        
