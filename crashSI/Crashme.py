import os, sys
import math
from random import randint, choice

import pygame 
from pygame.sprite import Sprite
from pygame import *
from pygame.locals import *
from vec2d import vec2d

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

class hourGlass(Sprite):
    """ An hourglass sprite; used to control pauses"""
    def __init__(self, screen, img_filename, init_position):
        """ Create a new hourglass.

        """
        Sprite.__init__(self)
        self.screen = screen
        self.pause = True
        self.base_image = self.base_image = pygame.image.load('hourGlassDown.png').convert_alpha()
        self.image = self.base_image
        self.pos = vec2d(init_position)
        self.image_w, self.image_h = self.image.get_size()
    def update(self):
        if(self.pause):
            self.pause = False;
            self.image = pygame.image.load('hourGlassUp.png').convert_alpha()        
        else:
            self.pause = True;
            self.image = pygame.image.load('hourGlassDown.png').convert_alpha()            
    def blitme(self):
        """ Blit the hourglass onto the screen that was provided in
            the constructor.
        """
        # The hourglass image is placed at self.pos.
        self.screen.blit(self.image, self.pos)
    def stop(self):
        if(not self.pause):
            self.update()
        

class Button(Sprite):
    """ A button sprite"""

    def __init__(self, screen, text, init_position):

        Sprite.__init__(self)
        self.screen = screen
        self.position = init_position
        self.text = text;
        self.pos = vec2d(init_position)
        img_filename = 'button' + text + '.png'
        self.image = pygame.image.load(img_filename).convert_alpha()
        self.image_w, self.image_h = self.image.get_size()
        self.screen.blit(self.image, self.position)
        self.text = ''

    def blitme(self):
        size = 15
        line = self.text.split('\n')
        while(len(line[0]) * size/2 > self.image_w):
            size -= 1
        self.screen.blit(self.image, self.pos)
        if(self.text != ''):
            write_to_button(self.text, self.screen, size, black, white, self)
        
        
class Car(Sprite):
    """ A car sprite."""
    def __init__(   
            self, screen, img_filename, init_position, 
            init_direction, mass, speed = 0, friction = 0, axes_mutable = (0,0)):
        """ Create a new Car.
            screen: 
                The screen on which the car lives (must be a 
                pygame Surface object, such as pygame.display)            
            img_filaneme: 
                Image file for the car.            
            init_position:
                A vec2d or a pair specifying the initial position
                of the car on the screen.            
            init_direction:
                A vec2d or a pair specifying the initial direction
                of the car. Must have an angle that is a 
                multiple of 45 degres.            
            speed: 
                Car speed, in pixels/millisecond (px/ms)
        """
        Sprite.__init__(self)
        
        self.screen = screen
        self.speed = speed
        self.mass = mass
        self.friction = friction
        self.axes_mutable = axes_mutable
        self.imgFileName = img_filename
        # base_image holds the original image
        self.base_image = pygame.image.load(self.imgFileName).convert_alpha()
        self.image = self.base_image
        self.image_w, self.image_h = self.image.get_size()
        
        # A vector specifying the car's position on the screen
        #
        self.pos = vec2d(init_position)

        # The direction is a normalized vector
        #
        self.direction = vec2d(init_direction).normalized()        
       
        
    def crash(self, other):
        """an Inelastic collision with another car, returns a new car wreck """
        wreck_x = (self.pos.x + other.pos.x) /2
        wreck_y = (self.pos.y + other.pos.y) /2
        wreck_direction = self.direction * self.speed + other.direction * other.speed
        wreck_mass = self.mass + other.mass
        wreck_speed = ((self.speed * self.mass) +
                       (other.speed * other.mass)) / wreck_mass
        wreck = Car(self.screen, 'crashSprite01.png', (wreck_x, wreck_y),
                    wreck_direction, wreck_mass, wreck_speed, 0.000006)
        return wreck
    
    def bump(self, other, spot, fric = 0.000006):
        total_mom = (self.direction * self.speed * self.mass) + (other.direction * other.speed * other.mass)
        distance = vec2d(spot) - self.pos
        self.friction = fric
        time = 800 #ms
        self.direction = distance.normalized()
        new_speed = (distance / time).get_length() + (0.5 * self.friction * time) 
        while(new_speed > self.speed):
            time += 100
            new_speed = (distance / time).get_length() + (0.5 * self.friction * time)
        self.speed = new_speed    
        if(distance.get_length() == 0):
            self.speed = 0  
            self.friction = 0
        else:
            if(self.mass > 100):
                self.imgFileName = 'damagedSprite00.png'
            else:
                self.imgFileName = 'bikerSpriteCrash00.png'
        remainder = total_mom - (self.direction * self.speed * self.mass)
        other.direction = remainder.normalized()
        other.speed = remainder.get_length() / other.mass 
        if(other.mass > 100):
            other.friction = fric
        else:
            other.friction = 0.0006
        
    def clone(self):
        new_car = Car(self.screen, self.imgFileName, self.pos, self.direction, self.mass, self.speed, self.friction, self.axes_mutable)
        return new_car
        

               
    def update(self, time_passed):
        """ Update the car.
        
            time_passed:
                The time passed (in ms) since the previous update.
        """
        # Make the car point in the correct direction.
        # Since our direction vector is in screen coordinates 
        # (i.e. right bottom is 1, 1), and rotate() rotates 
        # counter-clockwise, the angle must be inverted to 
        # work correctly.
        if(self.direction == vec2d(1,0)):#heading right
            self.image = pygame.image.load(self.imgFileName[:-6] + '00.png').convert_alpha() 
        elif(self.direction == vec2d(0,-1)):#heading up
            self.image = pygame.image.load(self.imgFileName[:-6] + '01.png').convert_alpha() 
        elif(self.direction == vec2d(-1,0)):#heading left
            self.image = pygame.image.load(self.imgFileName[:-6] + '10.png').convert_alpha()
        elif(self.direction == vec2d(0,1)):#heading down
            self.image = pygame.image.load(self.imgFileName[:-6] + '11.png').convert_alpha()
        elif(self.direction.get_angle() == -45):#heading right and up
            right = pygame.image.load(self.imgFileName[:-6] + '01.png').convert_alpha()
            self.image = transform.rotate(right, 10)
        elif(self.direction.get_angle() == -135):#heading left and up
            left = pygame.image.load(self.imgFileName[:-6] + '01.png').convert_alpha()
            self.image = transform.rotate(left, 10)        
        elif(self.direction.get_angle() == 45):#heading right and down
            right = pygame.image.load(self.imgFileName[:-6] + '11.png').convert_alpha()
            self.image = transform.rotate(right, 10)     
        elif(self.direction.get_angle() == 135):#heading left and down
            left = pygame.image.load(self.imgFileName[:-6] + '10.png').convert_alpha()
            self.image = transform.rotate(left, 10)   
        # Compute and apply the displacement to the position 
        # vector. The displacement is a vector, having the angle
        # of self.direction (which is normalized to not affect
        # the magnitude of the displacement)
        #
        if(self.friction > 0 and self.speed > 0.0):          
            deceleration = self.mass * self.friction * 0.01
            self.speed = self.speed - (deceleration * time_passed)             
        if(self.speed < 0):
            self.speed = 0
        displacement = vec2d(    
            self.direction.x * self.speed * time_passed,
            self.direction.y * self.speed * time_passed)       
        self.pos += displacement
        #print(self.speed)
        
        # When the image is rotated, its size is changed.
        # We must take the size into account for detecting 
        # collisions with the walls.
        #
        self.image_w, self.image_h = self.image.get_size()
        bounds_rect = self.screen.get_rect().inflate(
                        -self.image_w, -self.image_h)
        
        if (self.pos.x < bounds_rect.left - 50 or self.pos.x > bounds_rect.right):
            if (self.pos.y < bounds_rect.top or self.pos.y > bounds_rect.bottom):
                self.speed = 0
                self.friction = 10
    
    def printable(self):#prints a surface with the car's picture and stats    
        font = pygame.font.SysFont("buxton sketch", 14)
        image_s = transform.smoothscale(self.image,(int(self.image_w/2), int(self.image_h/2)))
        surface = pygame.surface.Surface((250,50),pygame.SRCALPHA, 32)        
        surface.blit(image_s, (0,0))
        text = "was"
        if(self.speed == 0):
            text += " at a stop;"
        else:
            text += " going " + str(round(self.speed,2) * 50) + "m/s;"
        text += " had a mass of " +str(self.mass) + " kg"
        alt_text = "had a momentum of " + str(round(self.speed * self.mass, 2)) + " kg.m/s"
        surface.blit(font.render(text, True, black),(35,0))
        surface.blit(font.render(alt_text, True, black),(35,14))
        
        return surface
    
    def blitme(self):
        """ Blit the car onto the screen that was provided in
            the constructor.
        """
        # The car image is placed at self.pos.
        # To allow for smooth movement even when the car rotates
        # and the image size changes, its placement is always
        # centered.
        #
        draw_pos = self.image.get_rect().move(
            self.pos.x - self.image_w / 2, 
            self.pos.y - self.image_h / 2)
        self.screen.blit(self.image, draw_pos)
