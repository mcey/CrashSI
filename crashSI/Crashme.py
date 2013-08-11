import os, sys
import math
from random import randint, choice

import pygame 
from pygame.sprite import Sprite
from pygame import *
from pygame.locals import *
from vec2d import vec2d


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

    def blitme(self, str=''):
        self.screen.blit(self.image, self.pos)
        
        
class Car(Sprite):
    """ A car sprite."""
    def __init__(   
            self, screen, img_filename, init_position, 
            init_direction, mass, speed, friction):
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
        self.imgFileName = img_filename
        # base_image holds the original image
        self.base_image = pygame.image.load(img_filename).convert_alpha()
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
        wreck_direction = vec2d(self.direction.x + other.direction.x,
                                self.direction.y + other.direction.y)
        wreck_mass = self.mass + other.mass
        wreck_speed = ((self.speed * self.mass) +
                       (other.speed * other.mass)) / wreck_mass
        wreck = Car(self.screen, 'crashSprite01.png', (wreck_x, wreck_y),
                    wreck_direction, wreck_mass, wreck_speed, 0.000006)
        return wreck


               
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
        if(self.direction.angle == 0):#heading right
            self.image = pygame.image.load(self.imgFileName[:-6] + '00.png').convert_alpha() 
        elif(self.direction.angle == -90):#heading up
            self.image = pygame.image.load(self.imgFileName[:-6] + '01.png').convert_alpha() 
        elif(self.direction.angle == 180):#heading left
            self.image = pygame.image.load(self.imgFileName[:-6] + '10.png').convert_alpha()
        else:#heading down
            self.image = pygame.image.load(self.imgFileName[:-6] + '11.png').convert_alpha()
     
        # Compute and apply the displacement to the position 
        # vector. The displacement is a vector, having the angle
        # of self.direction (which is normalized to not affect
        # the magnitude of the displacement)
        #
        if(self.friction > 0 and self.speed > 0.0):
            deceleration = self.mass * self.friction * 0.01
            self.speed = self.speed - (deceleration * time_passed)
            #if(self.speed > 0.5):     # spinning animation for the wreckage
                #self.direction.angle += 90
            print(deceleration, time_passed, deceleration*time_passed, self.speed)
        if(self.speed < 0):
            self.speed = 0
        displacement = vec2d(    
            self.direction.x * self.speed * time_passed,
            self.direction.y * self.speed * time_passed)       
        self.pos += displacement
        
        
        # When the image is rotated, its size is changed.
        # We must take the size into account for detecting 
        # collisions with the walls.
        #
        self.image_w, self.image_h = self.image.get_size()
        bounds_rect = self.screen.get_rect().inflate(
                        -self.image_w, -self.image_h)
        
        if self.pos.x < bounds_rect.left:
            self.pos.x = bounds_rect.left
            self.direction.x *= -1
        elif self.pos.x > bounds_rect.right:
            self.pos.x = bounds_rect.right
            self.direction.x *= -1
        elif self.pos.y < bounds_rect.top:
            self.pos.y = bounds_rect.top
            self.direction.y *= -1
        elif self.pos.y > bounds_rect.bottom:
            self.pos.y = bounds_rect.bottom
            self.direction.y *= -1
    
    def printable(self):#prints a surface with the car's picture and stats    
        font = pygame.font.SysFont("buxton sketch", 14)
        image_s = transform.smoothscale(self.image,(int(self.image_w/2), int(self.image_h/2)))
        surface = pygame.surface.Surface((250,50),pygame.SRCALPHA, 32)        
        surface.blit(image_s, (0,0))
        text = "was"
        if(self.speed == 0):
            text += " at a stop;"
        else:
            text += " going " + str(self.speed) + "m/s;"
        text += " had a mass of " +str(self.mass)
        alt_text = "had a momentum of " + str(self.speed * self.mass) + " kg.m/s"
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
           
    #------------------ PRIVATE PARTS ------------------#
    
    _counter = 0

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.init()
font = pygame.font.Font(None,8)
clock = pygame.time.Clock()
played_levels = []
won_levels = []

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)


