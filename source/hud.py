# Author: Darron Vanaria
# Filesize: 24409 bytes
# LOC: 538

import pygame
import sys
import math

import objects
import define
import game_engine
import flatland_engine

WRAP_OFFSET_X = 80
WRAP_OFFSET_Y = 60

WRAP_X = 320 # 40 * 8 squares
WRAP_Y = 240 # 30 * 8 squares

class ScannerBlip(pygame.sprite.Sprite):   # a blip on the scanner screen

    def __init__(self, obj, x, y, blip_size):

        super().__init__() 
      
        # all sprites must have an 'image' attribute and a 'rect' attribute
        if isinstance(obj, objects.PlayerShip):
            self.image = pygame.image.load('images/player_blip.png').convert()
            self.image.set_colorkey(define.BLACK)
        else:
            self.image = pygame.Surface((blip_size,blip_size))
            self.image.fill(obj.color)

        self.rect = self.image.get_rect()
        self.rect.centerx = obj.scanner_x + WRAP_OFFSET_X + x
        self.rect.centery = obj.scanner_y + WRAP_OFFSET_Y + y

        self.offset_x = x
        self.offset_y = y

        # call parent constructor pygame.sprite.Sprite.__init__(self)

        self.parent_object = obj

    def update(self):

        if self.parent_object.alive() == False:
            self.kill()
        else:
            self.rect.centerx = self.parent_object.scanner_x + \
                    WRAP_OFFSET_X + self.offset_x
            self.rect.centery = self.parent_object.scanner_y + \
                    WRAP_OFFSET_Y + self.offset_y



class Scanner():

    def __init__(self):

        self.full_image = pygame.image.load('images/scanner.png').convert()
        self.background_image = self.full_image.copy()

        self.blip_group = pygame.sprite.Group()

    def add_blip(self, obj, blip_size):

        # top row
        self.blip_group.add( ScannerBlip(obj, -320, -240, blip_size) )
        self.blip_group.add( ScannerBlip(obj, 0, -240, blip_size) )
        self.blip_group.add( ScannerBlip(obj, 320, -240, blip_size) )

        # middle row
        self.blip_group.add( ScannerBlip(obj, -320, 0, blip_size) )
        self.blip_group.add( ScannerBlip(obj, 0, 0, blip_size) )
        self.blip_group.add( ScannerBlip(obj, 320, 0, blip_size) )
        
        # top row
        self.blip_group.add( ScannerBlip(obj, -320, 240, blip_size) )
        self.blip_group.add( ScannerBlip(obj, 0, 240, blip_size) )
        self.blip_group.add( ScannerBlip(obj, 320, 240, blip_size) )

    def update(self):

        self.blip_group.clear(self.full_image, self.background_image) 
        self.blip_group.update()
        self.blip_group.draw(self.full_image)



class CompassBlip(pygame.sprite.Sprite):   

    def __init__(self, obj):
       
        # all sprites must have an 'image' attribute and a 'rect' attribute
        self.image = pygame.Surface((4,4))
        self.image.fill(define.YELLOW)

        self.rect = self.image.get_rect()
        self.rect.centerx = int(obj.global_x / define.COMPASS_SCALE_W)
        self.rect.centery = int(obj.global_y / define.COMPASS_SCALE_H)

        # call parent constructor
        pygame.sprite.Sprite.__init__(self)

        self.parent_object = obj

    def update(self):

        if self.parent_object.alive() == False:
            self.kill()
        else:
            self.rect.centerx = \
                    int(self.parent_object.global_x / define.COMPASS_SCALE_W)
            self.rect.centery = \
                    int(self.parent_object.global_y / define.COMPASS_SCALE_H)

class Compass():

    def __init__(self, player):

        self.full_image = pygame.Surface((64,48))
        self.full_image.fill(define.BLACK)

        star_x = player.planet_data.star_x
        star_y = player.planet_data.star_y
        star_image = pygame.Surface((6,6))
        star_image.fill(define.WHITE)
        self.add_item(star_x, star_y, star_image)

        planet_x = player.planet_data.planet_x
        planet_y = player.planet_data.planet_y
        planet_image = pygame.Surface((8,8))
        planet_image.fill(define.BLUE)
        self.add_item(planet_x, planet_y, planet_image)

        station_x = player.planet_data.station_x
        station_y = player.planet_data.station_y
        station_image = pygame.Surface((3,3))
        station_image.fill(define.CYAN)
        self.add_item(station_x, station_y, station_image)

        self.background_image = self.full_image.copy()

        self.blip_group = pygame.sprite.Group()
        self.blip_group.add( CompassBlip(player) )
        
    def add_item(self, global_x, global_y, image):

        scaled_x = int(global_x / define.COMPASS_SCALE_W)
        scaled_y = int(global_y / define.COMPASS_SCALE_H)
    
        self.full_image.blit(image, (scaled_x, scaled_y))
    
    def update(self):

        self.blip_group.clear(self.full_image, self.background_image) 
        self.blip_group.update()
        self.blip_group.draw(self.full_image)