class Counter():
    def __init__(self):
        self.count = 0
        self.spots_shown = False
        self.tutorial_shown = False  
        self.level_ready = False
        self.carpos = []
    #------------------ PRIVATE PARTS ------------------#
    
    

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.init()
font = pygame.font.Font(None,8)
clock = pygame.time.Clock()
played_levels = []
won_levels = []


def logo_screen():
    bg = pygame.image.load('csi.png')
    screen.blit(bg,bg.get_rect());
    pygame.display.flip()
    time.delay(1200)
    bg = pygame.image.load('opening_monologue.png')    
    screen.blit(bg,bg.get_rect()); 
    pos = []
    pos.append(150)
    pos.append(200)
    
    write_monologue("After acquiring your degree in applied mathematics\n"
                    "you become.... an insurance salesman.                  \n"
                    "No, not really; but you work for an insurance company,\n"
                    "spending your days checking claims.         \n"
                    "So when an opportunity comes up with the local police force\n"
                    "you inevitably take it."
                    ,screen, 25, white, black, pos)
    
    continue_button = Button(screen, 'Gen', (324,490))
    continue_button.text = "Continue"
    continue_button.blitme()   
    pygame.display.flip()
    while True:
        clock.tick(50)
        x,y = mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif(event.type == MOUSEBUTTONDOWN):
                if(within_boundaries((x,y), continue_button, False)):
                    intro_screen()    
    

def intro_screen():
    #Level selection etc
    background = pygame.image.load('intro_bg.png')
    screen.blit(background,background.get_rect());
    buttons = []
    buttons.append(Button(screen, 'Gen', (600,500)))
    for i in range(0,2):
        for j in range(0,4):
            buttons.append(Button(screen, 'Gen', (75 + j*175,50 + i * 75)))
    buttons.append(Button(screen, 'Gen', (250,200))) 
    buttons.append(Button(screen, 'Gen', (425,200)))  
    button_score_bar = Button(screen, 'ScoreBar', (100,525))   
    write_to_button(("EXIT"), screen, 35, black, white,buttons[0])
    score_button = Button(screen, 'InfoScreen', (100,300))
    rank = ''
    if(len(won_levels) < 3): rank = "Rookie"
    elif(len(won_levels) < 6): rank = "Amateur"
    elif(len(on_levels) < 9): rank = "Nerd"
    else: rank = "Veteran"
    write_to_button(("Current Rank: "+rank+"\nLevels Completed: " + 
                     str(len(won_levels)))+"/10", screen, 20, black, 
                    white,score_button)
    for i in range (1,11):
                if(i in won_levels):
                    write_to_button((str(i) +  " - completed!"), screen, 15, 
                                    black, white,buttons[i])
                else:
                    write_to_button(("Level " + str(i)), screen, 30, black, 
                                    white,buttons[i])                    
    pygame.display.flip()
    pygame.mixer.music.load('bomberman.mid')
    pygame.mixer.music.play()

    while True:        
        clock.tick(50)
        x,y = mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif(event.type == MOUSEBUTTONDOWN):
                for i in range(1,11):
                    if(within_boundaries((x,y),buttons[i],False)):
                        pygame.mixer.music.stop()
                        if(i not in played_levels):
                            level_intro_screen(i)
                            played_levels.append(i)
                        run_game(i)
                if(within_boundaries((x,y),buttons[0],False)):
                    exit_game()
        
    

