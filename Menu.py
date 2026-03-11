import pygame
from AsteroidsRound import *
from shipSelectScreen import *
from button import *
from leaderboard import *
from instructions import *
from CoOp import *
import pygame.font
import feedparser

class Menu:
    def __init__(self):
        pygame.init()
        self.title = "Asteroids   Plus"
        self.title_font = pygame.font.Font('Galaxus-z8Mow.ttf', 100)
        self.title_text = self.title_font.render(self.title, True, WHITE)
        self.title_y = 150
        self.title_y_velocity = 0.20
        # load screen and images for background
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.background = pygame.image.load('Images/backgrounds/space-backgound.png').convert_alpha()
        self.background = pygame.transform.scale(self.background, (WIN_WIDTH, WIN_HEIGHT))
        stars_image = pygame.image.load('Images/backgrounds/space-stars.png')
        self.bg_stars = pygame.transform.scale(stars_image, (WIN_WIDTH, WIN_HEIGHT))
        self.shipicon = pygame.image.load('Images/ships/ship-a/ship-a-damaged.png')
        
        # init vars for background movement
        self.bg_stars_x1 = 0
        self.bg_stars_x2 = WIN_WIDTH
        # init clock for FPS
        self.clock = pygame.time.Clock()

        self.running = True
        self.playButton = Button((WIN_WIDTH/2 - 130, WIN_HEIGHT/2 - 150), (100, 100), WHITE, "PLAY")
        self.shipSelect = Button((WIN_WIDTH/2 -50, WIN_HEIGHT/2), (100, 100), WHITE, "SHIP", 'Images/ships/ship-a/ship-a-damaged.png')
        self.exitButton = Button((WIN_WIDTH/2 -50, WIN_HEIGHT/2 + 150), (100, 100), WHITE, "EXIT")
        self.statButton = Button((WIN_WIDTH/2 -50, WIN_HEIGHT/2 + 300), (100, 100), WHITE, "STATS")
        self.instructionsButton = Button((WIN_WIDTH - 120, WIN_HEIGHT - 70), (100, 50), WHITE, "Help")
        self.coOpButton = Button((WIN_WIDTH/2 + 20, WIN_HEIGHT/2 - 150), (100, 100), WHITE, "CO-OP")

        self.alert_message = self.fetch_alert()

        if self.alert_message:
            print("ALERT:", self.alert_message)

    #makes alert text fit on screen
    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            width, _ = font.size(test_line)

            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)
        return lines

    #fetches alert using feedparser
    def fetch_alert(self):
        try:
            feed = feedparser.parse("https://nitter.net/TempleAlert/rss")
            if feed.entries:
                return feed.entries[0].title
        except Exception as e:
            print("Alert fetch failed:", e)

        return None

    def draw(self):
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.bg_stars, (self.bg_stars_x1 ,0))
        self.screen.blit(self.bg_stars, (self.bg_stars_x2 ,0))

        #writes alert to the main window
        if self.alert_message:
            alert_font = pygame.font.Font(None, 36)

            lines = self.wrap_text(self.alert_message, alert_font, WIN_WIDTH - 40)

            y = WIN_HEIGHT - 750
            for line in lines:
                alert_surface = alert_font.render(line, True, (255, 0, 0))
                alert_rect = alert_surface.get_rect(center=(WIN_WIDTH/2, y))
                self.screen.blit(alert_surface, alert_rect)
                y += 35
        
        self.title_y += self.title_y_velocity
        if self.title_y >= WIN_HEIGHT - 635:
            self.title_y = WIN_HEIGHT - 635  # Limit the title's position to the bottom of the screen
            self.title_y_velocity = -0.20  # Reverse direction when reaching bottom
        elif self.title_y <= 150:
            self.title_y = 150  # Limit the title's position to the top of the screen
            self.title_y_velocity = 0.20 

        # Add the following lines
        title_rect = self.title_text.get_rect(center=(WIN_WIDTH/2, self.title_y)) 
        self.screen.blit(self.title_text, title_rect)

        self.clock.tick(FPS) #update the screen based on FPS
        pygame.mouse.set_visible(True)
        
        self.playButton.draw(self.screen, BLACK)
        self.shipSelect.draw(self.screen, BLACK)
        self.exitButton.draw(self.screen, BLACK)
        self.statButton.draw(self.screen,BLACK)
        self.instructionsButton.draw(self.screen,BLACK)
        self.coOpButton.draw(self.screen,BLACK)
    
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
    
    def show_instructions(self):
        inst_menu = InstructionsMenu(self.screen)
        inst_menu.run()

    def play(self):
        selected_ship = 0
        while True:
            m.draw()
            m.update_background()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()

                if self.playButton.is_clicked(event):
                        g = Game(selected_ship) #init Game class
                        g.new() #create a new game everytime we run
                        while g.running:
                            g.main()

                if self.shipSelect.is_clicked(event):
                    select = ShipSelection()
                    selected_ship = select.main()
                    while select.running:
                        select.main()

                if self.instructionsButton.is_clicked(event):
                    self.show_instructions()

                if self.statButton.is_clicked(event):
                    # exit
                    leaderboard = LeaderBoard()
                    while leaderboard.running:
                        leaderboard.view()
                        
                if self.coOpButton.is_clicked(event):
                        c = CoOp(selected_ship) #init Game class
                        c.new() #create a new game everytime we run
                        while c.running:
                            c.main()

                if self.exitButton.is_clicked(event):
                    # exit
                    pygame.quit()
                    exit()
        
        
m = Menu()
while m.running:
    m.play()
