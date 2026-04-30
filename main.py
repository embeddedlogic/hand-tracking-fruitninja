from cvzone.HandTrackingModule import HandDetector
import cv2
import random
import pygame
import sys

class HandTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.rgb_frame = None
        #fix camera quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.detector = HandDetector(detectionCon=0.65, maxHands=1)

        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()

    def read_frame(self):
        ret, self.frame = self.cap.read()
        self.hands, self.frame = self.detector.findHands(self.frame,flipType=True)
        #if hand is present in the frame store all 20 landmarks in lmlist
        if self.hands:
            lmlist = self.hands[0]['lmList']
            x8,y8 = lmlist[8][0], lmlist[8][1] 
            x7,y7 = lmlist[7][0], lmlist[7][1]
            
            #makes a circle to show the top of index finger
            #all the paremters
            #radius = 20 
            #color = 255,0,0
            #thickness is 2
            cv2.circle(self.frame,(x8,y8),20,(255,0,0),2)
            cv2.circle(self.frame,(x7,y7),20,(255,0,0),2)


        if ret is False:
            return False
            #flip the frame it can be like iphone video in way
            # if user swipes right it will be right and not inverse
        self.frame = cv2.flip(self.frame,1)

        # Changes the color of the frame from BGR to RGB
        # because OpenCV uses BGR and MediaPipe uses RGB
        self.rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        return True
    def fingertip_postion(self):
        pass

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
                     "1: Stand in front of the camera and make sure index finger is visible",
                     "2: Move your index finger to slice the fruit",
                     "3: Each fruit you slice gets you a point",
                     "4: Avoid bombs or the game ends",
                     "5: Keep your hand inside the camera view",
                     "6: Only one player hands should be in frame",
                     "7: Try to get the highest score possible",
                    ]
        #creating the back button for the play guide
        self.back_button = Button(150,50,"Back")
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
            #displays the  back button
        self.back_button.draw(screen)  