def level_intro_screen(level):
    background = pygame.image.load('level_intro_bg.png')
    continue_button = Button(screen, 'Gen', (324,490))
    screen.blit(background,background.get_rect());
    skip = False
    dialogue = []
    dialogue.append("Now son, don't get cocky.\nMy expert opinion here is that "
    "we have two speeders.\nBut one guy says he was stopped at the sign all "
    "proper.\n\nNow I say one moving car hitting a stationary car is not\nenough"
    " for their wreckage to drift so far.\nUse your fancy science son, prove me wrong...")       
    dialogue.append("We have a head-on collision on a major road.\n"
                    "Either both drivers fell asleep on the wheel,\n"
                    "or they were playing a game of chicken.\n\n"
                    "This might prove tricky, there is damage but the \n"
                    "wreckage is very close to the crash site.\n\n"
                    "..............What's wrong with people.")
    dialogue.append("Lucky shot with the previous case...    \"Lucky.\"\n"
                    "We have another collision at a nearby intersection.\n"
                    "It's a residential neighbourhood, thankfully no casualties.\n\n"
                    "Figure out their exact speeds at the moment of the crash\n"
                    "Insurance purposes...  plus, I would be glad to add\n"
                    "speeding charges along with endangerment.\n")
    dialogue.append("This guy has the audacity to run down a biker, and claim\n"
                    "innocence.         \nSays the biker jumped out from a side-road\n"
                    "speeding.\nBiker's fine and pressing charges, a lovely little lady.\n"
                    "And she's getting a big settlement if she was going\nslower than 10km/h\n"
                    "..Can't believe she's actually unhurt; helms works wonders.")
    dialogue.append("We have an accident on the highway; near a merge.\n"
                    "Both parties claim they saw the road empty, and that\n"
                    "the other must have been speeding.\n"
                    "I see clearly what transpired here, but department wants \n"
                    "your \"approval\" now that you have a few cases \nunder your belt.\n\n"
                    "You're starting to make a name for yourself...")
    dialogue.append("Some local kids snatched their fathers' carkeys, \n"
                    "and ended up in a parking lot.\n"
                    "From the tire-marks, looks like they tried their hand \n"
                    "in drag racing.\n"
                    "Nothing like a few movies to get youngsters worked up.\n\n"
                    "Figure this mess out for me, time to set examples.")
    dialogue.append("One drives out of a street, only to get clipped by\n"
                    "another on the main road. Never been in this area\n"
                    "before and I can see why it's treacherous...\n\n"
                    "It's a pretty blind spot, if you prove these drivers\n"
                    "did nothing wrong, we'll get some traffic lights\n"
                    "installed here.                                  \n"
                    "But not before... Penny-pinching city hall.")
    dialogue.append("Remember the head-on collision some weeks ago?\n"
                    "Well, lightning struck twice, and there are rumors\n"
                    "in the area about the road being haunted now.\n\n"
                    "My bet's still towards people not getting enough sleep.")
    dialogue.append("Here's a heartwarming one, two speeders, both admit\n"
                    "their fault. \n"
                    "Turns out they're old friends who lost contact  long ago.\n\n"
                    "So they literally \"bumped into\" each-other.\n"
                    "The cars drifted apart in an interesting way though,\n"
                    "and that's why you're here.")
    dialogue.append("Certain concerned parents contacted us, with info\n"
                    "on what possessed their kids to play bumper-cars\n"
                    "in that parking lot:    they're \"wanna-be\"s.\n"
                    "There's an underground drag-racing group in town.\n"
                    "We found crash and tire-marks; some youngsters are\n"
                    "in custody. Take the specs of their cars and figure\n"
                    "out if these two could be the ones racing on the scene.\n"
                    "Won't count as evidence, but maybe they'll admit it.")
    
    lines  = dialogue[level-1]
    pos = vec2d(250,170)
    
    write_monologue(lines, screen, 20, (255,255,255), (0,0,0), pos)
    continue_button.blitme()
    write_to_button("Continue", screen, 25, (0,0,0), (255,255,255), continue_button)     
    while True:
        clock.tick(50)
        x,y = mouse.get_pos()
        if(skip):
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif(event.type == MOUSEBUTTONDOWN):
                if(within_boundaries((x,y), continue_button, False)):
                    skip = True
        pygame.display.flip()           
    
    