# Panel Indicators ###########################################################

class Block(pygame.sprite.Sprite):   # a block on any instrument panel 

    def __init__(self, x, y, color):
       
        # all sprites must have an 'image' attribute and a 'rect' attribute
        self.image = pygame.Surface((8,8))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.top  = y 
        self.rect.left = x

        # call parent constructor
        pygame.sprite.Sprite.__init__(self)

class MissileBlock(pygame.sprite.Sprite):   

    def __init__(self, x, y, color):
       
        # all sprites must have an 'image' attribute and a 'rect' attribute
        self.image = pygame.Surface((14,8))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.top  = y 
        self.rect.left = x

        # call parent constructor
        pygame.sprite.Sprite.__init__(self)


class PanelType1():

    # Type 1 is all-white blocks across one panel

    def __init__(self, min_value, max_value, loc_x, loc_y, color):

        self.MIN_VALUE = min_value
        self.MAX_VALUE = max_value

        self.X_START = loc_x 
        self.Y_START = loc_y 

        self.sprite_list = []
        for i in range(9):
            temp = Block((loc_x + (9*i)), loc_y, color)
            self.sprite_list.append(temp)

        self.sprite_group = pygame.sprite.Group()

        self.scale = (self.MAX_VALUE - self.MIN_VALUE) / 10.0

        self.meter = 0   # how many blocks are showing?

        self.warning_on = False


    def update(self, data, surface, background):

        data = data - self.MIN_VALUE

        temp = int(data / self.scale)   # 0-9

        if temp < 0:
            temp = 0
        elif temp > 9:
            temp = 9

        if self.meter != temp:

            self.sprite_group.clear(surface, background) 
            self.sprite_group.empty()
            for i in range(temp):
                self.sprite_group.add( self.sprite_list[i] )
            self.sprite_group.draw(surface)
            self.meter = temp

    def forced_update(self, data, surface, background):

        data = data - self.MIN_VALUE

        temp = int(data / self.scale)   # 0-9

        if temp < 0:
            temp = 0
        elif temp > 9:
            temp = 9

        self.sprite_group.clear(surface, background) 
        self.sprite_group.empty()
        for i in range(temp):
            self.sprite_group.add( self.sprite_list[i] )
        self.sprite_group.draw(surface)
        self.meter = temp

class PanelType2():

    # Type 2 is "striped" blocks across 4 panels (ex: energy banks) 

    def __init__(self, min_value, max_value, loc_x, loc_y):

        self.MIN_VALUE = min_value
        self.MAX_VALUE = max_value

        self.X_START = loc_x 
        self.Y_START = loc_y 

        self.block_max = 9 * 4

        self.sprite_list = []
        for j in range(4):
            for i in range(9):
                if i%2 == 0:
                    temp = Block((loc_x + (72-(9*(8-i)))), (loc_y+ (16*(3-j))),\
                            define.RED) 
                    self.sprite_list.append(temp)
                else:
                    temp = Block((loc_x + (72-(9*(8-i)))), (loc_y+ (16*(3-j))),\
                            define.PINK) 
                    self.sprite_list.append(temp)

        self.sprite_group = pygame.sprite.Group()

        self.scale = (self.MAX_VALUE - self.MIN_VALUE) / self.block_max 

        self.meter = 0   # how many blocks are showing?

        self.warning_on = False


    def update(self, data, surface, background):

        temp = int(data / self.scale)   

        if self.meter != temp:

            self.sprite_group.clear(surface, background) 
            self.sprite_group.empty()
            for i in range(temp):
                self.sprite_group.add( self.sprite_list[i] )
            self.sprite_group.draw(surface)
            self.meter = temp

    def forced_update(self, data, surface, background):

        temp = int(data / self.scale)   

        self.sprite_group.clear(surface, background) 
        self.sprite_group.empty()
        for i in range(temp):
            self.sprite_group.add( self.sprite_list[i] )
        self.sprite_group.draw(surface)
        self.meter = temp

