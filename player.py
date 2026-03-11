import pygame
from config import *
import math
import random
from dashEffect import DashEffect

class Player(pygame.sprite.Sprite):
    
    def __init__(self, game, x, y, image_list):

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups) #add player to all sprites group

        self.lives = PLAYER_LIVES
        self.last_shot_time = 0  # Initialize the last shot time

        # dash stuff
        self.last_dash_time = 0
        self.dash_cooldown = 5000 
        self.dash_distance = 150

        # player position based on tile
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        # player size - one tile
        self.width = TILESIZE
        self.height = TILESIZE

        # create player
        self.image_list = image_list 
        self.og_image = self.image_list[0]
        self.image = self.og_image
        self.damaged_image = self.image_list[3]
        self.damage_loop = 0

        # self.image.get_rect() returns a new rectangle covering the entire surface of `self.image`. This rectangle (rect) is used to position the sprite on the screen.
        # it's important for collision detection and rendering the sprite at its current position.
        self.rect = self.og_image.get_rect()

        # set player's rect x, y positions
        self.rect.x = self.x
        self.rect.y = self.y

        #acceleration
        self.velocity = pygame.math.Vector2(0, 0)  # Initialize velocity vector
        self.acceleration = 0.2  # Adjust as needed for acceleration rate
        self.deceleration = 0.98  # Adjust as needed for deceleration rate

        #temporary value at init
        self.x_change = 0
        self.y_change = 0
        self.angle = 0
        self.player_bullets = self.game.player_bullets
        
        self.score = 0
        
    #update player sprite
    def update(self):

        current_time = pygame.time.get_ticks()           
        #update movement
        self.rotate()
        self.movement()
        #update collision check
        #self.collide_asteroid()

        #check collisions
        self.collide(self.game.ship_bullets)
        self.collide(self.game.asteroids)
        self.collide(self.game.ships)
        

        #update acceleration
        self.rect.center += self.velocity  # Apply velocity to the player's position
        self.decelerate()  # Apply deceleration to slow down the player over time
        self.wrap_around_screen()

        #update player rect position based on return value of movement()
        self.rect.x += self.x_change
        self.rect.y += self.y_change

        #reset _change vars
        self.x_change = 0
        self.y_change = 0

        # Flickering logic: Change image back and forth if within invulnerability period
        if current_time <= self.damage_loop + 3000:  # 3000 ms invulnerability
            if current_time // 250 % 2 == 0:  # Change image every 250 ms
                self.image = self.damaged_image
            else:
                self.image = self.og_image
        else:
            self.image = self.og_image  # Outside invulnerability period, use original image

        self.rotate()
        self.handle_input()
           
    def dash(self):
        DashEffect(self.game, self.rect.center, 'Images/dash/dash-1.png')

        # calc the final dash position
        rad_angle = math.radians(self.angle)
        dash_x = math.cos(rad_angle) * self.dash_distance
        dash_y = math.sin(rad_angle) * self.dash_distance
        
        # vwooop (dash)
        self.rect.centerx += dash_x
        self.rect.centery += dash_y
        self.wrap_around_screen()

        DashEffect(self.game, self.rect.center, 'Images/dash/dash-2.png')

    def draw_cooldown_bar(self, screen):
        current_time = pygame.time.get_ticks()
        time_passed = current_time - self.last_dash_time
        
        # if still in cooldown then draw the bar
        if time_passed < self.dash_cooldown:
            progress = time_passed / self.dash_cooldown
            
            bar_width = TILESIZE
            bar_x = self.rect.centerx - bar_width / 2
            bar_y = self.rect.top - 10
            
            # draw bg
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, 5))
            # draw progres
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bar_width * progress, 5))

    def shoot_regular_bullet(self):
        bullet = RegularBullet(self, self.rect.centerx, self.rect.centery, self.angle)
        rad_angle = math.radians(self.angle)  # Convert angle to radians
        bullet.vel_x = math.cos(rad_angle) * bullet.speed  # Calculate x velocity based on angle
        bullet.vel_y = math.sin(rad_angle) * bullet.speed  # Calculate y velocity based on angle
        self.game.all_sprites.add(bullet)
        self.player_bullets.add(bullet)

    def shoot_special_bullet(self):
        bullet = SpecialBullet(self.rect.centerx, self.rect.centery, self.angle)
        rad_angle = math.radians(self.angle)  # Convert angle to radians
        bullet.vel_x = math.cos(rad_angle) * bullet.speed  # Calculate x velocity based on angle
        bullet.vel_y = math.sin(rad_angle) * bullet.speed  # Calculate y velocity based on angle
        self.game.all_sprites.add(bullet)
        self.player_bullets.add(bullet)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Calculate the time elapsed since the last shot
        time_since_last_shot = current_time - self.last_shot_time

        if keys[pygame.K_SPACE] and time_since_last_shot >= 500:  # Shoot only if 500 milliseconds (0.5 second) have passed since the last shot
            self.shoot_regular_bullet()  # Shoot regular bullet when space key is pressed
            PLAYER_CHANNEL.play(PLAYER_BULLET_MUSIC)
            self.last_shot_time = current_time  # Update the last shot time

        elif keys[pygame.K_LSHIFT] and time_since_last_shot >= 500:
            self.shoot_special_bullet()
            PLAYER_CHANNEL.play(PLAYER_BULLET_MUSIC)
            self.last_shot_time = current_time  # Update the last shot time
        
        if keys[pygame.K_e] and (current_time - self.last_dash_time) >= self.dash_cooldown:
            self.dash()
            DASH_CHANNEL.play(DASH_MUSIC)
            self.last_dash_time = current_time

    def wrap_around_screen(self):
        if self.rect.right < 0:
            self.rect.left = WIN_WIDTH
        if self.rect.left > WIN_WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = WIN_HEIGHT
        if self.rect.top > WIN_HEIGHT:
            self.rect.bottom = 0

    def decelerate(self):
        self.velocity *= self.deceleration
        if self.velocity.length() < 0.1:  # If the velocity is very small, make it zero
            self.velocity = pygame.math.Vector2(0, 0)

    def turnRight(self):
        self.angle += 5 # Adjust rotation speed as needed
        if self.angle > 360:
            self.angle -= 360

    def turnLeft(self):
        self.angle -= 5  # Adjust rotation speed as needed
        if self.angle < 0:
            self.angle += 360

    def moveForward(self):
        rad_angle = math.radians(self.angle)  # Convert angle to radians
        acceleration_vector = pygame.math.Vector2(math.cos(rad_angle), math.sin(rad_angle)) * self.acceleration
        self.velocity += acceleration_vector

    def rotate(self):
        original_center = self.rect.center  # Save the sprite's center
        self.image = pygame.transform.rotate(self.image, -self.angle)  # Rotate the original image
        self.rect = self.image.get_rect(center=original_center)  # Create a new rect with the old center

    #function to make player move based on arrow keys
    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.turnLeft()
        if keys[pygame.K_RIGHT]:
            self.turnRight()
        if keys[pygame.K_UP]:
            self.moveForward()
  
    def collide(self, spriteGroup):
        current_time = pygame.time.get_ticks()
        for sprite in spriteGroup:
            distance = math.sqrt((self.rect.centerx - sprite.rect.centerx) ** 2 + (self.rect.centery - sprite.rect.centery) ** 2)
            collision_threshold = max(self.rect.width, self.rect.height) / 2 + max(sprite.rect.width, sprite.rect.height) / 2 - 2 * TILESIZE
            
            # Check if within collision threshold and not currently invulnerable
            if distance < collision_threshold and current_time > self.damage_loop + 3000:  # Assuming 3000 ms invulnerability
                self.lives -= 1
                PLAYER_DESTROYED_CHANNEL.play(PLAYER_DESTROYED_MUSIC)
                self.damage_loop = current_time  # Reset invulnerability timer
                
                if self.lives <= 0:
                    self.kill()
                    self.game.playing = False
                    break
            
class RegularBullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
        self.angle = angle  # Store the angle passed from the player
        self.vel_x = math.cos(math.radians(self.angle)) * self.speed  # Calculate x velocity based on angle
        self.vel_y = math.sin(math.radians(self.angle)) * self.speed  # Calculate y velocity based on angle
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        #self.collide(self.game.asteroids)
        # destroy bullet exists for more than 2 seconds
        if pygame.time.get_ticks() - self.creation_time > 2000: 
            self.kill()

        # leaves the screen = reenters from the opposite side
        if self.rect.bottom < 0: 
            self.rect.y = WIN_HEIGHT
            self.rect.x = WIN_WIDTH - self.rect.x
        if self.rect.right < 0:
            self.rect.y = WIN_HEIGHT - self.rect.y
            self.rect.x = WIN_WIDTH
        if self.rect.top > WIN_HEIGHT:
            self.rect.y = 0
            self.rect.x = WIN_WIDTH - self.rect.x
        if self.rect.left > WIN_WIDTH:
            self.rect.y = WIN_HEIGHT - self.rect.y
            self.rect.x = 0

class SpecialBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(SPECIAL_BULLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = SPECIAL_BULLET_SPEED
        self.angle = angle  # store the angle passed from the player
        self.vel_x = math.cos(math.radians(self.angle)) * self.speed  # calculate x velocity based on angle
        self.vel_y = math.sin(math.radians(self.angle)) * self.speed  # calculate y velocity based on angle
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # destroy bullet exists for more than 2 seconds
        if pygame.time.get_ticks() - self.creation_time > 2000: 
            self.kill()

        # leaves the screen = reenters from the opposite side
        if self.rect.bottom < 0: 
            self.rect.y = WIN_HEIGHT
            self.rect.x = WIN_WIDTH - self.rect.x
        if self.rect.right < 0:
            self.rect.y = WIN_HEIGHT - self.rect.y
            self.rect.x = WIN_WIDTH
        if self.rect.top > WIN_HEIGHT:
            self.rect.y = 0
            self.rect.x = WIN_WIDTH - self.rect.x
        if self.rect.left > WIN_WIDTH:
            self.rect.y = WIN_HEIGHT - self.rect.y
            self.rect.x = 0
        
        