def run_game(level):
    # Game parameters
    CAR_FILENAMES = [
        'darkSprite00.png','redSprite00.png','blueSprite00.png',
        'brownSprite00.png', 'greenSprite00.png']
    CRASH_FILENAMES = [
        'crashSprite01.png',
        'crashSprite02.png']
    crash_sound = pygame.mixer.Sound('crash_sound.wav')
    car_start_sound = pygame.mixer.Sound('car_start.wav')
    
    background = pygame.image.load("bg_level"+str(level)+".png")    
    
    buttons = []
    buttonPanel = Button(screen, 'MidPanel', (5, 400))
    buttons.append(buttonPanel)
    hour_glass = hourGlass(screen, 'hourGlassDown.png',
                               (buttonPanel.pos.x + 85, buttonPanel.pos.y + 20))
    buttons.append(hour_glass)
    reset = Button(screen, 'Reset',
                           (buttonPanel.pos.x + 15, buttonPanel.pos.y + 20))
    buttons.append(reset)
    ret = Button(screen, 'Return',
                            (buttonPanel.pos.x + 15, buttonPanel.pos.y + 85))
    buttons.append(ret)
    show_tutorial= Button(screen, 'Gen' , (0,0))
    show_tutorial.text = "Show Tutorial"
    buttons.append(show_tutorial)
    show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h)) 
    show_spots.text = "Show Instructions"
    buttons.append(show_spots)
    arrow = Button(screen, 'Arrow', (50,50))
        
    pause = True;  #level starts paused
    if level == 1:
        counter = Counter()         
        counter.carpos.append((435,340))
        counter.carpos.append((435,390))        
        # The main game loop
        #
        while True:            
            if(not counter.level_ready):
                cars = []
                inactive_cars = []
                car0 = Car(screen,'darkSprite00.png',counter.carpos[0], (0,-1), 600, 0, 0, (0,0))
                cars.append(car0)
                car1 = Car(screen,'redSprite00.png',counter.carpos[1], (0,-1), 1000, 0, 0, (0,1))
                cars.append(car1)  
                crash_pos = vec2d(0,0)
                
                target = Button(screen, 'Target', (410,100))
                crash = Button(screen, 'Crash', (405,310))
                cop_spot = Button(screen, 'ShowSpot', (420, 250))
                button_gen = Button(screen, 'Gen', (280, 390))                
                        
                i = 0
                carClicked = []
                carClicked.append(False)
                carClicked.append(False)
                counter.level_ready = True   
        
            # Limit frame speed to 50 FPS
            #
            time_passed = clock.tick(50)            
            screen.blit(background, background.get_rect())
            draw_buttons(screen, buttons)
            target.blitme()
            crash.blitme()
            if(hour_glass.pause):
                time_passed = 0;
            draw_spots(counter, cop_spot, button_gen, crash, target)
            x,y = mouse.get_pos()
            handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
            blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
            checkCrashes(cars, inactive_cars, hour_glass, crash_sound)  
            pygame.display.flip()
    
    
    elif level == 2:  
                counter = Counter()
                counter.carpos.append((325,275))
                counter.carpos.append((425,300))
                # The main game loop
                while True:            
                    if(not counter.level_ready):
                        cars = []
                        inactive_cars = []              
                        background = pygame.image.load("bg_level"+str(level)+".png")
                        car0 = Car(screen,'darkSprite00.png',counter.carpos[0],
                                        (1,0), 900, 0, 0,(-1,0))
                        cars.append(car0)                      
                        car1 = Car(screen,'greenSprite00.png',counter.carpos[1],
                                                            (-1,0), 1600, 0, 0,(1,0))
                        cars.append(car1)
                        show_tutorial= Button(screen, 'Gen' , (0,0))
                        show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))                    
                        target = Button(screen, 'Target', (300,260))
                        crash = Button(screen, 'Crash', (360,260))
                        cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                        button_gen = Button(screen, 'Gen', (400, 340)) #
                                            
                        i = 0
                        carClicked = []
                        carClicked.append(False)
                        carClicked.append(False)
                        counter.level_ready = True 
                    time_passed = clock.tick(50)            
                    screen.blit(background, background.get_rect())
                    draw_buttons(screen, buttons)
                    target.blitme()
                    crash.blitme()
                    if(hour_glass.pause):
                        time_passed = 0;
                    draw_spots(counter, cop_spot, button_gen, crash, target)
                    x,y = mouse.get_pos()
                    handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
                    checkCrashes(cars, inactive_cars, hour_glass, crash_sound)              
                    blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
                    pygame.display.flip()                              
    
    elif level == 3:  
        counter = Counter()
        counter.carpos.append((515,400))
        counter.carpos.append((625,350))        
        # The main game loop
        #
        while True:            
            if(not counter.level_ready):
                cars = []
                inactive_cars = []
                                          
                background = pygame.image.load("bg_level"+str(level)+".png")
                car0 = Car(screen,'brownSprite00.png',counter.carpos[0],
                                (0,-1), 1350, 0, 0,(0,1))
                cars.append(car0)
                car1 = Car(screen,'redSprite00.png', counter.carpos[1],
                                (-1,0), 1700, 0, 0,(1,0))
                cars.append(car1)  
                
                original_pos = car1.pos
                crash_pos = vec2d(0,0)
                show_tutorial= Button(screen, 'Gen' , (0,0))
                show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))                     
                target = Button(screen, 'Target', (300,250))
                crash = Button(screen, 'Crash', (car0.pos.x - 30,car1.pos.y - 30))
                cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                button_gen = Button(screen, 'Gen', (280, 390)) # Click&Drag msg
                i = 0
                carClicked = []
                carClicked.append(False)
                carClicked.append(False) 
                crashPlayed = False
                counter.level_ready = True    
            
            # Limit frame speed to 50 FPS
            #
            time_passed = clock.tick(50)            
            screen.blit(background, background.get_rect())
            draw_buttons(screen, buttons)
            target.blitme()
            crash.blitme()
            if(hour_glass.pause):
                time_passed = 0;
            draw_spots(counter, cop_spot, button_gen, crash, target)
            x,y = mouse.get_pos()
            handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
            checkCrashes(cars, inactive_cars, hour_glass, crash_sound)              
            blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
            pygame.display.flip()      
            
    elif level == 4:  
        counter = Counter()
        counter.carpos.append((445,420))
        counter.carpos.append((530,500))
        # The main game loop
        while True:            
            if(not counter.level_ready):
                cars = []
                inactive_cars = []              
                background = pygame.image.load("bg_level"+str(level)+".png")
                car0 = Car(screen,'darkSprite00.png',counter.carpos[0],
                                (1,0), 900, 0, 0,(-1,0))
                cars.append(car0)                      
                car1 = Car(screen,'bikerSprite00.png',counter.carpos[1],
                                                    (0,-1), 80, 0, 0,(0,1))
                cars.append(car1)
                show_tutorial= Button(screen, 'Gen' , (0,0))
                show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))                    
                target = Button(screen, 'Target', (550,340))
                crash = Button(screen, 'Crash', (car0.pos.x + 50,395))
                cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                button_gen = Button(screen, 'Gen', (280, 390)) #
                                    
                i = 0
                carClicked = []
                carClicked.append(False)
                carClicked.append(False)
                counter.level_ready = True    
            
            # Limit frame speed to 50 FPS
            #
            time_passed = clock.tick(50)
            screen.blit(background, background.get_rect())
            draw_buttons(screen, buttons)
            target.blitme()
            crash.blitme()
            if(hour_glass.pause):
                time_passed = 0;
            draw_spots(counter, cop_spot, button_gen, crash, target)
            x,y = mouse.get_pos()
            handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
            blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
            checkCrashes(cars, inactive_cars, hour_glass, crash_sound, True, cars[0].pos)  
            pygame.display.flip()    
            
    elif level == 5: 
        counter = Counter()
        counter.carpos.append((200,250))
        counter.carpos.append((225,400))
        # The main game loop
        while True:            
            if(not counter.level_ready):
                cars = []
                inactive_cars = []              
                background = pygame.image.load("bg_level"+str(level)+".png")
                car0 = Car(screen,'darkSprite00.png',counter.carpos[0],
                                (1,0), 900, 0, 0,(-1,0))
                cars.append(car0)                      
                car1 = Car(screen,'greenSprite00.png',counter.carpos[1],
                                                    (1,-1), 1600, 0, 0,(-1,1))
                cars.append(car1)
                show_tutorial= Button(screen, 'Gen' , (0,0))
                show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))                    
                target = Button(screen, 'Target', (600,80))
                crash = Button(screen, 'Crash', (325,225))
                cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                button_gen = Button(screen, 'Gen', (400, 300)) 
                i = 0
                carClicked = []
                carClicked.append(False)
                carClicked.append(False)
                counter.level_ready = True 
            time_passed = clock.tick(50)            
            screen.blit(background, background.get_rect())
            target.blitme()
            crash.blitme()
            if(hour_glass.pause):
                time_passed = 0;
            draw_spots(counter, cop_spot, button_gen, crash, target)
            x,y = mouse.get_pos()
            handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
            checkCrashes(cars, inactive_cars, hour_glass, crash_sound)              
            blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
            draw_buttons(screen, buttons)            
            pygame.display.flip()
            
    elif level == 6:  
            counter = Counter()
            counter.carpos.append((330,375))
            counter.carpos.append((250,350))
            # The main game loop
            while True:            
                if(not counter.level_ready):
                    cars = []
                    inactive_cars = []              
                    background = pygame.image.load("bg_level"+str(level)+".png")
                    car0 = Car(screen,'rustySprite00.png',counter.carpos[0],
                                    (0,-1), 1300, 0, 0,(0,1))
                    cars.append(car0)                      
                    car1 = Car(screen,'blueSprite00.png',counter.carpos[1],
                                                        (1,-1), 1400, 0, 0,(-1,1))
                    cars.append(car1)
                    show_tutorial= Button(screen, 'Gen' , (0,0))
                    show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))  
                    target2 = Button(screen, 'Target', (475,120))                    
                    target = Button(screen, 'Target', (325,120))
                    crash = Button(screen, 'Crash', (300,250))
                    cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                    button_gen = Button(screen, 'Gen', (280, 390)) #
                                        
                    i = 0
                    carClicked = []
                    carClicked.append(False)
                    carClicked.append(False)
                    counter.level_ready = True    
                
                # Limit frame speed to 50 FPS
                #
                time_passed = clock.tick(50)            
                screen.blit(background, background.get_rect())
                draw_buttons(screen, buttons)
                target.blitme()
                target2.blitme()
                crash.blitme()
                if(hour_glass.pause):
                    time_passed = 0;
                draw_spots(counter, cop_spot, button_gen, crash, target, target2)
                x,y = mouse.get_pos()
                handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
                blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
                checkCrashes(cars, inactive_cars, hour_glass, crash_sound, True, (target2.pos.x,target2.pos.y))  
                pygame.display.flip()
                
    elif level == 7:  
                counter = Counter()
                counter.carpos.append((610,300))
                counter.carpos.append((630,390))
                # The main game loop
                while True:            
                    if(not counter.level_ready):
                        cars = []
                        inactive_cars = []              
                        background = pygame.image.load("bg_level"+str(level)+".png")
                        car0 = Car(screen,'redSprite00.png',counter.carpos[0],
                                        (0,1), 1400, 0, 0,(0,-1))
                        cars.append(car0)                      
                        car1 = Car(screen,'blueSprite00.png',counter.carpos[1],
                                                            (-1,0), 3000, 0, 0,(1,0))
                        cars.append(car1)
                        show_tutorial= Button(screen, 'Gen' , (0,0))
                        show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))  
                        target = Button(screen, 'Target', (440,360))                    
                        target2 = Button(screen, 'Target', (500,460))
                        crash = Button(screen, 'Crash', (580,350))
                        cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                        button_gen = Button(screen, 'Gen', (280, 390)) #
                                            
                        i = 0
                        carClicked = []
                        carClicked.append(False)
                        carClicked.append(False)
                        counter.level_ready = True    
                    
                    # Limit frame speed to 50 FPS
                    #
                    time_passed = clock.tick(50)            
                    screen.blit(background, background.get_rect())
                    draw_buttons(screen, buttons)
                    target.blitme()
                    target2.blitme()
                    crash.blitme()
                    if(hour_glass.pause):
                        time_passed = 0;
                    draw_spots(counter, cop_spot, button_gen, crash, target, target2)
                    x,y = mouse.get_pos()
                    handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
                    blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
                    checkCrashes(cars, inactive_cars, hour_glass, crash_sound, True, (target2.pos.x,target2.pos.y))  
                    pygame.display.flip()
                    
    elif level == 8:  
        counter = Counter()
        counter.carpos.append((475,270))
        counter.carpos.append((300,290))
        # The main game loop
        while True:            
            if(not counter.level_ready):
                cars = []
                inactive_cars = []              
                background = pygame.image.load("bg_level"+str(level)+".png")
                car0 = Car(screen,'redSprite00.png',counter.carpos[0],
                                (-1,0), 1900, 0, 0,(1,0))
                cars.append(car0)                      
                car1 = Car(screen,'blueSprite00.png',counter.carpos[1],
                                                    (1,0), 1250, 0, 0,(-1,0))
                cars.append(car1)
                show_tutorial= Button(screen, 'Gen' , (0,0))
                show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))  
                target = Button(screen, 'Target', (500,320))                    
                target2 = Button(screen, 'Target', (250,180))
                crash = Button(screen, 'Crash', (375,250))
                cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                button_gen = Button(screen, 'Gen', (280, 390)) #
                                    
                i = 0
                carClicked = []
                carClicked.append(False)
                carClicked.append(False)
                counter.level_ready = True    
            
            # Limit frame speed to 50 FPS
            #
            time_passed = clock.tick(50)            
            screen.blit(background, background.get_rect())
            draw_buttons(screen, buttons)
            target.blitme()
            target2.blitme()
            crash.blitme()
            if(hour_glass.pause):
                time_passed = 0;
            draw_spots(counter, cop_spot, button_gen, crash, target, target2)
            x,y = mouse.get_pos()
            handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
            blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
            checkCrashes(cars, inactive_cars, hour_glass, crash_sound, True, (target2.pos.x,target2.pos.y))  
            pygame.display.flip()
            
    elif level == 9:  
        counter = Counter()
        counter.carpos.append((350,200))
        counter.carpos.append((500,350))
        # The main game loop
        while True:            
            if(not counter.level_ready):
                cars = []
                inactive_cars = []              
                background = pygame.image.load("bg_level"+str(level)+".png")
                car0 = Car(screen,'redSprite00.png',counter.carpos[0],
                                (1,1), 1900, 0, 0,(-1,-1))
                cars.append(car0)                      
                car1 = Car(screen,'blueSprite00.png',counter.carpos[1],
                                                    (-1,-1), 1250, 0, 0,(1,1))
                cars.append(car1)
                show_tutorial= Button(screen, 'Gen' , (0,0))
                show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))  
                target2 = Button(screen, 'Target', (550,260))                    
                target = Button(screen, 'Target', (250,280))
                crash = Button(screen, 'Crash', (400,250))
                cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                button_gen = Button(screen, 'Gen', (280, 390)) #
                                    
                i = 0
                carClicked = []
                carClicked.append(False)
                carClicked.append(False)
                counter.level_ready = True    
            
            # Limit frame speed to 50 FPS
            #
            time_passed = clock.tick(50)            
            screen.blit(background, background.get_rect())
            draw_buttons(screen, buttons)
            target.blitme()
            target2.blitme()
            crash.blitme()
            if(hour_glass.pause):
                time_passed = 0;
            draw_spots(counter, cop_spot, button_gen, crash, target, target2)
            x,y = mouse.get_pos()
            handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
            blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
            checkCrashes(cars, inactive_cars, hour_glass, crash_sound, True, (target2.pos.x,target2.pos.y))  
            pygame.display.flip()
            
    elif level == 10:  
                counter = Counter()
                counter.carpos.append((300,200))
                counter.carpos.append((460,200))
                # The main game loop
                while True:            
                    if(not counter.level_ready):
                        cars = []
                        inactive_cars = []              
                        background = pygame.image.load("bg_level"+str(level)+".png")
                        car0 = Car(screen,'rustySprite00.png',counter.carpos[0],
                                        (1,1), 1800, 0, 0,(-1,-1))
                        cars.append(car0)                      
                        car1 = Car(screen,'blueSprite00.png',counter.carpos[1],
                                                            (-1,1), 2000, 0, 0,(1,-1))
                        cars.append(car1)
                        show_tutorial= Button(screen, 'Gen' , (0,0))
                        show_spots = Button(screen, 'Gen', (0,show_tutorial.image_h))  
                        target = Button(screen, 'Target', (475,440))                    
                        target2 = Button(screen, 'Target', (325,440))
                        crash = Button(screen, 'Crash', (350,250))
                        cop_spot = Button(screen, 'ShowSpot', (crash.pos.x + 20, crash.pos.y - 70))
                        button_gen = Button(screen, 'Gen', (280, 390)) #
                                            
                        i = 0
                        carClicked = []
                        carClicked.append(False)
                        carClicked.append(False)
                        counter.level_ready = True    
                    
                    # Limit frame speed to 50 FPS
                    #
                    time_passed = clock.tick(50)            
                    screen.blit(background, background.get_rect())
                    draw_buttons(screen, buttons)
                    target.blitme()
                    target2.blitme()
                    crash.blitme()
                    if(hour_glass.pause):
                        time_passed = 0;
                    draw_spots(counter, cop_spot, button_gen, crash, target, target2)
                    x,y = mouse.get_pos()
                    handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound)
                    blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed,x,y,level)
                    checkCrashes(cars, inactive_cars, hour_glass, crash_sound, True, (target2.pos.x,target2.pos.y))  
                    pygame.display.flip()            
                  