class PanelType3():

    # Type 3 is all-white blocks across one panel, unless its over a certain
    # threshold, then all blocks turn red.

    def __init__(self, min_value, max_value, loc_x, loc_y, threshold):

        self.MIN_VALUE = min_value
        self.MAX_VALUE = max_value

        self.X_START = loc_x 
        self.Y_START = loc_y 

        self.white_list = []
        for i in range(9):
            temp = Block((loc_x + (9*i)), loc_y, define.WHITE)
            self.white_list.append(temp)

        self.red_list = []
        for i in range(9):
            temp = Block((loc_x + (9*i)), loc_y, define.RED)
            self.red_list.append(temp)

        self.sprite_group = pygame.sprite.Group()

        self.scale = (self.MAX_VALUE - self.MIN_VALUE) / 10.0

        self.meter = 0   # how many blocks are showing?

        self.warning_on = False

        self.threshold = threshold


    def update(self, data, surface, background):

        data = data - self.MIN_VALUE

        temp = int(data / self.scale)   # 0-9

        if temp < 0:
            temp = 0
        elif temp > 9:
            temp = 9

        if self.meter != temp:

            self.sprite_group.clear(surface, background) 
            self.sprite_group.empty()
            if data < self.threshold:
                for i in range(temp):
                    self.sprite_group.add( self.white_list[i] )
            else:
                for i in range(temp):
                    self.sprite_group.add( self.red_list[i] )
            self.sprite_group.draw(surface)
            self.meter = temp

    def forced_update(self, data, surface, background):

        data = data - self.MIN_VALUE

        temp = int(data / self.scale)   # 0-9

        if temp < 0:
            temp = 0
        elif temp > 9:
            temp = 9

        self.sprite_group.clear(surface, background) 
        self.sprite_group.empty()
        if data < self.threshold:
            for i in range(temp):
                self.sprite_group.add( self.white_list[i] )
        else:
            for i in range(temp):
                self.sprite_group.add( self.red_list[i] )
        self.sprite_group.draw(surface)
        self.meter = temp

class PanelType4():

    # Type 4 is "striped" blocks across 1 panel

    def __init__(self, min_value, max_value, loc_x, loc_y):

        self.MIN_VALUE = min_value
        self.MAX_VALUE = max_value

        self.X_START = loc_x 
        self.Y_START = loc_y 

        self.block_max = 9 

        self.sprite_list = []
        for i in range(9):
            if i%2 == 0:
                temp = Block((loc_x + (72-(9*(8-i)))), (loc_y),\
                        define.RED) 
                self.sprite_list.append(temp)
            else:
                temp = Block((loc_x + (72-(9*(8-i)))), (loc_y),\
                        define.PINK) 
                self.sprite_list.append(temp)

        self.sprite_group = pygame.sprite.Group()

        self.scale = (self.MAX_VALUE - self.MIN_VALUE) / self.block_max 

        self.meter = 0   # how many blocks are showing?

        self.warning_on = False


    def update(self, data, surface, background):

        temp = int(data / self.scale)   

        if self.meter != temp:

            self.sprite_group.clear(surface, background) 
            self.sprite_group.empty()
            for i in range(temp):
                self.sprite_group.add( self.sprite_list[i] )
            self.sprite_group.draw(surface)
            self.meter = temp
    
    def forced_update(self, data, surface, background):

        temp = int(data / self.scale)   

        self.sprite_group.clear(surface, background) 
        self.sprite_group.empty()
        for i in range(temp):
            self.sprite_group.add( self.sprite_list[i] )
        self.sprite_group.draw(surface)
        self.meter = temp


class PanelType5():  # for missile silo indicators

    def __init__(self, loc_x, loc_y):

        self.X_START = loc_x 
        self.Y_START = loc_y 

        self.sprite_list = []
        for i in range(9):
            temp = MissileBlock((loc_x + (22*i)), loc_y, define.WHITE)
            self.sprite_list.append(temp)

        self.sprite_group = pygame.sprite.Group()

        self.meter = 0   # how many blocks are showing?
        
        self.blink_color = define.WHITE

    def blink(self, surface):

        if self.blink_color == define.WHITE:
            self.blink_color = define.RED
            flatland_engine.sound.play_sound_effect('MISSILE_ARMED')
        else:
            self.blink_color = define.WHITE

        # find right-most missile
        right_most = 0
        m = None
        for i in self.sprite_group:
            if i.rect.left > right_most:
                right_most = i.rect.left
                m = i

        if m != None:
            m.image.fill(self.blink_color)

        self.sprite_group.draw(surface)
    
    def no_blink(self, surface):

        for i in self.sprite_group:
            c = i.image.get_at((1,1))
            if c == define.RED:
                i.image.fill(define.WHITE)
                
        self.sprite_group.draw(surface)

    def update(self, ship, surface, background):

        data = ship.equipment[1]
        temp = data

        if temp < 0:
            temp = 0
        elif temp > 4:
            temp = 4

        if self.meter != temp:

            self.sprite_group.clear(surface, background) 
            self.sprite_group.empty()
            for i in range(temp):
                self.sprite_group.add( self.sprite_list[i] )
            self.sprite_group.draw(surface)
            self.meter = temp

    def forced_update(self, data, surface, background):

        temp = data

        if temp < 0:
            temp = 0
        elif temp > 4:
            temp = 4

        self.sprite_group.clear(surface, background) 
        self.sprite_group.empty()
        for i in range(temp):
            self.sprite_group.add( self.sprite_list[i] )
        self.sprite_group.draw(surface)
        self.meter = temp