class Game:
    def __init__(self):
        pygame.init()
        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fruit Ninja")
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_start_time = None
        self.game_duration = 25
        self.score = 0

        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = 400

        self.fruit_images = {
            "apple": pygame.image.load("assets/images/apple.png"),
            "avocado": pygame.image.load("assets/images/avocado.png"),
            "banana": pygame.image.load("assets/images/banana.png"),
            "cherries": pygame.image.load("assets/images/cherries.png"),
            "lemon": pygame.image.load("assets/images/lemon.png"),
            "orange": pygame.image.load("assets/images/orange.png"),
            "pear": pygame.image.load("assets/images/pear.png"),
            "pineapple": pygame.image.load("assets/images/pineapple.png"),
            "tomato": pygame.image.load("assets/images/tomato.png"),
            "bomb": pygame.image.load("assets/images/bomb.png"),
        }

        for key in self.fruit_images:
            self.fruit_images[key] = pygame.transform.scale(
                self.fruit_images[key], (300, 150)
            )

        self.fruits = []

        self.menu = MainMenu(self.width, self.height)
        self.play_guide = PlayGuideScreen(self.width, self.height)
        self.tracker = HandTracker()
        self.state = "menu"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def get_remaining_time(self):
        if self.game_start_time is None:
            return self.game_duration

        elapsed_time = (pygame.time.get_ticks() - self.game_start_time) / 1000
        remaining_time = self.game_duration - elapsed_time

        if remaining_time <= 0:
            return 0

        return remaining_time

    def run_webcam_game(self):
       
        remaining_time = self.get_remaining_time()

        if remaining_time <= 0:
            self.state = "game_over"
            return

        if self.tracker.read_frame():
            frame = self.tracker.rgb_frame
            surface = pygame.image.frombuffer(
                frame.tobytes(),
                frame.shape[1::-1],
                "RGB"
            )

            surface = pygame.transform.scale(surface, (self.width, self.height))
            self.screen.blit(surface, (0, 0))

            font = pygame.font.SysFont(None, 55)

            # Score box
            pygame.draw.rect(self.screen, (0, 0, 0), (30, 30, 250, 60))
            score_text = font.render(
                f"Score: {self.score}",
                True,
                (255, 255, 255)
            )
            self.screen.blit(score_text, (45, 45))

            # Time
            time_text = font.render(
                f"Time: {int(remaining_time)}",
                True,
                (255, 255, 255)
            )
            self.screen.blit(time_text, (1065, 45))

            current_time = pygame.time.get_ticks()

            if current_time - self.last_spawn_time > self.spawn_interval:
                self.spawn_fruits()
                self.last_spawn_time = current_time

            for fruit in self.fruits:
                fruit.move()
                fruit.draw(self.screen)

            if self.tracker.hands:
                lmlist = self.tracker.hands[0]['lmList']

                x8 = self.width - lmlist[8][0]
                y8 = lmlist[8][1]

                x7 = self.width - lmlist[7][0]
                y7 = lmlist[7][1]

                pygame.draw.line(
                    self.screen,
                    (255, 0, 0),
                    (x7, y7),
                    (x8, y8),
                    18
                )

                pygame.draw.line(
                    self.screen,
                    (255, 0, 0),
                    (x7, y7),
                    (x8, y8),
                    6
                )

                for fruit in self.fruits[:]:
                    fruit_width = fruit.image.get_width()
                    fruit_height = fruit.image.get_height()

                    hit_8 = (
                        x8 >= fruit.x and x8 <= fruit.x + fruit_width and
                        y8 >= fruit.y and y8 <= fruit.y + fruit_height
                    )

                    hit_7 = (
                        x7 >= fruit.x and x7 <= fruit.x + fruit_width and
                        y7 >= fruit.y and y7 <= fruit.y + fruit_height
                    )

                    if hit_8 or hit_7:
                        self.fruits.remove(fruit)
                        if fruit.type == "bomb":
                            self.state = "game_over"
                            return
                        else:
                            self.score += 1

        else:
            self.quit_game()

    def draw_game_over_screen(self):
        self.screen.fill((0, 0, 0))

        font_big = pygame.font.SysFont(None, 90)
        font_small = pygame.font.SysFont(None, 55)

        game_over_text = font_big.render("Game OVER", True, (255, 0, 0))
        score_text = font_small.render(f"Final Score: {self.score}", True, (255, 0, 0,))
        restart_text = font_small.render("Press R to Return to Main Screen",True,(255,0,0))

        self.screen.blit(game_over_text, (self.width // 2 - 220, self.height // 2 - 120))
        self.screen.blit(score_text, (self.width // 2 - 150, self.height // 2))
        self.screen.blit(restart_text, (self.width // 2 - 180, self.height // 2 + 140))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
             self.state = "menu"

    def spawn_fruits(self):
        #more bombs depedning on the users score
        if self.score >= 20:
            bomb_chance = 0.9
        elif self.score >= 10:
            bomb_chance = 0.85
        elif self.score >= 7:
            bomb_chance = 0.5
        elif self.score >= 4:
            bomb_chance = 0.3
        elif self.score >= 30:
            bomb_chance = 0.9
        else:
            bomb_chance = 0.2
        if random.random() < bomb_chance:
            fruit_type = "bomb"
        else:
            fruit_type = random.choice([
                "apple",
                "avocado",
                "bannana",
                "cherries",
                "lemon",
                "orange",
                "pear",
                "pinapple",
                "tomato"
            ])

       
        fruit_type = random.choice(list(self.fruit_images.keys()))
        fruit_image = self.fruit_images[fruit_type]
        fruit = Fruit(fruit_image, fruit_type)
        self.fruits.append(fruit)


    def run(self):
        while self.running:
            self.handle_events()

            if self.state == "menu":
                self.menu.draw(self.screen, self.width, self.height)

                if self.menu.play_button.is_pressed():
                    self.state = "playing"
                    self.game_start_time = pygame.time.get_ticks()
                    self.score = 0
                    self.fruits = []

                elif self.menu.play_guide_button.is_pressed():
                    self.state = "play_guide"

                elif self.menu.quit_button.is_pressed():
                    self.quit_game()

            elif self.state == "play_guide":
                self.play_guide.show_play_guide(self.screen)

                if self.play_guide.back_button.is_pressed():
                    self.state = "menu"

            elif self.state == "playing":
                self.run_webcam_game()

            elif self.state == "game_over":
                self.draw_game_over_screen()

            pygame.display.flip()
            self.clock.tick(60)

        self.quit_game()

    def quit_game(self):
        self.tracker.release_camera()
        pygame.quit()
        sys.exit()
class Fruit:
    def __init__(self,image,fruit_type):
        #storing the image
        # x will pick a random horizontal postion where the fruit appears
        #y is the starting vertical position so lowest is bottom of screen large number 
        #speed_x and speed_ y control how fast the fruit show move in the x and y direction. Controls the diagonal movement of fruits
        self.image = image
        self.type = fruit_type
        self.x = random.randint(150,980)       # avoids spawning too close 
        self.y = 770  # start near button of screen
        self.speed_x = random.randint(-2,2)      #control sideways movement 
        self.speed_y = random.randint(-25,-15)  #control how fast fruit goes upward
        self.gravity = 0.3 #pulling the fruit down
    def move(self):
        self.speed_y += self.gravity
        self.x += self.speed_x 
        self.y += self.speed_y  
    def draw(self,screen):
        screen.blit(self.image,(self.x,self.y))
        

game = Game()
game.run()