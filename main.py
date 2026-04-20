import cv2
import time
import math
import pygame, sys
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.rgb_frame = None

        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()

    def read_frame(self):
        ret, self.frame = self.cap.read()

        if ret is False:
            print("Cannot receive frame")
            return False

        # Changes the color of the frame from BGR to RGB
        # because OpenCV uses BGR and MediaPipe uses RGB
        self.rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        return True

    def show_frame(self):
        cv2.imshow("Frame", self.frame)

    def release_camera(self):
        self.cap.release()
        cv2.destroyAllWindows()
class Button:
    def __init__(self,x,y,text):
         #loading image from file path as a string
        self.image = pygame.image.load("assets/images/button_grey.png").convert_alpha()
        #get the buttons the same size 
        self.image = pygame.transform.scale(self.image,(300,90))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.text = text
        self.font = pygame.font.Font(None, 50)
        self.pressed = False
    def draw(self, window):
        # draw button image
        window.blit(self.image, self.rect)
        # render button label
        text_surface = self.font.render(self.text, True, "white")
        # center text on button
        text_rect = text_surface.get_rect(center=self.rect.center)
        # draw text on button
        window.blit(text_surface, text_rect)
    def is_pressed(self):
        #if mouse is clickin on the button right now if yes return true 
        # where mouse is on screen
        mouse_pos = pygame.mouse.get_pos()
        #if left mouse button pressed
        mouse_pressed = pygame.mouse.get_pressed()[0]
        #check if mouse cursor is around 
        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed and not self.pressed:
                self.pressed = True
                return True
            if not mouse_pressed:
                self.pressed = False
    
                return False
class MainMenu:
    def __init__(self, width, height):
        self.title = "Welcome to Fruit Ninja"
        self.title_font = pygame.font.Font(None, 150)

        self.background = pygame.image.load(
            "assets/images/pexels-jj-jordan-44924743-7780320.jpg"
        )
        self.background = pygame.transform.scale(self.background, (width, height))

        self.play_button = Button(width // 2, 300, "Play")
        self.play_guide_button = Button(width // 2, 380, "Play Guide")
        self.quit_button = Button(width // 2, 460, "Quit")

    def draw(self, screen, width, height):
        screen.blit(self.background, (0, 0))

        title_text = self.title_font.render(self.title, True, "white")
        title_rect = title_text.get_rect(center=(width // 2, 150))
        screen.blit(title_text, title_rect)

        self.play_button.draw(screen)
        self.play_guide_button.draw(screen)
        self.quit_button.draw(screen)
class PlayGuideScreen:
    #stores the background for the play guide screen
    def __init__(self,width,height):
        self.width = width 
        self.height = height
        self.play_guide_background = pygame.image.load(
            "assets/images/guide_background_blurred.png"
        )
        self.play_guide_background = pygame.transform.scale(self.play_guide_background,(width, height))
        self.rules =[
                     "1: Stand in front of the camera and make sure hand is visible",
                     "2: Move your hand to slice fruit to score points",
                     "3: Each fruit you slice earns you a score",
                     "4: Avoid bombs or the game ends",
                     "5: Slice multiple fruits for combo points",
                     "6: Keep your hand inside the camera view",
                     "7: Only one player should be in frame",
                     "8: Try to get the highest score possible",
                    ]
        #showing the image for the play guide
        # when user clicks play guide  will have another background
    def show_play_guide(self, screen):
        # drawing a brackgrunf to fill the screen
        #(0,0) this is the top right corner
        screen.blit(self.play_guide_background, (0, 0))
        #create font because pygame cant read strings
        font = pygame.font.SysFont(None,40)
        #starting vertical postion
        y = 120
        #shoe each rule
        for rule in self.rules:
            # converts the rules into something pygame can draw 
            #255 text color is white
            text = font.render(rule, True, (255, 255, 255))
            #draws the text on the screen
            #80 pixels from the left and y pixels down from the top
            screen.blit(text, (80, y))
            #so the rules dont overlap on each other
            y += 50          
class Game:
    def __init__(self):
        pygame.init()
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fruit Ninja")
        self.clock = pygame.time.Clock()
        self.running = True
        self.menu = MainMenu(self.width,self.height)
        self.play_guide = PlayGuideScreen(self.width, self.height)
        self.tracker = HandTracker()
        self.state = "menu"
        #Rules for the Play Guide

    def draw_play_guide(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 40)
        y = 100

        for rule in self.rules:
            text = font.render(rule, True, (255,255,255))
            self.screen.blit(text, (50, y))
            y += 50

        self.menu = MainMenu(self.width,self.height)
        self.tracker = HandTracker()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self):
        #self.state helps show which screen u want your game to show
        # menu will show the menu
        #play_guide will have the rules 
        #playing will run the game
        while self.running:
            self.handle_events()

            if self.state == "menu":
                self.menu.draw(self.screen, self.width, self.height)
            elif self.state == "play_guide":
               self.play_guide.show_play_guide(self.screen)
            #see if the buttons work
            if self.menu.play_button.is_pressed():
                self.state = "playing"
            elif self.menu.play_guide_button.is_pressed():
                self.state = "play_guide"
            elif self.state == "play_guide":
                self.play_guide.show_play_guide(self.screen)
            elif self.menu.quit_button.is_pressed():
                self.exit() 
            elif self.state == "playing":
                if not self.tracker.read_frame():
                    self.running = False

                # temporary test only
                self.tracker.show_frame()

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.running = False

            pygame.display.flip()
            self.clock.tick(60)

        self.quit_game()

    def quit_game(self):
        self.tracker.release_camera()
        pygame.quit()
        sys.exit()
        


game = Game()
game.run()