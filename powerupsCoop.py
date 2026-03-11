from color_theme import theme
import math
import pygame
import random
from config import *
import sys

class Powerups(pygame.sprite.Sprite):

    # create the powerups
    def __init__(self, all_sprites, player):
        super().__init__()
        self.all_sprites = all_sprites
        self.player = player
        self.collision = False

        #load all powerup images and random chooses one
        image_paths = ['Images/powerups/shield.png', 'Images/powerups/plus.png', 'Images/powerups/bomb.png']
        self.images = [pygame.image.load(path) for path in image_paths]
        self.image_size = (40, 40)  # Change the size as needed
        self.images = [pygame.transform.scale(image, self.image_size) for image in self.images]
        self.image = random.choice(self.images)  # Randomly choose one image
        self.rect = self.image.get_rect()
        self.rand_placement()
    
    def rand_placement(self):
        self.rect.x = random.randint(0, WIN_WIDTH)
        self.rect.y = random.randint(0, WIN_HEIGHT)

    def shield_funct(self, player):
        current_time = pygame.time.get_ticks()
        player.damage_loop = current_time + 5000 # allows 5 seconds of invulnerability
        player.update()
    
    def plus_funct(self, player):
        player.lives += 1
    
    def bomb_funct(self):
        # destroys all objects besides the players
        for sprite in self.all_sprites:
            if sprite not in self.player:
                sprite.kill()

    def update(self):
        for player in self.player:
            distance = math.sqrt((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2)
            collision_threshold = max(self.rect.width, self.rect.height) / 2 + max(player.rect.width, player.rect.height) / 2 - 2 * TILESIZE
                
            # check if within collision threshold to obtain the powerup
            if distance < collision_threshold:
                if self.image == self.images[0]:
                    POWERUP_CHANNEL.play(POWERUP_MUSIC)
                    theme.trigger_powerup_shield(5000)
                    self.shield_funct(player)
                elif self.image == self.images[1]:
                    POWERUP_CHANNEL.play(POWERUP_MUSIC)
                    theme.trigger_powerup_plus(600)
                    self.plus_funct(player)
                elif self.image == self.images[2]:
                    POWERUP_CHANNEL.play(BOMB_MUSIC)
                    theme.trigger_bomb(500)
                    self.bomb_funct()
                self.kill()  # Remove the powerup sprite after collision