def intro_screen():
    #Level selection etc
    background = pygame.image.load('intro_bg.png')
    screen.blit(background,background.get_rect());
    buttons = []
    buttons.append(Button(screen, 'Gen', (600,500)))
    buttons.append(Button(screen, 'Gen', (100,100)))
    buttons.append(Button(screen, 'Gen', (100,200)))
    button_score_bar = Button(screen, 'ScoreBar', (100,525))   
    write_to_button(("EXIT"), screen, 35, black, white,buttons[0])
    score_button = Button(screen, 'InfoScreen', (100,300))
    write_to_button(("Current Rank: Rookie\nLevels Completed: " + str(len(won_levels))), screen, 20, black, white,score_button)
    for i in range (1,len(buttons)):
                if(i in won_levels):
                    write_to_button((str(i) +  " - completed!"), screen, 15, black, white,buttons[i])
                else:
                    write_to_button(("Level " + str(i)), screen, 30, black, white,buttons[i])                    
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
                if(within_boundaries((x,y),buttons[1],False)):
                    pygame.mixer.music.stop()
                    if(1 not in played_levels):
                        level_intro_screen(1)
                        played_levels.append(1)
                    run_game(1)
                elif(within_boundaries((x,y),buttons[2],False)):
                    pygame.mixer.music.stop()
                    run_game(2)
                elif(within_boundaries((x,y),buttons[0],False)):
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
        'darkSprite00.png', 
        'redSprite00.png']
    CRASH_FILENAMES = [
        'crashSprite01.png',
        'crashSprite02.png']
    crash_sound = pygame.mixer.Sound('crash_sound.wav')
    car_start_sound = pygame.mixer.Sound('car_start.wav')

    
    buttonPanel = Button(screen, 'MidPanel', (5, 400))
    hour_glass = hourGlass(screen, 'hourGlassDown.png',
                               (buttonPanel.pos.x + 85, buttonPanel.pos.y + 20))
    reset = Button(screen, 'Reset',
                           (buttonPanel.pos.x + 15, buttonPanel.pos.y + 20))
    ret = Button(screen, 'Return',
                            (buttonPanel.pos.x + 15, buttonPanel.pos.y + 85))
    arrow = Button(screen, 'Arrow', (50,50))
        
    pause = True;  #level starts paused
    if level == 1:
        level_ready = False
        # The main game loop
        #
        while True:
            if(not level_ready):
                cars = []
                inactive_cars = []  
                suspend_for_input = False
                spots_shown = False
                tutorial_shown = False
                counter = 0                 
                background = pygame.image.load('bg_level02.png')
                car0 = Car(screen,'darkSprite00.png',
                                (435,340),
                                (1,0), 500, 0, 0)
                cars.append(car0)
                car1 = Car(screen,'redSprite00.png',
                                (435,390),
                                (1,0), 500, 0, 0)
                cars.append(car1)  
                car0.direction.rotate(-90)
                car1.direction.rotate(-90)
                
                original_pos = car1.pos
                crash_pos = vec2d(0,0)
        
                target = Button(screen, 'Target', (410,100))
                cop_spot = Button(screen, 'ShowSpot', (420, 250))
                button_gen = Button(screen, 'Gen', (280, 390))
                
                
                i = 0
                carClicked = False
                crashPlayed = False
                level_ready = True    
            
            # Limit frame speed to 50 FPS
            #
            time_passed = clock.tick(50)            
            screen.blit(background, background.get_rect())
            buttonPanel.blitme()                
            hour_glass.blitme()
            reset.blitme()
            ret.blitme()
            target.blitme()
            if(hour_glass.pause):
                time_passed = 0;
            if(not spots_shown):     #Show the crash and final positions
                if(counter <= 75):
                    cop_spot.blitme()
                    write_to_button("          The crash"
                                    "\n          happened here", screen, 15, black, white, cop_spot, False)
                elif(counter <= 150):
                    cop_spot.pos = vec2d((420,30))
                    cop_spot.blitme()
                    write_to_button("          And the wreck"
                                    "\n          was found here", screen, 15, black, white, cop_spot, False)
                counter += 1
                if(counter > 150):
                    spots_shown = True
                    counter = 0
            elif(not tutorial_shown):   #Show tutorial bubbles
                if(counter <= 75):
                    button_gen.blitme()
                    write_to_button("Click&Drag the car\nto set its velocity",screen, 14, black,white,button_gen)
                elif(counter <= 150):
                    button_gen.pos = vec2d((150, 450))
                    button_gen.blitme()
                    write_to_button("And flick the\nswitch ON", screen, 16, black,white,button_gen)
                counter += 1
                if(counter > 150):
                    tutorial_shown = True
            else:
                x,y = mouse.get_pos()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game()
                    elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), hour_glass, False)):
                        hour_glass.update()
                        hour_glass.blitme()
                    elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), reset, False)):
                        level_ready = False
                        if(not hour_glass.pause):
                            hour_glass.update()
                        break;
                    elif(event.type == MOUSEBUTTONDOWN and within_boundaries((x,y), ret, False)):
                        #pygame.display.quit() shut down the working instance
                        intro_screen()
                    elif(event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP):
                        if(event.type == MOUSEBUTTONDOWN):
                            if(within_boundaries((x,y), car1, True)):
                                carClicked = True
                                clickPosx = x
                                clickPosy = y                           
                        else:    #event.type == MOUSEBUTTONUP
                            if(carClicked):
                                carClicked = False
                                releasePosx = x
                                releasePosy = y                            
                                new_direction = vec2d(releasePosx - clickPosx, releasePosy - clickPosy).normalized()
                                new_speed = int(vec2d(releasePosx - original_pos.x, releasePosy - original_pos.y).get_length() / 50) / 10 + 0.02
                                print(new_speed)
                                car1.speed = new_speed
                                car_start_sound.play()
                    elif(carClicked and hour_glass.pause):
                        car1.pos = vec2d(car1.pos.x,y) #x axis immutable
               
                for car in cars:
                    car.update(time_passed)
                    if(spots_shown):
                        car.blitme()
                    if(car.speed < 0.05 and car.friction > 0): #friction > 0 implies car is a wreck
                        if(within_boundaries(car.pos, target, False)):
                            win_report(screen, level, inactive_cars)
                            break
                        elif(car.speed == 0):
                            lose_button = Button(screen, 'InfoScreen', (300,250))
                            lose_button.blitme()
                            write_to_button("NOPE!\nYou're off the final mark.\nHit Reset to try again.\nHit Return to quit.", screen, 25, black, white, lose_button, False)  
                    if(within_boundaries((x,y), car, True)):
                        stats = Button(screen, 'Gen', (car.pos.x+50, car.pos.y-50))
                        stats.blitme()
                        info = "Mass=" + str(car.mass) + "\n Velocity=" + str(round(car.speed,2))
                        write_to_button(info, screen, 15, (0,0,0), (255,255,255), stats)
                    
            if(len(cars) > 1 and checkCrashes(cars[0], cars[1]) and not hour_glass.pause):
                wreck = cars[0].crash(cars[1])
                inactive_cars.append(cars[0])
                inactive_cars.append(cars[1])
                crash_pos = wreck.pos
                if(not crashPlayed):
                    crashPlayed = True
                    crash_sound.play()
                cars = []
                cars.append(wreck)
            pygame.display.flip()
    
    
    elif level == 2:  #NOT YET IMPLEMENTED
        car0 = Car(screen,'darkSprite00.png',
                        (SCREEN_WIDTH/2,SCREEN_HEIGHT/2),
                        (1,0), 500, 0.2, 0)
        cars.append(car0)
        car1 = Car(screen,'redSprite00.png',
                        (SCREEN_WIDTH/2+150,SCREEN_HEIGHT/2),
                        (0,1), 500, 0.2, 0)
        cars.append(car1)

        pause = True;  #level starts paused
        i = 0
        carClicked = False
        clickedCar = -1
        # The main game loop
        #
        while True:
            # Limit frame speed to 50 FPS
            #
            time_passed = clock.tick(50)
            background = pygame.image.load('bg.png')
            screen.blit(background, background.get_rect())
            hour_glass.blitme()        
            if(hour_glass.pause):
                time_passed = 0;
            x,y = mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif(event.type == MOUSEBUTTONDOWN and x < 124 and x > 50 and y < 124 and y > 50):
                    hour_glass.update()
                    hour_glass.blitme()
                elif(event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP):
                
                    for i in range(len(cars)):
                        if(event.type == MOUSEBUTTONDOWN):
                            if(x < (cars[i].pos.x + cars[i].image_w / 2) and
                                   x > (cars[i].pos.x - cars[i].image_w / 2) and
                                   y < (cars[i].pos.y + cars[i].image_h / 2) and
                                   y > (cars[i].pos.y - cars[i].image_h / 2)):
                               carClicked = True
                               clickedCar = i
                               clickPosx = x
                               clickPosy = y
                        else:    
                            if(carClicked):
                                carClicked = False
                                releasePosx = x
                                releasePosy = y
                                new_direction = vec2d(releasePosx - clickPosx, releasePosy - clickPosy).normalized()
                                new_speed = vec2d(releasePosx - clickPosx, releasePosy - clickPosy).get_length() / 1000
                                cars[clickedCar].speed = new_speed
                                car_start_sound.play()
                            #print(releasePosx,clickPosx,releasePosy, clickPosy,new_speed) horrible testing line
                elif(carClicked and hour_glass.pause):
                    cars[clickedCar].pos = vec2d(x,cars[i].pos.y)  
            for car in cars:
                car.update(time_passed)
                car.blitme()
            if(checkCrashes(cars[0], cars[1])and not hour_glass.pause):
                wreck = cars[0].crash(cars[1])
                cars = []
                cars.append(wreck)
                cars.append(wreck)
            pygame.display.flip()

    

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
    win_button = Button(screen, 'InfoScreen', (300,250))
    win_button.blitme()
    write_to_button("SUCCESS!..", screen, 20, black, white, win_button, False)
    screen.blit(inactive_cars[0].printable(), (win_button.pos.x + 20, win_button.pos.y + 40))
    screen.blit(inactive_cars[1].printable(), (win_button.pos.x + 20, win_button.pos.y + 80))
    if(level not in won_levels):
        won_levels.append(level)    

def write_monologue(str, screen, size, color, bg, pos):    
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
       
def exit_game():
    pygame.display.quit()
    pygame.mixer.music.stop()
    sys.exit()
    
def checkCrashes(car0, car1):
    if(car0.pos.x - car0.image_w/4 < car1.pos.x + car1.image_w/4 
           and car0.pos.x + car0.image_w/4 > car1.pos.x - car1.image_w/4 ):
        if(car0.pos.y - car0.image_h/4 < car1.pos.y + car1.image_h/4 
               and car0.pos.y + car0.image_w/4 > car1.pos.y - car1.image_w/4 ):
            return True

intro_screen()