def blit_cars(screen, counter, cars, inactive_cars, target, hour_glass, time_passed, x,y, level):
    if(counter.spots_shown):               
        for car in cars:
                car.update(time_passed)
                car.blitme()
                if(car.speed < 0.05 and car.friction > 0): #friction > 0 implies car is a wreck
                    if(within_boundaries(car.pos, target, False)):
                        win_report(screen, level, inactive_cars)
                        hour_glass.stop()
                        break
                    elif(car.speed == 0):
                        lose_report(screen)
                        hour_glass.stop()  
                if(within_boundaries((x,y), car, True)):
                    fits = True
                    new_x = car.pos.x+50
                    new_y = car.pos.y-50 
                    if(new_x + 114 > 800):
                        new_x = car.pos.x - 175
                        fits = False
                    if(new_y + 66 > 600):
                        new_y = car.pos.y - 100
                        fits = False                    
                    stats = Button(screen, 'Gen', (new_x, new_y))
                    
                    stats.blitme()
                    info = "Mass=" + str(car.mass) + " kg\n Velocity=" + str(round(car.speed * 50,2)) + " m/s"
                    write_to_button(info, screen, 15, (0,0,0), (255,255,255), stats)
                    if(car.axes_mutable != (0,0)):
                        if(car.direction == vec2d(1,0)):
                            car.image = pygame.image.load("silverSprite00.png").convert_alpha()
                        if(car.direction == vec2d(0,-1)):
                            car.image = pygame.image.load("silverSprite01.png").convert_alpha()
                        elif(car.direction == vec2d(-1,0)):
                            car.image = pygame.image.load("silverSprite10.png").convert_alpha()
                        elif(car.direction == vec2d(0,1)):
                            car.image = pygame.image.load("silverSprite11.png").convert_alpha()
                        if(car.direction.get_angle() == -45):#heading right and up
                            right = pygame.image.load("silverSprite" + '01.png').convert_alpha()
                            car.image = transform.rotate(right, 10)
                        elif(car.direction.get_angle() == -135):#heading left and up
                            left = pygame.image.load("silverSprite" + '01.png').convert_alpha()
                            car.image = transform.rotate(left, 10)        
                        elif(car.direction.get_angle() == 45):#heading right and down
                            right = pygame.image.load("silverSprite" + '11.png').convert_alpha()
                            car.image = transform.rotate(right, 10)     
                        elif(car.direction.get_angle() == 135):#heading left and down
                            left = pygame.image.load("silverSprite" + '10.png').convert_alpha()
                            car.image = transform.rotate(left, 10)                         
                        if(car.mass < 100):
                            car.image = pygame.image.load("bikerSpriteSelected01.png").convert_alpha()
                        car.blitme()                         
                        
                        
                        

