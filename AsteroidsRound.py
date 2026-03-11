import pygame
import sys
import time

from player import *
from ship import *
from config import *
from asteroid import *
from powerups import *
from leaderboard import *
from explosion import *

class Game:
    asteroid_timer = 0
    asteroid_spawn_delay = 0.7

    def __init__(self, selected_ship=0):
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

        self.selected_ship = selected_ship

        self.background = pygame.image.load('Images/backgrounds/space-backgound.png').convert_alpha()
        self.background = pygame.transform.scale(self.background, (WIN_WIDTH, WIN_HEIGHT))
        stars_image = pygame.image.load('Images/backgrounds/space-stars.png')
        self.bg_stars = pygame.transform.scale(stars_image, (WIN_WIDTH, WIN_HEIGHT))
        self.bg_stars_x1 = 0
        self.bg_stars_x2 = WIN_WIDTH

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('Galaxus-z8Mow.ttf', 32)
        self.running = True

        

        # all variables for the ship class
        self.game_timer = 0
        self.spawn_timer_ship = 0
        self.spawn_delay_ship = 30
        self.spawn_delay_reg_bullet = 2
        self.spawn_delay_sp_bullet = 13

        #init sprite group
        self.ships = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.ship_bullets = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()

        # update all variables
        self.spawn_timer_powerup = 0

    def new(self):
        
        #new game
        self.playing = True

        #reset asteroid timer and spawn delay
        self.asteroid_timer = 0
        self.asteroid_spawn_delay = 1

        # Clear existing asteroid sprites
        self.asteroids.empty()

        #take all sprites and bunch them together so we can update all at once if needed
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()

        #create player at middle of screen
        ship_image_list = SHIP_A
        if self.selected_ship == 1:
            ship_image_list = SHIP_B
        elif self.selected_ship == 2:
            ship_image_list = SHIP_C
        elif self.selected_ship == 3:
            ship_image_list = SHIP_D

        self.player = Player(self, (WIN_WIDTH/TILESIZE)/2, (WIN_HEIGHT/TILESIZE)/2, ship_image_list)


    
    def events(self):
        for event in pygame.event.get():
            #when you x-out of window, game quits
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        #game loop updates
        self.all_sprites.update()
        self.update_background()
        self.spawn_timer_ship += 1
        self.game_timer += 1
        self.spawn_timer_powerup += 1
        self.asteroid_timer += 0.5
 
        self.asteroid_alg()
        # check all collision for asteroid
        for asteroid in self.asteroids:
            # collision with player bullets
            if asteroid.check_collision(self.player_bullets):
                self.play_explosion(asteroid.rect.center, asteroid.size)
                if asteroid.width != SM_ASTEROID_SIZE:
                    self.player.score += 10
                    new_size = asteroid.getSizeBelow()
                    new_x, new_y = asteroid.rect.centerx, asteroid.rect.centery
                    self.spawn_asteroid(new_size, new_x, new_y)
                    self.spawn_asteroid(new_size, new_x, new_y)
                else: # small asteroid - no split - extra points
                    self.player.score += 20
            # collision with alien ship bullets no points for player
            if asteroid.check_collision(self.ship_bullets):
                self.play_explosion(asteroid.rect.center, asteroid.size)
                if asteroid.width != SM_ASTEROID_SIZE:
                    new_size = asteroid.getSizeBelow()
                    new_x, new_y = asteroid.rect.centerx, asteroid.rect.centery
                    self.spawn_asteroid(new_size, new_x, new_y)
                    self.spawn_asteroid(new_size, new_x, new_y)
            # collision with alien ship itself, no points for player, and do not destroy alien ship
            if asteroid.check_collision(self.ships, False):
                self.play_explosion(asteroid.rect.center, asteroid.size)
                if asteroid.width != SM_ASTEROID_SIZE:
                    new_size = asteroid.getSizeBelow()
                    new_x, new_y = asteroid.rect.centerx, asteroid.rect.centery
                    self.spawn_asteroid(new_size, new_x, new_y)
                    self.spawn_asteroid(new_size, new_x, new_y)
        
        # check all collision for alien ship ~ in our version, alien ships plow through asteroids
        for ship in self.ships:
            if ship.check_collision(self.player_bullets):
                self.play_explosion(ship.rect.center, 60)
                self.player.score += 30

        # move the ship
        for ship in self.ships:
            ship.spawn_timer_sp_bullet += 1
            ship.spawn_timer_reg_bullet += 1
            ship.move()
            for bullet in ship.ship_sp_bullets:
                bullet.update_dir(self.player)

            # start shooting for regular bullet
            if ship.spawn_timer_reg_bullet >= self.spawn_delay_reg_bullet * FPS:
                ship.shoot_reg_bullet()
                ship.spawn_timer_reg_bullet = 0
            # start shooting for special bullet
            if ship.spawn_timer_sp_bullet >= self.spawn_delay_sp_bullet * FPS:
                ship.shoot_sp_bullet()
                ship.spawn_timer_sp_bullet = 0

        # check if player obtained the powerup
        for powerup in self.powerups:
            powerup.update()

        # create the ship based on time interval
        if self.spawn_timer_ship >= self.spawn_delay_ship * FPS:
            self.spawn_timer_ship = 0
            self.spawn_ship()
            SHIP_CHANNEL.play(SHIP_MUSIC)

        # increase difficulty - every one minute increase difficulty and both ship and bullet time of spawn decrease by 5
        if self.game_timer >= 60 and self.spawn_delay_sp_bullet > 30:
            #add a screen display of difficult level currently - to do
            if self.spawn_delay_ship > 25:
                self.spawn_delay_ship -= 5
                self.spawn_delay_reg_bullet -= 5
            self.spawn_delay_sp_bullet -= 5
            
            #points given each minute
            self.player.score+=500
            self.game_timer = 0
        
        # spawn powerups based off the game time
        if self.spawn_timer_powerup >= SPAWN_DELAY_POWERUP * FPS:
            powerup = Powerups(self.all_sprites, self.player)
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)
            self.spawn_timer_powerup = 0
            
        
        
    #create background screen for game
    def draw(self):
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.bg_stars, (self.bg_stars_x1 ,0))
        self.screen.blit(self.bg_stars, (self.bg_stars_x2 ,0))
        self.all_sprites.draw(self.screen) 

        # draw player cooldown bar
        self.player.draw_cooldown_bar(self.screen)
        
        self.clock.tick(FPS) #update the screen based on FPS
        minutes = self.game_timer // (60 * FPS)
        seconds = (self.game_timer // FPS) % 60

        # draw clock
        time_text = self.font.render(f"Time: {minutes:02}-{seconds:02}", True, WHITE)
        time_rect = time_text.get_rect(topright=(WIN_WIDTH - 10, 10))
        self.screen.blit(time_text, time_rect)

        lives_text = self.font.render('Lives: ' + str(self.player.lives), False, WHITE)
        score_text = self.font.render('Score: ' + str(self.player.score), False, WHITE)
        
        # Draw the lives text
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (10,40))
        pygame.display.update()

    def update_background(self):
        # Move backgrounds to the left
        self.bg_stars_x1 -= 1  # Adjust speed as necessary
        self.bg_stars_x2 -= 1
        
        # If the first image is completely off-screen
        if self.bg_stars_x1 + WIN_WIDTH < 0:
            self.bg_stars_x1 = WIN_WIDTH
            
        # If the second image is completely off-screen
        if self.bg_stars_x2 + WIN_WIDTH < 0:
            self.bg_stars_x2 = WIN_WIDTH

    def spawn_ship(self):
        # Create a new ship and add it to the groups
        ship = Ships(self.all_sprites, self.ship_bullets)
        self.all_sprites.add(ship)
        self.ships.add(ship)
        
    def spawn_asteroid(self, size, x = None, y = None):
        asteroid = Asteroid(self, size, x, y)
        self.all_sprites.add(asteroid)
        self.asteroids.add(asteroid)
        
    def asteroid_alg(self):
        size = random.choice([BIG_ASTEROID_SIZE, MED_ASTEROID_SIZE, SM_ASTEROID_SIZE])
        current_minute = self.game_timer // (60 * FPS) 

        if self.asteroid_timer >= self.asteroid_spawn_delay * FPS:
            if current_minute == 1:
                self.asteroid_spawn_delay = 0.6
                self.spawn_asteroid(size)
                self.spawn_asteroid(size)
                self.spawn_asteroid(BIG_ASTEROID_SIZE)
            elif current_minute == 2:
                self.asteroid_spawn_delay = 0.4
                self.spawn_asteroid(size)
                self.spawn_asteroid(size)
                self.spawn_asteroid(BIG_ASTEROID_SIZE)
            elif current_minute == 3:
                self.spawn_asteroid(MED_ASTEROID_SIZE)
                self.spawn_asteroid(SM_ASTEROID_SIZE)
                self.spawn_asteroid(BIG_ASTEROID_SIZE)
            elif current_minute == 4:
                self.asteroid_spawn_delay = 0.3
                self.spawn_asteroid(SM_ASTEROID_SIZE)
                self.spawn_asteroid(BIG_ASTEROID_SIZE)
                self.spawn_asteroid(BIG_ASTEROID_SIZE)
            elif current_minute == 6:
                self.asteroid_spawn_delay = 0.2
                self.spawn_asteroid(SM_ASTEROID_SIZE)
                self.spawn_asteroid(MED_ASTEROID_SIZE)
                self.spawn_asteroid(BIG_ASTEROID_SIZE)
                self.spawn_asteroid(BIG_ASTEROID_SIZE)
            else:
                self.spawn_asteroid(size)
                self.spawn_asteroid(size)
                self.spawn_asteroid(size)
            self.asteroid_timer = 0  # Reset the timer after spawning an asteroid
    

    def updateLeaderboard(self):

        leaderboard = LeaderBoard()
        leaderboard.save_highscore(self.player.score)
        if (leaderboard.check_new_highscore(self.player.score)):
           # t_end = time.time() + 3
           # while time.time() < t_end:
               # self.screen.blit(self.background, (0,0))
                #self.screen.blit(self.bg_stars, (self.bg_stars_x1 ,0))
                #s#elf.screen.blit(self.bg_stars, (self.bg_stars_x2 ,0))
                #s#e#lf.all_sprites.update()
                #self.update_background()
                #self.all_sprites.draw(self.screen) 

                text_surface = self.font.render("NEW HIGHSCORE!", True, (255, 255, 255))  # Black text

                # Center text
                text_rect = text_surface.get_rect(center=(WIN_WIDTH//2, (WIN_HEIGHT//2)-100))
                self.screen.blit(text_surface, text_rect)

                # Update the display 
               # pygame.display.update()


    def game_over_screen(self):
        self.screen.fill((0, 0, 0))  # Fill screen with black color
        self.updateLeaderboard()
        game_over_text = self.font.render("Game Over", True, (255, 255, 255))
        score_text = self.font.render("Score: " + str(self.player.score), True, (255, 255, 255))
        restart_text = self.font.render("Press R to restart", True, (255, 255, 255))
        menu_text = self.font.render("Press Q for menu", True, (255, 255, 255))  
        # Position text on the screen
        game_over_rect = game_over_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
        score_rect = score_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2-50))
        restart_rect = restart_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 50))
        menu_rect = menu_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 100))  # Adjust position as needed
        # Blit text onto the screen
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(menu_text, menu_rect) 
        pygame.display.flip()

    def play_explosion(self, position, size):
        explosion = Explosion(position, size)
        self.all_sprites.add(explosion)

        
    def main(self):
    # Start the background music
        MUSIC_CHANNEL.play(BACKGROUND_MUSIC, loops=-1)

        while self.running:
        # Start a new game
            self.new()

        # Game loop
            while self.playing:
                self.events()
                self.update()
                self.draw()
                self.player_bullets.update()

            # Check for game over condition
                if self.player.lives <= 0:
                    
                    self.game_timer = 0   # Reset game time to 0:00
                    self.playing = False  # Exit the game loop

        # Display game over screen
            self.game_over_screen()

        # Wait for player input to restart or quit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        self.running = False
                        return 0
                        
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:  # Restart the game
                            waiting = False
                        elif event.key == pygame.K_q:  # Quit the game
                            waiting = False
                            self.running = False
                            return 0


    # Stop music before quitting
        MUSIC_CHANNEL.stop()
        pygame.quit()
        sys.exit()

        return 0