##############################################################################






class HudPanel():

    def __init__(self, player_ship):

        self.player_ship = player_ship

        self.scanner = Scanner()
        self.compass = Compass(player_ship)

        self.vi = PanelType3( player_ship.MIN_THRUST, player_ship.MAX_THRUST, 527, 7, \
               player_ship.THRUST_WARNING) 
        self.fuel = PanelType1( player_ship.MIN_FUEL, player_ship.MAX_FUEL, 185, 39, \
                define.YELLOW)
        self.energy_banks = PanelType2( 0, player_ship.MAX_ENERGY, 527, 23)

        planet_data = self.player_ship.planet_data
        self.star_x = planet_data.star_x
        self.star_y = planet_data.star_y
        self.star_radius = planet_data.star_radius
        self.planet_x = planet_data.planet_x
        self.planet_y = planet_data.planet_y
        self.planet_radius = planet_data.planet_radius

        self.ai = PanelType1(self.planet_radius, self.planet_radius*4, \
                185, 87, define.BLUE)
        self.ct = PanelType1(self.star_radius*4, self.star_radius, \
                185, 55, define.RED)
        self.lt = PanelType1( 0, 100, 185, 71, \
                define.RED)

        self.fore = PanelType4( 0, player_ship.FORE_SHIELD_MAX, 185, 7)
        self.aft = PanelType4( 0, player_ship.AFT_SHIELD_MAX, 185, 23)

        self.silos = PanelType5(527,87) 
        self.blink_timer =15 

        self.message_timer = 60  # used to prevent spamming HUM messages

    def add_blip(self, obj, blip_size=5):

        self.scanner.add_blip(obj, blip_size)

    def update(self, surface_controller):

        if self.player_ship.state != define.ABANDONED:

            surface = surface_controller.hud_surface
            background = surface_controller.hud_cover

            self.scanner.update()
            self.compass.update()
            self.vi.update(self.player_ship.thrust, surface, background)
            self.fuel.update(self.player_ship.fuel, surface, background)
            self.energy_banks.update(self.player_ship.energy, surface, background)

            d = self.distance(self.planet_x, self.planet_y)
            self.ai.update(d, surface, background)
           
            # cabin temperature indicates proximity to star
            d = self.distance(self.star_x, self.star_y)
            self.ct.update(d, surface, background)

            if self.ct.meter >= 8:
                    
                self.message_timer += 1

                if self.player_ship.equipment[objects.FUEL_SCOOP] == True:


                    if self.player_ship.fuel < \
                            (self.player_ship.MAX_FUEL - 0.2):
                        self.player_ship.install_fuel(0.13)

                    if self.message_timer >= 60:

                        if self.player_ship.fuel >= \
                                (self.player_ship.MAX_FUEL - 0.2):
                            self.player_ship.add_hud_message('FUEL TANK FULL', 24, \
                                    define.CYAN, False)
                            self.message_timer = 0
                        else:
                            self.player_ship.add_hud_message('COLLECTING FUEL FROM STAR', 24, \
                                    define.YELLOW, False)
                            self.message_timer = 0
                else:

                    if self.message_timer >= 60:
                    
                        self.player_ship.add_hud_message(\
                            'NEED FUEL SCOOP TO COLLECT FUEL FROM STAR', 24, \
                            define.BLUE, False)

                        self.message_timer = 0

            self.lt.update(self.player_ship.laser_temp, surface, background)

            self.fore.update(self.player_ship.fore_shield, surface, background)
            self.aft.update(self.player_ship.aft_shield, surface, background)

            self.silos.update(self.player_ship, surface, background)

            if self.player_ship.auto_targeting_on == True:
                self.blink_timer -= 1
                if self.blink_timer <= 0:
                    self.silos.blink(surface)
                    self.blink_timer = 15 
            else:
                self.silos.no_blink(surface)


            # warning messages

            if self.ai.meter <= 5:
                if self.ai.warning_on == False:
                    self.ai.warning_on = True
                    flatland_engine.sound.play_sound_effect('BEEP')
                    self.player_ship.add_hud_message('LOW ALTITUDE WARNING!', 31, \
                            define.RED, False)
            else:
                self.ai.warning_on = False

            if self.ct.meter >= 1:
                if self.ct.warning_on == False:
                    self.ct.warning_on = True 
                    flatland_engine.sound.play_sound_effect('BEEP')
                    self.player_ship.add_hud_message('CABIN TEMPERATURE WARNING!', 29, \
                            define.RED, False)
            else:
                self.ct.warning_on = False

            if self.fuel.meter <= 3:
                if self.fuel.warning_on == False:
                    self.fuel.warning_on = True 
                    flatland_engine.sound.play_sound_effect('BEEP')
                    self.player_ship.add_hud_message('LOW FUEL WARNING!', 27, \
                            define.RED, False)
            else:
                self.fuel.warning_on = False
            
            if self.energy_banks.meter <= 18:
                if self.energy_banks.warning_on == False:
                    self.energy_banks.warning_on = True 
                    flatland_engine.sound.play_sound_effect('BEEP')
                    self.player_ship.add_hud_message('LOW ENERGY WARNING!', 25, \
                            define.CYAN, False)
            else:
                self.energy_banks.warning_on = False

            if self.fore.meter <= 0:
                if self.fore.warning_on == False:
                    self.fore.warning_on = True 
                    flatland_engine.sound.play_sound_effect('BEEP')
                    self.player_ship.add_hud_message('FORE SHIELD DEPLETED', 23, \
                            define.RED, False)
            else:
                self.fore.warning_on = False
            
            if self.aft.meter <= 0:
                if self.aft.warning_on == False:
                    self.aft.warning_on = True 
                    flatland_engine.sound.play_sound_effect('BEEP')
                    self.player_ship.add_hud_message('  AFT SHIELD DEPLETED  ', 23, \
                            define.RED, False)
            else:
                self.aft.warning_on = False
        
        else: 

            hud_image = pygame.image.load('images/hud.png').convert()
            surface_controller.hud_surface.blit(hud_image, (0,0))
            surface_controller.hud_cover = surface_controller.hud_surface.copy() 
            
            surface = surface_controller.hud_cover
            background = surface_controller.hud_cover

    def distance(self, x, y):

        dx = self.player_ship.global_x - x
        dy = self.player_ship.global_y - y
        return int(math.sqrt( (dx*dx) + (dy*dy) ))

    def draw(self, surface_controller):

        if self.player_ship.state != define.ABANDONED:

            surface = surface_controller.hud_surface

            # scanner drawing
            dest = (284, 6)
           
            area_rect = pygame.Rect( \
                    (self.player_ship.scanner_x+80) - 60, \
                    (self.player_ship.scanner_y+60) - 45, \
                    120, 90)
            
            surface.blit(self.scanner.full_image, dest, area_rect)

            # compass drawing
            dest = (430, 12)
            surface.blit(self.compass.full_image, dest)

        else:

            pass
    
    def forced_update(self, surface_controller):

        hud_image = pygame.image.load('images/hud.png').convert()
        surface_controller.hud_surface.blit(hud_image, (0,0))
        surface_controller.hud_cover = surface_controller.hud_surface.copy() 
        
        surface = surface_controller.hud_surface
        background = surface_controller.hud_cover

        self.scanner.update()
        self.compass.update()
        self.vi.forced_update(self.player_ship.thrust, surface, background)
        self.fuel.forced_update(self.player_ship.fuel, surface, background)
        self.energy_banks.forced_update(self.player_ship.energy, surface, background)

        d = self.distance(self.planet_x, self.planet_y)
        self.ai.forced_update(d, surface, background)
       
        # cabin temperature indicates proximity to star
        d = self.distance(self.star_x, self.star_y)
        self.ct.forced_update(d, surface, background)

        self.lt.forced_update(self.player_ship.laser_temp, surface, background)

        self.fore.forced_update(self.player_ship.fore_shield, surface, background)
        self.aft.forced_update(self.player_ship.aft_shield, surface, background)

        self.silos.forced_update(self.player_ship.equipment[1], surface, background)