def within_boundaries(c, obj, central_coordinates):
    if(not central_coordinates):
        result = (c[0] < obj.pos.x + obj.image_w and
            c[0] > obj.pos.x and c[1] < obj.pos.y + obj.image_h and
            c[1] > obj.pos.y)
    else:
        result = (c[0] < (obj.pos.x + obj.image_w / 2) and
            c[0] > (obj.pos.x - obj.image_w / 2) and
            c[1] < (obj.pos.y + obj.image_h / 2) and
            c[1] > (obj.pos.y - obj.image_h / 2))
    return result

def write_to_button(str, screen, size, color, bg, button, centered = True):
    if(str != ''):
        str = str.split("\n")
        font = pygame.font.SysFont("buxton sketch", size)
        pos_y = button.pos[1] + 15         
        if(centered):
            pos_y += ((button.image_h - font.size("C")[1] - 18 ) / 2) - 15           
        for s in str:
            pos_x = button.pos[0] + 15
            text_w = font.size(s)[0]
            if(centered):
                pos_x += ((button.image_w - text_w) / 2) - 15
            text = font.render(s, True, color)
            screen.blit(text,(pos_x, pos_y))
            pos_y += size + 5
            
def win_report(screen, level, inactive_cars):
    reports = []
    reports.append("\"What do you know, it was stopping.\"")
    reports.append("")
    win_button = Button(screen, 'InfoScreen', (300,250))
    win_button.blitme()    
    if(reports[level - 1] != ""):
        font = pygame.font.SysFont("buxton sketch", 15)        
        cop = image.load('cop.png').convert_alpha()
        surface = pygame.surface.Surface((250,50),pygame.SRCALPHA, 32)        
        surface.blit(cop, (0,0))
        surface.blit(font.render(reports[level-1], True, black),(40,15))
        screen.blit(surface, (win_button.pos.x + 20, win_button.pos.y + 120))        
    
    write_to_button("SUCCESS!..", screen, 20, black, white, win_button, False)
    screen.blit(inactive_cars[0].printable(), (win_button.pos.x + 20, win_button.pos.y + 40))
    screen.blit(inactive_cars[1].printable(), (win_button.pos.x + 20, win_button.pos.y + 80))
    if(level not in won_levels):
        won_levels.append(level)    
