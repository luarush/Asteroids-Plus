import pygame
from config import *

class DashEffect(pygame.sprite.Sprite):
    def __init__(self, game, pos, image_path):
        self.game = game
        self._layer = PLAYER_LAYER - 1
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        # load and scale
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE * 2, TILESIZE * 2))
        self.rect = self.image.get_rect(center=pos)
        
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 200


    def update(self):
        # rotate by 5 degrees every update
        # its a little hacky but whatever
        self.image = pygame.transform.rotate(self.image, 5)

        # recenter image
        self.rect = self.image.get_rect(center=self.rect.center)
        # delete once it's been there for long enough
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()