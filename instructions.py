import pygame
from button import Button
import config
from button import *

class InstructionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        # Semi-transparent background for submenu
        self.submenu_bg = pygame.Surface((500, 600))  # Smaller than the full screen
        self.submenu_bg.fill((50, 50, 50))  # Dark grey background
        self.submenu_bg.set_alpha(180)  # Semi-transparent
        self.submenu_rect = self.submenu_bg.get_rect(center=(config.WIN_WIDTH // 2, config.WIN_HEIGHT // 2))
        stars_image = pygame.image.load('Images/backgrounds/space-stars.png')
        self.bg_stars = pygame.transform.scale(stars_image, (WIN_WIDTH, WIN_HEIGHT))
        self.font = pygame.font.Font('Galaxus-z8Mow.ttf', 24)

        # init vars for background movement
        self.bg_stars_x1 = 0
        self.bg_stars_x2 = WIN_WIDTH

        # Semi-transparent background for submenu
        self.message_box = pygame.Surface((340, 500))  # Smaller width, enough for text
        self.message_box.fill((50, 50, 50))  # Dark grey background
        self.message_box.set_alpha(180)  # Semi-transparent
        self.message_box_rect = self.message_box.get_rect(topright=(WIN_WIDTH - 50, 100))
        self.current_message = None  # Store the current message to display

        # Define buttons
        button_y_start = 100  # Starting y-position of the first button
        self.objButton = Button((100, button_y_start), (200, 50), WHITE, 'Objectives')
        self.controlsButton = Button((100, button_y_start + 60), (200, 50), WHITE, 'Controls')
        self.mechanicsButton = Button((100, button_y_start + 120), (300, 50), WHITE, 'Gameplay Mechanics')
        self.powerupsButton = Button((100, button_y_start + 180), (200, 50), WHITE, 'Powerups')
        self.scoringButton = Button((100, button_y_start + 300), (200, 50), WHITE, 'Scorings')
        self.strategyButton = Button((100, button_y_start + 240), (200, 50), WHITE, 'Strategies')
        self.exitButton = Button((100, button_y_start + 360), (200, 50), WHITE, 'Return')
        self.p1button = Button((100, button_y_start + 60), (250, 50), WHITE, 'P1 Mechanics')
        self.p2button = Button((100, button_y_start + 120), (250, 50), WHITE, 'P2 Mechanics')
        self.backbutton = Button((100, button_y_start + 420), (200, 50), WHITE, 'Go back')
        self.singlebutton = Button((100, button_y_start + 60), (250, 50), WHITE, 'Single Player')
        self.coopbutton = Button((100, button_y_start + 120), (250, 50), WHITE, 'Multi Player')

        # Initial visibility of other buttons is False
        self.initial_buttons_visible = True
        self.coop_button_visible = False
        self.self_button_visible = False
        self.control_visible = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.exitButton.is_clicked(event):
                        self.running = False
                    if self.initial_buttons_visible:
                        if self.singlebutton.is_clicked(event):
                            self.self_button_visible = True
                            self.initial_buttons_visible = False
                        elif self.coopbutton.is_clicked(event):
                            self.coop_button_visible = True
                            self.initial_buttons_visible = False
                            

            self.update_background()
            self.screen.fill((0, 0, 0))  # Clear the screen or fill with base color
            self.screen.blit(self.bg_stars, (self.bg_stars_x1, 0))
            self.screen.blit(self.bg_stars, (self.bg_stars_x2, 0))

            self.draw_transparent_overlay()  # Draw the transparent overlay

            if self.current_message:  # Check if there is a message to display
                self.display_message(self.current_message)

            # Control visibility of each button group
            if self.initial_buttons_visible:
                self.singlebutton.draw(self.screen, BLACK)
                self.coopbutton.draw(self.screen, BLACK)
                self.exitButton.draw(self.screen, BLACK)
            elif self.self_button_visible:
                self.draw_game_buttons()
                self.scoringButton.draw(self.screen, BLACK)
                self.handle_button_click_single(event)
            elif self.coop_button_visible:
                self.draw_game_buttons()
                self.handle_button_click_coop(event)
            elif self.control_visible:
                self.p1button.draw(self.screen, BLACK)
                self.p2button.draw(self.screen, BLACK)
                self.backbutton.draw(self.screen, BLACK)
                self.handle_button_click_controls(event)
            
            pygame.display.update()

    def update_background(self):
        self.bg_stars_x1 -= 1  # Adjust speed as necessary
        self.bg_stars_x2 -= 1
        
        # Reset positions to loop the background
        if self.bg_stars_x1 + WIN_WIDTH < 0:
            self.bg_stars_x1 = WIN_WIDTH
            
        if self.bg_stars_x2 + WIN_WIDTH < 0:
            self.bg_stars_x2 = WIN_WIDTH

    def handle_button_click_single(self, event):
        if self.backbutton.is_clicked(event):
            self.initial_buttons_visible = True
            self.self_button_visible = False
        elif self.objButton.is_clicked(event):
            self.current_message = "The main goal of survival mode of Asteroids+ is to score as many points as possible by destroying asteroids and flying saucers."
        elif self.controlsButton.is_clicked(event):
            self.current_message = (
                "Left and Right key: You can rotate your spaceship left or right to aim at the asteroids.\n"
                "Upward key: This button moves your spaceship forward in the direction it's pointing.\n"
                "Movement is based on real physics, so you will continue drifting in one direction until you apply thrust in another direction.\n"
                "Space Key: Shoots bullets from your spaceship to break the asteroids into smaller pieces or destroy them entirely."
            )   
        elif self.mechanicsButton.is_clicked(event):
            self.current_message = (
                "You have three lives to start with, and collision with any asteroid, flying saucers, or their bullets will deduct a life. After each collision, there will be a three second invulnerability.\n"
                "The game field is a wrap-around screen, meaning if you go off one side, you reappear on the opposite side.\n"
                "Asteroids come in various sizes. Large asteroids break into two medium ones when shot, and medium ones break into two small ones. Small asteroids disappear when shot.\n"
                "Occasionally, a flying saucer will appear and shoot at you, one kind of bullet will go in a random direction while another kind will target you, which can also be destroyed for extra points.\n"
            )
        elif self.powerupsButton.is_clicked(event):
            self.current_message = (
                "They will spawn once in a while randomly, and picking it up will result in different effects\n"
                "Shield: provides invulnerability for five seconds\n"
                "Bomb: destroys everything on the screen, but no score will be obtained\n"
                "Plus sign: gains an additional life\n"
            )
        elif self.scoringButton.is_clicked(event):
            self.current_message = (
                "Large asteroids usually score the least points, with the point value increasing for medium and then small asteroids\n"
                "Destroying a flying saucer also scores points, typically higher than any asteroids\n"
            )
        elif self.strategyButton.is_clicked(event):
            self.current_message = (
                "Stay near the center of the screen to avoid wrapping into a dangerous situation\n"
                "Focus on controlling your speed and direction since momentum can make your ship difficult to control\n"
                "It’s often safer to pick off asteroids one at a time rather than shooting wildly\n"
            )

    def handle_button_click_coop(self, event):
        if self.backbutton.is_clicked(event):
            self.initial_buttons_visible = True
            self.coop_button_visible = False
        elif self.objButton.is_clicked(event):
            self.current_message = "The main goal of Co-op mode of Asteroids+ is two people combat to survive the longest"
        elif self.controlsButton.is_clicked(event):
            self.coop_button_visible = False
            self.control_visible = True
        elif self.mechanicsButton.is_clicked(event):
            self.current_message = (
                "You have three lives to start with, and collision with any asteroid or bullets from each other. After each collision, there will be a three second invulnerability.\n"
                "The game field is a wrap-around screen, meaning if you go off one side, you reappear on the opposite side.\n"
                "Asteroids come in various sizes. Large asteroids break into two medium ones when shot, and medium ones break into two small ones. Small asteroids disappear when shot.\n"
                "Players are able to shoot each other, but bullets will only be able to shoot every five seconds, the main objective is to dodge\n"
                "Players cannot collide with each other\n"
            )
        elif self.powerupsButton.is_clicked(event):
            self.current_message = (
                "They will spawn once in a while randomly, and picking it up will result in different effects\n"
                "Shield: provides invulnerability for five seconds\n"
                "Bomb: destroys everything on the screen, but no score will be obtained\n"
                "Plus sign: gains an additional life\n"
            )
        elif self.strategyButton.is_clicked(event):
            self.current_message = (
                "Stay near the center of the screen to avoid wrapping into a dangerous situation\n"
                "Focus on controlling your speed and direction since momentum can make your ship difficult to control\n"
            )

    def handle_button_click_controls(self, event):
        if self.p1button.is_clicked(event):
            self.current_message = (
                "Left and Right key: You can rotate your spaceship left or right to aim at the asteroids.\n"
                "Upward key: This button moves your spaceship forward in the direction it's pointing.\n"
                "Movement is based on real physics, so you will continue drifting in one direction until you apply thrust in another direction.\n"
                "Space Key: Shoots bullets from your spaceship to break the asteroids into smaller pieces or destroy them entirely.\n"
                "Shift Key: Changes ships and shoots faster bullet than the main ship"
            )  
        elif self.p2button.is_clicked(event):
            self.current_message = (
                "A and D: You can rotate your spaceship left or right to aim at the asteroids.\n"
                "W: This button moves your spaceship forward in the direction it's pointing.\n"
                "Movement is based on real physics, so you will continue drifting in one direction until you apply thrust in another direction.\n"
                "Shift key: Shoots bullets from your spaceship to break the asteroids into smaller pieces or destroy them entirely."
            )  
        elif self.backbutton.is_clicked(event):
            self.coop_button_visible = True
            self.control_visible = False

    def draw_game_buttons(self):
        self.objButton.draw(self.screen, BLACK)
        self.controlsButton.draw(self.screen, BLACK)
        self.mechanicsButton.draw(self.screen, BLACK)
        self.powerupsButton.draw(self.screen, BLACK)
        self.strategyButton.draw(self.screen, BLACK)
        self.backbutton.draw(self.screen, BLACK)

    def display_message(self, message):
        max_width = self.message_box_rect.width - 20  # Allow some margin for text wrapping
        line_spacing = 5  # Additional space between lines for readability
        y_offset = 20  # Start drawing text from this y-offset from the top of the message box

        # Split message into lines and then into words
        words_in_lines = [line.split(' ') for line in message.split('\n')]
        simulated_surface = pygame.Surface((self.message_box_rect.width, 1000))  # Temporary surface to simulate rendering
        total_height = y_offset  # Initial height with the top offset

        # Simulate rendering to calculate total height required
        for words in words_in_lines:
            current_line = ""
            for word in words:
                test_line = current_line + word + ' '
                if self.font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    # If the line is too long, render it to get the height
                    text_surface = self.font.render(current_line, True, (255, 255, 255))
                    line_height = text_surface.get_height() + line_spacing
                    total_height += line_height
                    current_line = word + ' '

            # Add the last line's height
            if current_line:
                text_surface = self.font.render(current_line, True, (255, 255, 255))
                line_height = text_surface.get_height() + line_spacing
                total_height += line_height

        # Create a new message box surface with calculated height, filled black
        self.message_box = pygame.Surface((self.message_box_rect.width, total_height))
        self.message_box.fill((0, 0, 0))  # Set background to black
        self.message_box.set_alpha(255)  # Opaque surface

        # Actual rendering of the text on the new surface
        y_offset = 20  # Reset y_offset for rendering
        for words in words_in_lines:
            current_line = ""
            for word in words:
                test_line = current_line + word + ' '
                if self.font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    text_surface = self.font.render(current_line, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(topleft=(10, y_offset))
                    self.message_box.blit(text_surface, text_rect)
                    y_offset += text_surface.get_height() + line_spacing
                    current_line = word + ' '

            # Render the last line
            if current_line:
                text_surface = self.font.render(current_line, True, (255, 255, 255))
                text_rect = text_surface.get_rect(topleft=(10, y_offset))
                self.message_box.blit(text_surface, text_rect)
                y_offset += text_surface.get_height() + line_spacing

        # Blit the updated message box onto the screen at its specified position
        self.screen.blit(self.message_box, self.message_box_rect)


    def draw_transparent_overlay(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))  # Create a surface the size of the screen
        overlay.set_alpha(128)  # Set transparency: 0 is fully transparent, 255 is opaque
        overlay.fill((0, 0, 0))  # Fill with black color or any other color
        self.screen.blit(overlay, (0, 0))  # Draw the overlay on the screen