def lose_report(screen):
    lose_button = Button(screen, 'InfoScreen', (300,250))
    lose_button.blitme()
    write_to_button("NOPE!\nYou're off the final mark.\n"
                    "Hit Reset to try again.\n"
                    "Hit Return to quit.", screen, 25, black, white, lose_button, False)      
def write_monologue(str, screen, size, color, bg, pos):    
    font = pygame.font.SysFont("buxton sketch", 12)
    escape = font.render("Hit ESC to skip", True, color, bg)
    screen.blit(escape,(720,430)) 
    font = pygame.font.SysFont("buxton sketch", 25)
    sequence = list(str)
    pos_x = pos[0]
    skip_flag = False
    for c in sequence:
        for event in pygame.event.get():
            if(event.type == KEYDOWN): #skipping intro monologue
                k = event.key
                if(k == pygame.K_ESCAPE):
                    skip_flag = True
                    break
        if(not skip_flag):        
            pygame.time.delay(40)
        if(c == '\n'):
                    pos[0] = pos_x
                    pos[1] += 35
                    pygame.time.delay(300)
        else:
            text = font.render(c, True, color, bg)
            screen.blit(text,(pos[0],pos[1])) 
            pos[0] += font.size(c)[0] 
        pygame.display.flip()
        
            
def draw_arrow(screen, angle, upper, lower):
    original_length = arrow.image_h
    scale_factor = (lower[1] - upper[1]) / original_length[1]
    new_w = (int)(scale_factor * original_length[0])
    new_h = (int)(lower[1] - upper[1])
    if(not angle == 90):
        pygame.transform.rotate(arrow, angle - 90)    
        transform.smoothscale(arrow, (new_w, new_h))
        screen.blit(arrow, upper)

def adjust_for_crash(cars, crash_spot):
    if(cars[0].speed != 0 and cars[1].speed != 0):
        index = 3
        longest = 0
        shortest = 9999
        for i in range(0,len(cars)):
            distance = cars[i].pos - vec2d(crash_spot.pos.x + crash_spot.image_w / 2, 
                                           crash_spot.pos.y + crash_spot.image_h / 2)
            time = int(distance.get_length() / cars[i].speed)
            print(distance.get_length())
            if(time > longest):
                longest = time
                index = i            
            if(time < shortest): 
                shortest = time
        displacement = ((longest - shortest) * cars[index].speed) * cars[index].direction
        cars[index].pos += displacement

def draw_buttons(screen, buttons):
    for button in buttons:
        button.blitme()

def draw_spots(counter, cop_spot, button_gen, crash, target, target2 = ''):
    if(not counter.spots_shown):     #Show the crash and final positions
        if(counter.count <= 75):
            cop_spot.blitme()
            write_to_button("          The crash"
                            "\n          happened here", screen, 15, black, white, cop_spot, False)
        elif(counter.count  <= 150):
            cop_spot.pos = vec2d((target.pos.x + 20, target.pos.y - 70))
            cop_spot.blitme()
            write_to_button("          The wreck"
                            "\n          was found here", screen, 15, black, white, cop_spot, False)
        elif(target2 != '' and counter.count <= 225):
            cop_spot.pos = vec2d((target2.pos.x + 20, target2.pos.y - 70))
            cop_spot.blitme()
            write_to_button("        Another wreck"
                            "\n          was found here", screen, 15, black, white, cop_spot, False)            
        counter.count  += 1
        if(counter.count  > 225):
            counter.spots_shown = True
            counter.count  = 0
            cop_spot.pos = vec2d(crash.pos.x + 20, crash.pos.y - 70)
    elif(not counter.tutorial_shown):   #Show tutorial bubbles
        if(counter.count  <= 100):
            button_gen.text = "Click&Drag the car\nto set its velocity"
            button_gen.blitme()
        elif(counter.count  <= 200):
            button_gen.pos = vec2d((150, 450))
            button_gen.text = "And flick the\nswitch ON"
            button_gen.blitme()
        counter.count  += 1
        if(counter.count  > 200):
            counter.tutorial_shown = True
            counter.count  = 0
            button_gen.pos = vec2d(280, 390)
def LCM(x,y):
    temp = x
    while temp%y != 0:
        temp += x
    return temp

def ms_to_kmh(speed):
    return speed * 3.6

def exit_game():
    pygame.display.quit()
    pygame.mixer.music.stop()
    sys.exit()
    
def checkCrashes(cars, inactive_cars, hour_glass, crash_sound, elastic = False, secondary = (0,0)):
    crash = False
    crashPlayed = False
    if(len(cars) > 1): 
        if(cars[0].pos.x - cars[0].image_w/4 < cars[1].pos.x + cars[1].image_w/4 
                   and cars[0].pos.x + cars[0].image_w/4 > cars[1].pos.x - cars[1].image_w/4 ):
                if(cars[0].pos.y - cars[0].image_h/4 < cars[1].pos.y + cars[1].image_h/4 
                       and cars[0].pos.y + cars[0].image_w/4 > cars[1].pos.y - cars[1].image_w/4 ):
                    crash = True
        if(crash and not hour_glass.pause): 
            car0 = cars[0].clone()
            car0.direction = vec2d(0,1) #turn down for win-caption
            car0.update(0) #update for img update
            car1 = cars[1].clone()
            car1.direction = vec2d(0,1)#turn down for win-caption
            car1.update(0)#update for img update
            inactive_cars.append(car0)
            inactive_cars.append(car1)            
            if(not elastic):
                wreck = cars[0].crash(cars[1])
                inactive_cars.append(wreck)
                cars.pop()
                cars.pop()
                cars.append(wreck)
            else: #elastic "bump"
                if(cars[0].speed > 0.02 and cars[1].speed > 0.02):
                    cars[0].bump(cars[1], secondary)
                elif(cars[1]. mass < 100):
                    cars[0].bump(cars[1], secondary)
                else:
                    crashPlayed = True
            if(not crashPlayed):
                crashPlayed = True
                crash_sound.play()
    
    
def handle_events(x, y, counter, buttons, cars, crash, carClicked, car_start_sound):
    
    clickPosx = x
    clickPosy = y     
    for event in pygame.event.get():
        if(counter.spots_shown):
            if event.type == pygame.QUIT:
                exit_game()
            elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), buttons[1], False)): #hour_glass
                buttons[1].update()
                buttons[1].blitme()
                if(cars[0].speed != 0 and cars[1].speed != 0):
                    adjust_for_crash(cars, crash)
            elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), buttons[2], False)): #reset
                counter.level_ready = False
                if(not buttons[1].pause):
                    buttons[1].update()
                break;
            elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), buttons[3], False)): #return
                #pygame.display.quit() shut down the working instance
                intro_screen()
            elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), buttons[4], False)): #show_tutorial
                buttons[1].stop()
                counter.tutorial_shown = False
            elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), buttons[5], False)): #show_spots
                buttons[1].stop()
                counter.spots_shown = False                                                    
            elif(event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP):
                if(event.type == MOUSEBUTTONDOWN):
                    for i in range(0,len(cars)):
                        if(within_boundaries((x,y), cars[i], True)):
                            carClicked[i] = True                          
                else:    #event.type == MOUSEBUTTONUP
                    for i in range(0,2):
                        if(carClicked[i]):
                            carClicked[i] = False
                            releasePosx = x
                            releasePosy = y 
                            if(cars[i].speed > 0):
                                car_start_sound.play()
            elif((carClicked[0] or carClicked[1]) and buttons[1].pause):
                for i in range(0,len(cars)):    
                    pos_x = cars[i].pos.x
                    pos_y = cars[i].pos.y                    
                    if(carClicked[i]):
                        if((x > counter.carpos[i][0] and cars[i].axes_mutable[0] == 1) or (x < counter.carpos[i][0] and cars[i].axes_mutable[0] == -1)):
                            pos_x = x
                        if((y > counter.carpos[i][1] and cars[i].axes_mutable[1] == 1) or (y < counter.carpos[i][1] and cars[i].axes_mutable[1] == -1)):
                            pos_y = y
                        if(cars[i].axes_mutable[0] != 0 and cars[i].axes_mutable[1] != 0):
                            dif = vec2d(pos_x,pos_y) - cars[i].pos
                            if(cars[i].axes_mutable == (1,-1)):
                                cars[i].pos += dif.projection(vec2d(1,-1))
                            elif(cars[i].axes_mutable == (-1,-1)):
                                cars[i].pos += dif.projection(vec2d(-1,-1))
                            elif(cars[i].axes_mutable == (-1,1)):
                                cars[i].pos += dif.projection(vec2d(-1,1))
                            elif(cars[i].axes_mutable == (1,1)):
                                cars[i].pos += dif.projection(vec2d(1,1))                          
                        else:
                            cars[i].pos = vec2d(pos_x,pos_y)
                                                  
                        new_direction = vec2d(cars[i].pos.x - counter.carpos[i][0], cars[i].pos.y - counter.carpos[i][1]).normalized()
                        new_speed = int(vec2d(cars[i].pos.x  - counter.carpos[i][0], cars[i].pos.y - counter.carpos[i][1]).get_length() / 4) / 100
                        print(new_speed)
                        cars[i].speed = new_speed 

logo_screen()

