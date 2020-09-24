# Author: Darron Vanaria
# Filesize: 106410 bytes
# LOC: 2197

import pygame
import random
import sys
import math

import define
import game_engine
import hud
import screens
import tga_generator
import flatland_engine
import planet_database

# graphics state (double duty, as state-identifiers and as reset values)
NORMAL              = 0
SHIELDS_ENGAGED     = 15  # number of frames to show shield on
RECEIVING_DAMAGE    = 7   # number of frames to show damage cloud 
DISINTEGRATING      = 70  # number of frames to show final explosion
GONE                = 100

# pilot behavior (non-player-character AI)
FLY_STRAIGHT        = 0
COLLISION_AVOIDANCE = 1
ATTACK_AVOIDANCE    = 2

COMMODITY_NAME = { \
        0:'Food        ', \
        1:'Textiles    ', \
        2:'Radioactives', \
        3:'Slaves      ', \
        4:'Liquor/Wine ', \
        5:'Luxuries    ', \
        6:'Narcotics   ', \
        7:'Computers   ', \
        8:'Machinery   ', \
        9:'Alloys      ', \
       10:'Firearms    ', \
       11:'Furs        ', \
       12:'Minerals    ', \
       13:'Gold        ', \
       14:'Platinum    ', \
       15:'Gem-Stones  ', \
       16:'Alien Items ' }

# ship equipment
NUM_EQUIPMENT_TYPES   = 13 
FUEL                  = 0
MISSILE               = 1
LARGE_CARGO_BAY       = 2
ECM_SYSTEM            = 3
PULSE_LASER           = 4
BEAM_LASER            = 5
FUEL_SCOOP            = 6
ESCAPE_CAPSULE        = 7
ENERGY_BOMB           = 8
EXTRA_ENERGY_UNIT     = 9
DOCKING_COMPUTER      = 10
MINING_LASER          = 11
MILITARY_LASER        = 12

# ship directions
FORE      = 0
PORT      = 1
AFT       = 2
STARBOARD = 3

# ship laser type
PULSE     = 0
BEAM      = 1
MINING    = 2
MILITARY  = 3

class Object(pygame.sprite.Sprite):

    def __init__(self, image, x, y):

        # a generic game object.
        
        # pass in an image (Surface), object dimensions will be pulled from 
        # this, (x,y) will be the center of the object (best to pass in 
        # an image that is an odd number of pixels for both width and height)

        # all Sprites must have an 'image' attribute and a 'rect' attribute

        self.image = image 

        # global (star-system-wide) coordinates are always updated
        self.global_x = x
        self.global_y = y
        
        # rect coordinates will always be local (screen-wide)
        self.rect = self.image.get_rect()
        self.rect.centerx = x % define.FLIGHT_W 
        self.rect.centery = y % define.FLIGHT_H
       
        # call parent constructor
        pygame.sprite.Sprite.__init__(self)

        # sector coordinates (sectors are 0-7)
        self.sector_x = int(self.global_x / define.FLIGHT_W)
        self.sector_y = int(self.global_y / define.FLIGHT_H)

        # scanner coordinates (120 x 90 pixels covers 3 x 3 sectors)
        self.scanner_x = int(self.global_x / define.SCANNER_SCALE_W)
        self.scanner_y = int(self.global_y / define.SCANNER_SCALE_H)

        # collision detection will be done using circles, for all objects
        average_size = int((self.rect.width + self.rect.height) / 2)
        self.radius = int(average_size / 2)

        # object properties ##################################################
        self.color = define.WHITE
        self.energy = 100 # hit points, 0 = destruction 
        self.mass = 30.0 # damage caused to others when collision occurs 
        
        # movement components (angle = "orientation") and (magnitude = "thrust")
        self.ORIENTATION_DELTA = 1.1       # orientation change per frame, if turning
        self.orientation = float(random.randint(0,359))  # degrees, float
        self.THRUST_DELTA = 0.18    # thrust change per frame, if thrusting
        self.MAX_THRUST = 3.0       
        self.MIN_THRUST = 1.0 
        self.thrust = random.randint(self.MIN_THRUST,self.MAX_THRUST)
        self.dx = 0  # components of vector
        self.dy = 0  # components of vector

        # calculate components based on vector orientation and magnitude
        self.recalculate_displacement()
        
        # graphics helpers 
        self.object_image = self.image 
        self.rotation_image = self.image # used for clean rotations
        self.graphics_state = NORMAL
        self.graphics_state_countdown = 0   # how many frames to show graphics/effects?
           
        # image of object receiving damage
        self.damage_image = pygame.image.load('images/damage.png').convert()
        outer_rect = self.damage_image.get_rect()
        temp_image = self.object_image.copy()
        inner_rect = temp_image.get_rect()
        blit_x = int((outer_rect.width / 2) - (inner_rect.width/2))
        blit_y = int((outer_rect.height / 2) - (inner_rect.height/2))
        self.damage_image.blit(temp_image, (blit_x,blit_y))
        self.damage_image.set_colorkey(define.BLACK)
        
        # image of object with missile targeting lock 
        self.target_image = pygame.image.load('images/target.png').convert()
        outer_rect = self.target_image.get_rect()
        temp_image = self.object_image.copy()
        inner_rect = temp_image.get_rect()
        blit_x = int((outer_rect.width / 2) - (inner_rect.width/2))
        blit_y = int((outer_rect.height / 2) - (inner_rect.height/2))
        self.target_image.blit(temp_image, (blit_x,blit_y))
        self.target_image.set_colorkey(define.BLACK)
        
        self.prerender_rotation()

        self.bounty = 0.01

        self.targeted = False

        self.name = 'OBJECT'

    def prerender_rotation(self):

        # If this object is included in the current 'draw_group', the image
        # must be created according to the object's current orientation.

        # step 1: save old center coordinates
        old_x = self.rect.centerx
        old_y = self.rect.centery

        # step 2: create new surface (rotated)
        self.image = pygame.transform.rotate(self.rotation_image, self.orientation)

        # step 3: correct center of new image
        self.rect = self.image.get_rect()
        self.rect.centerx = old_x
        self.rect.centery = old_y

        # Now self.image is correctly rotated and ready to be blitted at the
        # desired location.

    def adjust_thrust(self, t):

        self.thrust += t

        if self.thrust > self.MAX_THRUST:
            self.thrust = self.MAX_THRUST
        elif self.thrust < self.MIN_THRUST:
            self.thrust = self.MIN_THRUST

    def adjust_orientation(self, o):

        self.orientation = float((self.orientation + o) % 360.0)

    def recalculate_displacement(self):

        # uses the vector angle (orientation) and magnitude (thrust) to
        # calculate dx,dy components.

        self.dx = self.thrust * math.cos(math.radians(self.orientation))
        self.dy = self.thrust * math.sin(math.radians(self.orientation))

        self.dy = -self.dy   

    def update(self):

        # update global coordinates
        self.global_x += self.dx 
        self.global_y += self.dy 
        
        # account for system wrap-around when updating global coordinates
        self.global_x = self.global_x % define.SYSTEM_W
        self.global_y = self.global_y % define.SYSTEM_H

        # update rect coordinates (will always be local)
        self.rect.centerx = self.global_x % define.FLIGHT_W
        self.rect.centery = self.global_y % define.FLIGHT_H
   
        # update current sector
        self.sector_x = int(self.global_x / define.FLIGHT_W)
        self.sector_y = int(self.global_y / define.FLIGHT_H)

        # update scanner coordinates
        self.scanner_x = int(self.global_x / define.SCANNER_SCALE_W)
        self.scanner_y = int(self.global_y / define.SCANNER_SCALE_H)

        # status handler
        if self.graphics_state == RECEIVING_DAMAGE:
            self.graphics_state_countdown -= 1
            if self.graphics_state_countdown < 0:
                self.graphics_state_countdown = 0 
                self.graphics_state = NORMAL
                if self.targeted == False:
                    self.image = self.object_image
                    self.rotation_image = self.object_image.copy()
                else:
                    self.add_targeting_square()
                self.prerender_rotation()
        elif self.graphics_state == DISINTEGRATING:
            self.graphics_state_countdown -= 1
            if self.graphics_state_countdown < 0:
                self.graphics_state = GONE
                self.kill()


    def damage_handler(self, damage, obj_source=None):

        self.energy -= damage

        if self.energy > 0:

            self.graphics_state = RECEIVING_DAMAGE
            self.graphics_state_countdown = RECEIVING_DAMAGE

            self.image = self.damage_image
            self.rect = self.image.get_rect()
            self.rect.centerx = self.global_x % define.FLIGHT_W 
            self.rect.centery = self.global_y % define.FLIGHT_H
            self.rotation_image = self.image.copy()
            self.prerender_rotation()
                   
            pick = random.choice( ['MINOR_EXPLOSION_1', \
                    'MINOR_EXPLOSION_2', 'MINOR_EXPLOSION_3', \
                    'MINOR_EXPLOSION_4']  )
            flatland_engine.sound.play_sound_effect(pick)

            
        elif self.energy <= 0: # object destroyed!

            self.graphics_state = DISINTEGRATING
            self.graphics_state_countdown = DISINTEGRATING 

            self.image = pygame.image.load('images/disintegrate.png').convert()
            self.image.set_colorkey(define.BLACK)
            self.rotation_image = self.image.copy() # used for rotation 
            self.prerender_rotation()

            self.targeted = False
           
            pick = \
                random.choice(['EXPLODE_1','EXPLODE_2','EXPLODE_3','EXPLODE_4'])
            flatland_engine.sound.play_sound_effect(pick)

    def collision_detection(self, draw_group):

        pass

    def add_targeting_square(self):

        self.image = self.target_image
        self.rect = self.image.get_rect()
        self.rect.centerx = self.global_x % define.FLIGHT_W 
        self.rect.centery = self.global_y % define.FLIGHT_H
        self.rotation_image = self.image.copy()
        self.prerender_rotation()
    
    def remove_targeting_square(self):

        self.image = self.object_image
        self.rect = self.image.get_rect()
        self.rect.centerx = self.global_x % define.FLIGHT_W 
        self.rect.centery = self.global_y % define.FLIGHT_H
        self.rotation_image = self.image.copy()
        self.prerender_rotation()

class EscapeCapsule(Object):

    def __init__(self, ship):

        self.ship = ship

        image = pygame.image.load('images/capsule.png').convert()
        image.set_colorkey(define.BLACK)

        x = ship.global_x 
        y = ship.global_y 

        # call parent constructor
        Object.__init__(self, image, x, y)

        # initial rotation per frame
        self.spin = random.random() * random.choice([-4.5,4.5])
        self.color = define.CYAN
        self.energy = 40
        self.mass = 20

        # calculate trajectory to space station
        p1 = game_engine.Point(self.global_x,self.global_y)
        p2 = game_engine.Point(ship.planet_data.station_x,\
                ship.planet_data.station_y)
        v = game_engine.Vector(p1,p2)

        # normalize vector
        self.dx = (v.x / v.mag) * 3 
        self.dy = (v.y / v.mag) * 3
        self.dy = -self.dy

        self.successful_return = False

        self.name = 'ESCAPE CAPSULE'

    def update(self):

        # call parent update()
        Object.update(self)

        if self.graphics_state != DISINTEGRATING:
            self.adjust_orientation(self.spin)

    def collision_detection(self, draw_group):

        hit_list = pygame.sprite.spritecollide(self, draw_group, False, \
                    pygame.sprite.collide_circle)

        for h in hit_list:

            if isinstance(h, Station) == True:

                self.successful_return = True

class Asteroid(Object):

    def __init__(self):

        image = pygame.image.load('images/asteroid.png').convert()
        image.set_colorkey(define.BLACK)

        x = random.randint(0,define.SYSTEM_W)
        y = random.randint(0,define.SYSTEM_H)

        # call parent constructor
        Object.__init__(self, image, x, y)

        # initial rotation per frame
        self.spin = random.random() * random.choice([-4.5,4.5])
        self.color = define.OLIVE
        self.energy = 40
        self.mass = 80

        self.bounty = random.random() * 10.00

        self.converted_to_shard = False

        self.name = 'ASTEROID'

    def update(self):

        # call parent update()
        Object.update(self)

        if self.graphics_state != DISINTEGRATING:
            self.adjust_orientation(self.spin)

        if self.energy == 1 and self.converted_to_shard == False:
            self.converted_to_shard = True

    def collision_detection(self, draw_group):

        hit_list = pygame.sprite.spritecollide(self, draw_group, False, \
                    pygame.sprite.collide_circle)

        for h in hit_list:

            if self == h or h.graphics_state == DISINTEGRATING or \
                    (isinstance(h, PlayerShip) and \
                    self.converted_to_shard == True):

                pass

            else:

                self.damage_handler(h.mass, h)

                h.damage_handler(self.mass, self)


class Shard(Object):

    def __init__(self, x, y):

        image = pygame.image.load('images/shard.png').convert()
        image.set_colorkey(define.BLACK)

        # call parent constructor
        Object.__init__(self, image, x, y)

        # initial rotation per frame
        self.spin = random.random() * random.choice([-4.5,4.5])
        self.color = define.CYAN
        self.energy = 100 
        self.mass = 80

        self.bounty = random.random() * 10.00

        self.name = 'ASTEROID SHARD'

    def update(self):

        # call parent update()
        Object.update(self)

        if self.graphics_state != DISINTEGRATING:
            self.adjust_orientation(self.spin)

    def collision_detection(self, draw_group):

        hit_list = pygame.sprite.spritecollide(self, draw_group, False, \
                    pygame.sprite.collide_circle)

        for h in hit_list:

            if self == h or h.graphics_state == DISINTEGRATING or \
                    isinstance(h, PlayerShip):

                pass

            else:

                self.damage_handler(h.mass, h)

                h.damage_handler(self.mass, self)


class Station(Object):

    def __init__(self, planet_data):
        
        image = pygame.image.load('images/coriolis_station.png').convert()
        image.set_colorkey(define.BLACK)

        x = planet_data.station_x
        y = planet_data.station_y

        # call parent constructor
        Object.__init__(self, image, x, y)

        self.thrust = 0

        # initial rotation per frame
        self.spin = random.choice([-0.5,0.5])
        self.color = define.CYAN
        self.energy = 65536 
        self.ENERGY_RECHARGE_RATE = 256 
        self.MAX_ENERGY = 65536 
        self.mass = 65536 

        self.radius = 20

        self.name = 'STATION'
        
    def update(self):

        self.adjust_orientation(self.spin)
   
    def update_sector_offset(self, sector_x, sector_y):

        # modify rect coordinates to be dependent on current sector
        # (why? to draw very large objects on the current screen even if the
        # center of that object is in a neighboring sector).
        
        offset_x = (sector_x * define.FLIGHT_W) - self.global_x
        offset_y = (sector_y * define.FLIGHT_H) - self.global_y

        self.rect.centerx = -offset_x 
        self.rect.centery = -offset_y 

    def damage_handler(self, damage, obj_source=None):

        pass 

    def collision_detection(self, draw_group):

        pass

class Star(Object):

    def __init__(self, planet_data):
        
        x = planet_data.star_x
        y = planet_data.star_y
        
        radius = planet_data.star_radius
        c = planet_data.star_color
        image = pygame.Surface((radius*2, radius*2))
        image.fill(define.BLACK)
        pygame.draw.circle(image, c, (radius, radius), radius)
        image.set_colorkey(define.BLACK)

        # call parent constructor
        Object.__init__(self, image, x, y)

        self.color = define.WHITE
        self.energy = 65536 
        self.ENERGY_RECHARGE_RATE = 256 
        self.MAX_ENERGY = 65536 
        self.mass = 65536 

        self.name = 'STAR'
        
    def update_sector_offset(self, sector_x, sector_y):

        # modify rect coordinates to be dependent on current sector
        # (why? to draw very large objects on the current screen even if the
        # center of that object is in a neighboring sector).
        
        offset_x = (sector_x * define.FLIGHT_W) - self.global_x
        offset_y = (sector_y * define.FLIGHT_H) - self.global_y

        self.rect.centerx = -offset_x 
        self.rect.centery = -offset_y 

    def damage_handler(self, damage, obj_source=None):

        pass 
    
    def update(self):

        pass
    
    def collision_detection(self, draw_group):

        pass

class Planet(Object):

    def __init__(self, planet_data):
        
        x = planet_data.planet_x
        y = planet_data.planet_y
        
        radius = planet_data.planet_radius
        c = planet_data.planet_color
        image = pygame.Surface((radius*2, radius*2))
        image.fill(define.BLACK)
        pygame.draw.circle(image, c, (radius, radius), radius)
        image.set_colorkey(define.BLACK)

        # call parent constructor
        Object.__init__(self, image, x, y)

        self.color = define.BLUE
        self.energy = 65536 
        self.ENERGY_RECHARGE_RATE = 256 
        self.MAX_ENERGY = 65536 
        self.mass = 65536 

        self.name = 'PLANET'
        
    def update_sector_offset(self, sector_x, sector_y):

        # modify rect coordinates to be dependent on current sector
        # (why? to draw very large objects on the current screen even if the
        # center of that object is in a neighboring sector).
       
        offset_x = (sector_x * define.FLIGHT_W) - self.global_x
        offset_y = (sector_y * define.FLIGHT_H) - self.global_y

        self.rect.centerx = -offset_x 
        self.rect.centery = -offset_y 

    def damage_handler(self, damage, obj_source=None):

        pass 
    
    def update(self):

        pass

    def collision_detection(self, draw_group):

        pass

class Ship(Object):

    def __init__(self, image, x, y, planet_data, ship_type):

        self.planet_data = planet_data 
        self.state = define.FLYING 

        # call parent constructor
        Object.__init__(self, image, x, y)

        # line of sight, Vectors that use local coordinates, from ship to
        # distance sight directions in all four cardinal directions
        # Reminder of game_engine.Vector:
        # 3 items are stored: 1. the displacement from center (x,y)
        #                     2. origin (local coordinates, ship center) p1
        #                     3. LOS tip (local coordinates) p2
        self.LINE_OF_SIGHT_DISTANCE = 570  # how far can pilot see?
        self.LOS_vector = None 
        self.recalculate_line_of_sight()

        # lasers ############################################################
        # note: each time a laser is fired, it heats up the gun by a certain
        #       degree, and it takes time for the gun to re-energize in 
        #       order to fire again. If the gun overheats, the re-energize
        #       time is increased by a factor of 3 (or similar)

        self.laser_coordinates = [0,0,0,0] # to draw and erase laser beam
        self.laser_temp        = 0         # for hud meter (max = 100)
        self.laser_recharge    = 0         # how fast can laser fire?
        self.laser_discharged  = False
        
        self.LASER_TEMP_PER_FIRE      = 10 # how fast gun heats up?
        self.LASER_POWER              = 25 # how much damage does it do?
        self.LASER_RECHARGE_RATE_COOL = 10 # number of MS till re-fire possible
        self.LASER_RECHARGE_RATE_HOT  = 30  

        self.fore_laser      = None 
        self.aft_laser       = None
        self.port_laser      = None
        self.starboard_laser = None
        ####################################################################

        self.name = 'SHIP'
        self.ship_type = -1

        self.mass = random.randrange(75,120)
        
        self.ENERGY_RECHARGE_RATE = 0.0027 
        self.MAX_ENERGY = 400
        self.energy = self.MAX_ENERGY
       
        if ship_type == define.ADDER:
            self.MAX_THRUST = 3.3
            self.MIN_THRUST = 0.5 
            self.THRUST_DELTA = 0.09    # thrust change per frame, if thrusting
            self.ORIENTATION_DELTA = 1.8    # orientation change per frame, if turning
            self.ship_name = "ADDER"
        elif ship_type == define.ANACONDA:
            self.MAX_THRUST = 2.3
            self.MIN_THRUST = 0.5 
            self.THRUST_DELTA = 0.03   
            self.ORIENTATION_DELTA = 0.9 
            self.ship_name = "ANACONDA"
        elif ship_type == define.ASP_MK_II:
            self.MAX_THRUST = 4.3
            self.MIN_THRUST = 1.2 
            self.THRUST_DELTA = 0.11   
            self.ORIENTATION_DELTA = 1.3 
            self.ship_name = "ASP MK II"
        elif ship_type == define.BOA_CLASS_CRUISER:
            self.MAX_THRUST = 2.3
            self.MIN_THRUST = 0.5 
            self.THRUST_DELTA = 0.13   
            self.ORIENTATION_DELTA = 1.1 
            self.ship_name = "BOA CLASS CRUISER"
        elif ship_type == define.COBRA_MK_I:
            self.MAX_THRUST = 4.3
            self.MIN_THRUST = 1.0 
            self.THRUST_DELTA = 0.09   
            self.ORIENTATION_DELTA = 1.2 
            self.ship_name = "COBRA MK I"
        elif ship_type == define.COBRA_MK_III:
            self.MAX_THRUST = 4.8
            self.MIN_THRUST = 1.2 
            self.THRUST_DELTA = 0.12   
            self.ORIENTATION_DELTA = 2.1 
            self.ship_name = "COBRA_MK_III"
        elif ship_type == define.FER_DE_LANCE:
            self.MAX_THRUST = 4.9
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.14   
            self.ORIENTATION_DELTA = 0.9 
            self.ship_name = "FER DE LANCE"
        elif ship_type == define.GECKO:
            self.MAX_THRUST = 3.9
            self.MIN_THRUST = 0.6 
            self.THRUST_DELTA = 0.14   
            self.ORIENTATION_DELTA = 1.6 
            self.ship_name = "GECKO"
        elif ship_type == define.KRAIT:
            self.MAX_THRUST = 4.1
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.24   
            self.ORIENTATION_DELTA = 1.8 
            self.ship_name = "KRAIT"
        elif ship_type == define.MAMBA:
            self.MAX_THRUST = 4.1
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.24   
            self.ORIENTATION_DELTA = 1.8 
            self.ship_name = "MAMBA"
        elif ship_type == define.MORAY_STAR_BOAT:
            self.MAX_THRUST = 4.1
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.24   
            self.ORIENTATION_DELTA = 1.8 
            self.ship_name = "MORAY STAR BOAT"
        elif ship_type == define.PYTHON:
            self.MAX_THRUST = 4.1
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.24   
            self.ORIENTATION_DELTA = 1.8 
            self.ship_name = "PYTHON"
        elif ship_type == define.SIDEWINDER:
            self.MAX_THRUST = 4.1
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.24   
            self.ORIENTATION_DELTA = 1.8 
            self.ship_name = "SIDEWINDER"
        elif ship_type == define.THARGOID:
            self.MAX_THRUST = 6.1
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.34   
            self.ORIENTATION_DELTA = 2.2 
            self.ship_name = "THARGOID"
        elif ship_type == define.TRANSPORTER:
            self.MAX_THRUST = 4.1
            self.MIN_THRUST = 0.9 
            self.THRUST_DELTA = 0.24   
            self.ORIENTATION_DELTA = 1.8 
            self.ship_name = "TRANSPORTER"
        elif ship_type == define.VIPER:
            self.MAX_THRUST = 5.3
            self.MIN_THRUST = 0.7 
            self.THRUST_DELTA = 0.20   
            self.ORIENTATION_DELTA = 1.9   
            self.ship_name = "VIPER"
        elif ship_type == define.MISSILE:
            self.MAX_THRUST = 6.3 
            self.MIN_THRUST = 0.0 
            self.THRUST_DELTA = 0.18    
            self.ORIENTATION_DELTA = 13.8
            self.ship_name = "MISSILE"
        
        self.equipment = [0] * NUM_EQUIPMENT_TYPES    # installed equipment

        # initialize
        self.add_laser(FORE, PULSE_LASER)
        self.equipment[MISSILE] = 3
        self.equipment[FUEL] = 8.0

        self.launch_missile = False
        self.cargo_ejected = False   # set to true on ship destruction
        
        self.missile_attack_wait = 0  # don't allow rapid-fire
        self.ecm_attack_wait = 0     
        self.bomb_attack_wait = 0

        self.ecm_activated = False
        self.bomb_activated = False

        self.missile_target = None

        self.laser_sound = 'LASER_1'

    def add_laser(self, direction, laser_name):

        # first make sure that bay is available:
        if direction == FORE:
            laser_installed = self.fore_laser
        elif direction == PORT:
            laser_installed = self.port_laser
        elif direction == AFT:
            laser_installed = self.aft_laser
        elif direction == STARBOARD:
            laser_installed = self.starboard_laser

        if laser_installed == None:

            if self.equipment[laser_name] < 4:

                self.equipment[laser_name] += 1

                if direction == FORE:
                    if laser_name == PULSE_LASER:
                        self.fore_laser = PULSE
                    elif laser_name == BEAM_LASER:
                        self.fore_laser = BEAM
                    elif laser_name == MINING_LASER:
                        self.fore_laser = MINING 
                    elif laser_name == MILITARY_LASER:
                        self.fore_laser = MILITARY 
                elif direction == PORT:
                    if laser_name == PULSE_LASER:
                        self.port_laser = PULSE
                    elif laser_name == BEAM_LASER:
                        self.port_laser = BEAM
                    elif laser_name == MINING_LASER:
                        self.port_laser = MINING 
                    elif laser_name == MILITARY_LASER:
                        self.port_laser = MILITARY 
                elif direction == AFT:
                    if laser_name == PULSE_LASER:
                        self.aft_laser = PULSE
                    elif laser_name == BEAM_LASER:
                        self.aft_laser = BEAM
                    elif laser_name == MINING_LASER:
                        self.aft_laser = MINING 
                    elif laser_name == MILITARY_LASER:
                        self.aft_laser = MILITARY 
                elif direction == STARBOARD:
                    if laser_name == PULSE_LASER:
                        self.starboard_laser = PULSE
                    elif laser_name == BEAM_LASER:
                        self.starboard_laser = BEAM
                    elif laser_name == MINING_LASER:
                        self.starboard_laser = MINING 
                    elif laser_name == MILITARY_LASER:
                        self.starboard_laser = MILITARY 

                return True

            else:

                return False

        else:

            return False

        
    def dock(self):

        self.state = define.DOCKED
        
        self.global_x = self.planet_data.station_x
        self.global_y = self.planet_data.station_y 
        
        self.scanner_x = int(self.global_x / define.SCANNER_SCALE_W)
        self.scanner_y = int(self.global_y / define.SCANNER_SCALE_H)

        self.thrust = 0
        self.dx = 0  # components of vector
        self.dy = 0  # components of vector

    def launch(self):

        self.state = define.CLEARING_STATION

        self.orientation = float(random.randint(0,359))  # degrees, float
        self.thrust = 2.0 
        self.recalculate_displacement()

        self.prerender_rotation() 

    def turn_ship(self, direction):

        # direction should be +1 (turn left) or -1 (turn right)
 
        self.adjust_orientation(self.ORIENTATION_DELTA * direction)

        self.recalculate_displacement()

    def throttle_ship(self, direction):

        # direction should be +1 (speed up) or -1 (slow down)

        self.adjust_thrust(self.THRUST_DELTA * direction)
        
        self.recalculate_displacement()

    def fire_laser(self, tx, ty, laser_type):
       
        # can the laser discharge at this moment?
        if self.laser_recharge <= 0 and self.laser_discharged == False:

            p1 = game_engine.Point(self.rect.centerx, self.rect.centery)
            p2 = game_engine.Point(tx,ty)

            v = game_engine.Vector(p1, p2)

            self.laser_coordinates = [v.p1.x, v.p1.y, v.p2.x, v.p2.y] 

            if laser_type == PULSE:
        
                self.LASER_TEMP_PER_FIRE      = 17 
                self.LASER_POWER              = 25
                self.LASER_RECHARGE_RATE_COOL = 8 
                self.LASER_RECHARGE_RATE_HOT  = 15  

            elif laser_type == BEAM:
        
                self.LASER_TEMP_PER_FIRE      = 7 
                self.LASER_POWER              = 25
                self.LASER_RECHARGE_RATE_COOL = 3 
                self.LASER_RECHARGE_RATE_HOT  = 6  

            elif laser_type == MINING:
        
                self.LASER_TEMP_PER_FIRE      = 7 
                self.LASER_POWER              = 39  # asteroids have energy 40 
                self.LASER_RECHARGE_RATE_COOL = 4 
                self.LASER_RECHARGE_RATE_HOT  = 8  

            elif laser_type == MILITARY:
        
                self.LASER_TEMP_PER_FIRE      = 8 
                self.LASER_POWER              = 50 
                self.LASER_RECHARGE_RATE_COOL = 3 
                self.LASER_RECHARGE_RATE_HOT  = 7  


            
            self.laser_recharge = self.LASER_RECHARGE_RATE_COOL 

            self.laser_temp += self.LASER_TEMP_PER_FIRE

            if self.laser_temp >= 100:
                self.laser_temp = 100
                self.laser_recharge = self.LASER_RECHARGE_RATE_HOT 

            
            self.laser_discharged = True

            
            return True

        else:

            return False

    def update(self):

        # call parent update()
        Object.update(self)

        # LOS
        self.recalculate_line_of_sight()

        # laser update
        if self.laser_recharge > 0:
            self.laser_recharge -= 1
        if self.laser_temp > 0:
            self.laser_temp -= 1
       
        # energy recharge
        self.energy += self.ENERGY_RECHARGE_RATE
        if self.energy > self.MAX_ENERGY:
            self.energy = self.MAX_ENERGY

        # launching from station
        if self.state == define.CLEARING_STATION:
            dx = self.global_x - self.planet_data.station_x
            dy = self.global_y - self.planet_data.station_y
            distance = math.sqrt( dx*dx + dy*dy )
            if distance > 170:
                self.state = define.FLYING
            
    def recalculate_line_of_sight(self):

        # LOS vector always uses local coordinates only

        x = self.LINE_OF_SIGHT_DISTANCE * math.cos(math.radians(self.orientation))
        y = self.LINE_OF_SIGHT_DISTANCE * math.sin(math.radians(self.orientation))
        y = -y

        p1 = game_engine.Point(self.rect.centerx, self.rect.centery)
        p2 = game_engine.Point(p1.x + x, p1.y + y)

        self.LOS_vector = game_engine.Vector(p1,p2)

    def get_alternate_line_of_sight(self, degrees):

        alt = (self.orientation + degrees) % 360

        x = self.LINE_OF_SIGHT_DISTANCE * math.cos(math.radians(alt))
        y = self.LINE_OF_SIGHT_DISTANCE * math.sin(math.radians(alt))
        y = -y

        p1 = game_engine.Point(self.rect.centerx, self.rect.centery)
        p2 = game_engine.Point(p1.x + x, p1.y + y)

        return game_engine.Vector(p1,p2)


class NonPlayerShip(Ship):

    def __init__(self, image, planet_data, ship_type):

        x = random.randint(0,define.SYSTEM_W) 
        y = random.randint(0,define.SYSTEM_H) 

        # call parent constructor
        Ship.__init__(self, image, x, y, planet_data, ship_type)
       
        # AI ############################################ 
        self.COLLISION_AVOIDANCE_DURATION = random.randint(45,85)   
        self.collision_avoidance_direction = -1
        self.collision_avoidance_timer = self.COLLISION_AVOIDANCE_DURATION

        self.ATTACK_AVOIDANCE_DURATION = random.randint(25,45)   
        self.attack_avoidance_direction = -1
        self.attack_avoidance_timer = self.ATTACK_AVOIDANCE_DURATION

        # pilot behavior (non-player character AI)
        #    FLY_STRAIGHT        = 0
        #    COLLISION_AVOIDANCE = 1
        #    TRACKING_ENEMY      = 2
        self.ai_state = FLY_STRAIGHT
        ##################################################
        
        self.MAX_ENERGY = 300 
        self.energy = self.MAX_ENERGY 
        self.ENERGY_RECHARGE_RATE = 0.0028 
        
        self.shield_threshold = int(0.40 * self.MAX_ENERGY) 

        # image of ship with shields active
        self.shield_image = pygame.image.load('images/shield.png').convert()
        self.shield_rect = self.shield_image.get_rect()
        temp_rect = self.object_image.get_rect()
        blit_x = int(self.shield_rect.width/2) - int(temp_rect.width/2)
        blit_y = int(self.shield_rect.height/2) - int(temp_rect.height/2)
        self.shield_image.blit(self.object_image, (blit_x,blit_y))
        self.shield_image.set_colorkey(define.BLACK)
        
        # how many more lasers to install?
        num_lasers = random.randint(1,4)
        for i in range(num_lasers):
            laser_type = random.randint(0,3)
            location = random.randint(0,3)
            self.add_laser(location, laser_type)
        self.equipment[MISSILE] = random.randint(2,4)

    def on_screen_pilot_AI(self, draw_group):

        v = self.LOS_vector

        for i in draw_group:

            if i != self:

                if v.collision_with_circle(i.rect.centerx, \
                    i.rect.centery, i.radius) == True:

                    if i.graphics_state != DISINTEGRATING:
                        self.object_sighted_handler(i, FORE, v)

                v = self.get_alternate_line_of_sight(90)

                if v.collision_with_circle(i.rect.centerx, \
                    i.rect.centery, i.radius) == True:

                    if i.graphics_state != DISINTEGRATING:
                        self.object_sighted_handler(i, PORT, v)

                v = self.get_alternate_line_of_sight(180)
                
                if v.collision_with_circle(i.rect.centerx, \
                    i.rect.centery, i.radius) == True:

                    if i.graphics_state != DISINTEGRATING:
                        self.object_sighted_handler(i, AFT, v)

                v = self.get_alternate_line_of_sight(270)
                
                if v.collision_with_circle(i.rect.centerx, \
                    i.rect.centery, i.radius) == True:

                    if i.graphics_state != DISINTEGRATING:
                        self.object_sighted_handler(i, STARBOARD, v)

    def object_sighted_handler(self, i, direction, v):

        if direction == FORE:
            laser_type = self.fore_laser
        elif direction == PORT:
            laser_type = self.port_laser
        elif direction == AFT:
            laser_type = self.aft_laser
        elif direction == STARBOARD:
            laser_type = self.starboard_laser

        if self.missile_attack_wait > 0:

            # wait, just fired missile, don't fire laser
            # or launch another missile yet
            self.missile_attack_wait -= 1
            self.ai_state = COLLISION_AVOIDANCE
            self.collision_avoidance_direction = random.choice([-1,1])
            self.collision_avoidance_timer = self.COLLISION_AVOIDANCE_DURATION

        else:  # attack!

            self.ai_state = FLY_STRAIGHT 

            # what attack method to use? 
            if laser_type != None:
                if random.randint(1,60) > 56:  
                    if self.equipment[MISSILE] > 0:
                        self.launch_missile = True
                        self.missile_target = i
                        self.missile_attack_wait = 170
                        self.equipment[MISSILE] -= 1
                    else:
                        if self.fire_laser(v.p2.x, v.p2.y, laser_type):
                            i.damage_handler(self.LASER_POWER, self)
                else:
                    if self.fire_laser(v.p2.x, v.p2.y, laser_type):
                        i.damage_handler(self.LASER_POWER, self)
            else:
                if random.randint(1,60) > 56:  
                    if self.equipment[MISSILE] > 0:
                        self.launch_missile = True
                        self.missile_target = i
                        self.missile_attack_wait = 170
                        self.equipment[MISSILE] -= 1

    def off_screen_pilot_AI(self, draw_group):

        p1 = game_engine.Point(self.global_x, self.global_y)
        p2 = game_engine.Point(self.LOS_vector.x*3 + self.global_x, \
                self.LOS_vector.y*3 + self.global_y)

        line_of_sight = game_engine.Vector(p1, p2)

        for i in draw_group:

            if i != self:

                if line_of_sight.collision_with_circle( i.global_x, \
                        i.global_y, i.radius*3) == True:
                    
                    if isinstance(i, Planet) == True or \
                       isinstance(i, Star) == True:

                        if self.ai_state != COLLISION_AVOIDANCE:
                        
                            self.ai_state = COLLISION_AVOIDANCE 
                            self.collision_avoidance_direction = random.choice([-1,1])
                            self.collision_avoidance_timer = self.COLLISION_AVOIDANCE_DURATION

    def update(self):

        if self.graphics_state != DISINTEGRATING:

            if self.ai_state == COLLISION_AVOIDANCE:
                self.collision_avoidance_timer -= 1
                if self.collision_avoidance_timer <= 0:
                    self.ai_state = FLY_STRAIGHT
                else:
                    self.turn_ship(self.collision_avoidance_direction)
                    self.throttle_ship(-1.1)
            
            if self.ai_state == ATTACK_AVOIDANCE:
                self.attack_avoidance_timer -= 1
                if self.attack_avoidance_timer <= 0:
                    self.ai_state = FLY_STRAIGHT
                else:
                    self.turn_ship(self.attack_avoidance_direction)
                    self.throttle_ship(1)

            else:

                self.throttle_ship(1)
            
        # call parent update()
        Ship.update(self)
        
        if self.graphics_state == SHIELDS_ENGAGED:
            self.graphics_state_countdown -= 1
            if self.graphics_state_countdown < 0:
                self.graphics_state_countdown = 0
                self.graphics_state = NORMAL
                self.image = self.object_image 
                self.rotation_image = self.object_image

        if self.state == define.DOCKING:
            if isinstance(self, Thargoid) == False:
                self.kill()
            else:
                self.damage_handler(99999)
                self.kill()

    def damage_handler(self, damage, obj_source=None):

        if self.ai_state != ATTACK_AVOIDANCE:

            self.ai_state = ATTACK_AVOIDANCE 
            self.attack_avoidance_direction = random.choice([-1,1])
            self.attack_avoidance_timer = self.ATTACK_AVOIDANCE_DURATION

        self.energy -= damage
        
        if self.energy > self.shield_threshold: 

            self.graphics_state = SHIELDS_ENGAGED
            self.graphics_state_countdown = SHIELDS_ENGAGED
            
            self.image = self.shield_image
            self.rect = self.image.get_rect()
            self.rect.centerx = self.global_x % define.FLIGHT_W 
            self.rect.centery = self.global_y % define.FLIGHT_H
            self.rotation_image = self.image

        else:

            Ship.damage_handler(self, 0, obj_source)

    def collision_detection(self, draw_group):
                
        hit_list = pygame.sprite.spritecollide(self, draw_group, False, \
                    pygame.sprite.collide_circle)

        for h in hit_list:

            if self == h or h.graphics_state == DISINTEGRATING:

                pass

            elif isinstance(h, Station) == True:
                 
                if self.state == define.FLYING:

                    self.state = define.DOCKING

            elif isinstance(h, Missile) == True:

                if self != h.ship: 

                    h.damage_handler(1000)  # missile explodes
                    self.damage_handler(h.mass, h)
                        
                    if isinstance(h.ship, PlayerShip) == True and \
                            self.graphics_state == DISINTEGRATING:
                        h.ship.pilot.increase_kill_count()
                        h.ship.add_bounty(self)
                        if isinstance(self, Police) == True or \
                                isinstance(self, Trader) == True or \
                                isinstance(self, BountyHunter) == True:
                            h.ship.pilot.increase_offense_count()

            elif h.graphics_state != DISINTEGRATING:

                self.damage_handler(h.mass, h)

                h.damage_handler(self.mass, self)

                if isinstance(h, PlayerShip) == True and \
                    self.graphics_state == DISINTEGRATING:
                    h.pilot.increase_kill_count()
                    h.add_bounty(self)
                    if isinstance(self, Police) == True or \
                            isinstance(self, Trader) == True or \
                            isinstance(self, BountyHunter) == True:
                        h.pilot.increase_offense_count()
  
class Trader(NonPlayerShip):

    def __init__(self, planet_data, ship_type):
        
        p = define.ship_image_pathname[ship_type] 
        image = pygame.image.load(p).convert()
        game_engine.swap_colors(image, define.WHITE, define.GRAY)
        image.set_colorkey(define.BLACK)

        NonPlayerShip.__init__(self, image, planet_data, ship_type)

        self.color = define.GRAY
        
        self.laser_sound = 'LASER_2'
       
    def object_sighted_handler(self, i, direction, v):

        if isinstance(i, Pirate) == True or \
           isinstance(i, Asteroid) == True or \
           isinstance(i, Missile) == True:

            NonPlayerShip.object_sighted_handler(self, i, direction, v)

        elif self.ai_state != COLLISION_AVOIDANCE:
        
            self.ai_state = COLLISION_AVOIDANCE 
            self.collision_avoidance_direction = random.choice([-1,1])
            self.collision_avoidance_timer = self.COLLISION_AVOIDANCE_DURATION

class Pirate(NonPlayerShip):

    def __init__(self, planet_data, ship_type):
        
        p = define.ship_image_pathname[ship_type] 
        image = pygame.image.load(p).convert()
        game_engine.swap_colors(image, define.WHITE, define.RED)
        image.set_colorkey(define.BLACK)

        NonPlayerShip.__init__(self, image, planet_data, ship_type)

        self.color = define.RED

        self.bounty = (random.random() * 100.00)
        
        self.laser_sound = 'LASER_3'
        
    def object_sighted_handler(self, i, direction, v):

        if isinstance(i, Ship) == True or \
           isinstance(i, Asteroid) == True or \
           isinstance(i, Missile) == True:

            NonPlayerShip.object_sighted_handler(self, i, direction, v) 

        elif self.ai_state != COLLISION_AVOIDANCE:
        
            self.ai_state = COLLISION_AVOIDANCE 
            self.collision_avoidance_direction = random.choice([-1,1])
            self.collision_avoidance_timer = self.COLLISION_AVOIDANCE_DURATION

class Police(NonPlayerShip):

    def __init__(self, planet_data, ship_type):

        p = define.ship_image_pathname[ship_type] 
        image = pygame.image.load(p).convert()
        game_engine.swap_colors(image, define.WHITE, define.BLUE)
        image.set_colorkey(define.BLACK)

        NonPlayerShip.__init__(self, image, planet_data, ship_type)

        self.color = define.BLUE
        
        self.ENERGY_RECHARGE_RATE = 0.0027 
        self.MAX_ENERGY = 400
        self.energy = self.MAX_ENERGY
        
        self.laser_sound = 'LASER_4'

    def object_sighted_handler(self, i, direction, v):

        if isinstance(i, Pirate) == True or \
           isinstance(i, Asteroid) == True or \
           isinstance(i, Missile) == True or \
               (isinstance(i, PlayerShip) == True and \
                i.pilot.legal_status == define.FUGITIVE):

            NonPlayerShip.object_sighted_handler(self, i, direction, v) 

        elif self.ai_state != COLLISION_AVOIDANCE:
        
            self.ai_state = COLLISION_AVOIDANCE 
            self.collision_avoidance_direction = random.choice([-1,1])
            self.collision_avoidance_timer = self.COLLISION_AVOIDANCE_DURATION

class BountyHunter(NonPlayerShip):

    def __init__(self, planet_data, ship_type):

        p = define.ship_image_pathname[ship_type] 
        image = pygame.image.load(p).convert()
        game_engine.swap_colors(image, define.WHITE, define.PURPLE)
        image.set_colorkey(define.BLACK)

        NonPlayerShip.__init__(self, image, planet_data, ship_type)

        self.color = define.PURPLE

        self.laser_sound = 'LASER_5'

    def object_sighted_handler(self, i, direction, v):

        if isinstance(i, Pirate) == True or \
           isinstance(i, Asteroid) == True or \
           isinstance(i, Missile) == True or \
               (isinstance(i, PlayerShip) == True and \
                i.pilot.legal_status == define.FUGITIVE):

            NonPlayerShip.object_sighted_handler(self, i, direction, v)
        
        elif (isinstance(i, PlayerShip) == True and \
                i.pilot.legal_status == define.OFFENDER):

            # bounty hunters will fire lasers at OFFENDERS, but not launch
            # missiles - kind of a "warning shot across the bow"

            self.ai_state = FLY_STRAIGHT 

            if direction == FORE:
                laser_type = self.fore_laser
            elif direction == PORT:
                laser_type = self.port_laser
            elif direction == AFT:
                laser_type = self.aft_laser
            elif direction == STARBOARD:
                laser_type = self.starboard_laser

            if self.fire_laser(v.p2.x, v.p2.y, laser_type):
                i.damage_handler(self.LASER_POWER, self)

        elif self.ai_state != COLLISION_AVOIDANCE:
        
            self.ai_state = COLLISION_AVOIDANCE 
            self.collision_avoidance_direction = random.choice([-1,1])
            self.collision_avoidance_timer = self.COLLISION_AVOIDANCE_DURATION

class Thargoid(NonPlayerShip):

    def __init__(self, planet_data, ship_type):
        
        p = define.ship_image_pathname[ship_type] 
        image = pygame.image.load(p).convert()
        game_engine.swap_colors(image, define.WHITE, define.GREEN)
        image.set_colorkey(define.BLACK)

        self.planet_data = planet_data

        NonPlayerShip.__init__(self, image, planet_data, ship_type)

        self.color = define.GREEN

        self.bounty = (random.random() * 525.00)
        
        self.laser_sound = 'LASER_6'

        self.TURN_MIN = 150
        self.TURN_MAX = 800
        self.random_turn_countdown = random.randint(self.TURN_MIN, self.TURN_MAX)
        self.turn_direction = random.choice([-1,1])
        self.turn_duration = random.randint(self.TURN_MIN, self.TURN_MAX)
        
        self.ENERGY_RECHARGE_RATE = 0.0028 
        self.MAX_ENERGY = 600
        self.energy = self.MAX_ENERGY
        
        self.add_laser(FORE, MILITARY_LASER)
        self.add_laser(AFT, MILITARY_LASER)
        self.add_laser(PORT, MILITARY_LASER)
        self.add_laser(STARBOARD, MILITARY_LASER)
        self.equipment[MISSILE] = 4

        self.name = 'THARGOID'

    def update(self):

        if self.graphics_state != DISINTEGRATING:

            self.random_turn_countdown -= 1

            if self.random_turn_countdown <= 0:

                # initiate turn
                self.turn_direction = random.choice([-1,1])
                self.random_turn_countdown = random.randint(self.TURN_MIN, self.TURN_MAX)
                self.random_turn_duration = random.randint(self.TURN_MIN, self.TURN_MAX)

            elif self.random_turn_countdown < self.TURN_MIN:

                self.turn_ship(self.turn_direction)
        
        NonPlayerShip.update(self)

    def damage_handler(self, damage, obj_source=None):

        NonPlayerShip.damage_handler(self, damage, obj_source)



class HudMessage():

    def __init__(self, string, y_loc, color, delay):

        self.string   = string 
        self.location = y_loc
        self.color    = color
        self.timer    = 120
 
        if delay == True:
            self.delay = 90
        else:
            self.delay = self.timer - 2 # almost zero delay 

    def update(self):

        self.timer -= 1


class PlayerShip(Ship):

    def __init__(self, planet_database, planet_number=7):

        ship_type = define.COBRA_MK_III

        p = define.ship_image_pathname[ship_type] 
        image = pygame.image.load(p).convert()
        game_engine.swap_colors(image, define.WHITE, define.YELLOW)
        image.set_colorkey(define.BLACK)

        self.planet_number    = planet_number 
        self.planet_data      = planet_database.get_planet_by_index(self.planet_number) 
        self.planet_database  = planet_database
        self.target_system    = self.planet_data 

        x = self.planet_data.station_x
        y = self.planet_data.station_y
        
        # call parent constructor
        Ship.__init__(self, image, x, y, self.planet_data, ship_type)

        self.add_laser(AFT, PULSE_LASER)
        self.add_laser(PORT, PULSE_LASER)
        self.add_laser(STARBOARD, PULSE_LASER)
        
        self.color = define.YELLOW

        self.energy = 400 
        self.ENERGY_RECHARGE_RATE = 0.4
        self.MAX_ENERGY = 400 

        self.MAX_FUEL = 20.0 
        self.MIN_FUEL = 0.0
        self.fuel = self.MAX_FUEL
        self.FUEL_DRAIN = 0.00057
        
        self.THRUST_WARNING = self.MAX_THRUST * 0.70

        self.pilot = None
        self.message_queue = []  
        self.equipment[FUEL] = self.fuel 
        self.cargo = CargoContainer(self)
        self.FORE_SHIELD_MAX = 80 
        self.AFT_SHIELD_MAX = 80 
        self.fore_shield = self.FORE_SHIELD_MAX 
        self.aft_shield = self.AFT_SHIELD_MAX 

        # image of ship with fore shields active
        self.fore_shield_image = pygame.image.load('images/fore_shield.png').convert()
        self.fore_shield_rect = self.fore_shield_image.get_rect()
        temp_rect = self.object_image.get_rect()
        blit_x = int(self.fore_shield_rect.width/2) - int(temp_rect.width/2)
        blit_y = int(self.fore_shield_rect.height/2) - int(temp_rect.height/2)
        self.fore_shield_image.blit(self.object_image, (blit_x,blit_y))
        self.fore_shield_image.set_colorkey(define.BLACK)
        
        # image of ship with aft shields active
        self.aft_shield_image = pygame.image.load('images/aft_shield.png').convert()
        self.aft_shield_rect = self.aft_shield_image.get_rect()
        temp_rect = self.object_image.get_rect()
        blit_x = int(self.aft_shield_rect.width/2) - int(temp_rect.width/2)
        blit_y = int(self.aft_shield_rect.height/2) - int(temp_rect.height/2)
        self.aft_shield_image.blit(self.object_image, (blit_x,blit_y))
        self.aft_shield_image.set_colorkey(define.BLACK)

        self.auto_targeting_on = False
        self.auto_target = None

        self.flagged_for_illegal_trading = False

        self.flagged_for_increased_police = False
        
        self.JUMP_RESET = 150
        self.jump_countdown = self.JUMP_RESET
        self.jump_initiated = False

        self.eject_sequence_on = False
        self.EJECT_RESET = 300
        self.eject_countdown = self.EJECT_RESET

        self.flagged_for_cleared_record = False

        self.escape_pod = None
        
        self.MIN_THRUST = 0.0 

        self.info_display_countdown = 0

        self.hud_update_needed = False # update HUD info when legal status changes

    def dock(self):

        self.auto_targeting_on = False
        self.auto_target = None
        self.jump_countdown = self.JUMP_RESET
        self.jump_initiated = False
        self.eject_countdown = self.EJECT_RESET

        Ship.dock(self)

        self.state = define.DOCKED

        flatland_engine.sound.stop_music()

    def update(self):
        
        if self.state != define.DOCKED:

            if self.info_display_countdown >= 0:
                self.info_display_countdown -= 1
                
            # call parent update()
            Ship.update(self)
            self.recalculate_displacement()
            self.recalculate_line_of_sight()

            # drain fuel due to thrusters on
            if self.thrust > 0:
                if self.fuel > 0:
                    self.drain_fuel(self.FUEL_DRAIN * self.thrust)
                else:
                    self.thrust -= 1 

            # escape capsule eject sequence
            if self.eject_sequence_on == True:
                self.eject_countdown -= 1
                if self.eject_countdown == 0:
                    self.add_hud_message('', 19, define.BLACK, False)
                    self.add_hud_message('', 21, define.BLACK, False)
                    self.add_hud_message('ESCAPE CAPSULE LAUNCHED', 19, \
                            define.YELLOW, False)
                    self.state = define.EJECTING_CAPSULE

            # update all messages in the queue
            for i in self.message_queue:
                i.update()

            # check docking speed
            if self.state == define.FLYING:
                a = self.global_x - self.planet_data.station_x
                b = self.global_y - self.planet_data.station_y
                c = int(math.sqrt( (a*a) + (b*b) ))
                if c < 400 and c > 395:
                    if self.thrust > self.THRUST_WARNING:
                        if self.equipment[DOCKING_COMPUTER] == 0: 
                                self.add_hud_message('WARNING: DOCKING SPEED EXCEEDED', \
                                                12, define.CYAN, False)
                        else: 
                                self.add_hud_message('DOCKING COMPUTER INITIALIZED', \
                                                12, define.CYAN, False)
               
            # must have a weapon firing delay
            if self.missile_attack_wait > 0:
                self.missile_attack_wait -= 1
            if self.ecm_attack_wait > 0:
                self.ecm_attack_wait -= 1
            if self.bomb_attack_wait > 0:
                self.bomb_attack_wait -= 1
           
            # how long to hold the shield state
            if self.graphics_state == SHIELDS_ENGAGED:
                self.graphics_state_countdown -= 1
                if self.graphics_state_countdown < 0:
                    self.graphics_state_countdown = 0
                    self.graphics_state = NORMAL
                    self.image = self.object_image 
                    self.rotation_image = self.object_image
        
            # energy recharge
            if self.fuel > 0:

                if self.fore_shield < self.FORE_SHIELD_MAX:
                    self.fore_shield += self.ENERGY_RECHARGE_RATE
                    self.drain_fuel(self.FUEL_DRAIN)
                    if self.fore_shield > self.FORE_SHIELD_MAX:
                        self.fore_shield = self.FORE_SHIELD_MAX

                if self.aft_shield < self.AFT_SHIELD_MAX:
                    self.aft_shield += self.ENERGY_RECHARGE_RATE
                    self.drain_fuel(self.FUEL_DRAIN)
                    if self.aft_shield > self.AFT_SHIELD_MAX:
                        self.aft_shield = self.AFT_SHIELD_MAX

                if self.energy < self.MAX_ENERGY and \
                        (self.fore_shield == self.FORE_SHIELD_MAX and \
                        self.aft_shield == self.AFT_SHIELD_MAX):
                    self.energy += self.ENERGY_RECHARGE_RATE
                    self.drain_fuel(self.FUEL_DRAIN)
                    if self.energy > self.MAX_ENERGY:
                        self.energy = self.MAX_ENERGY

            else:

                if self.fore_shield > 0: 
                    self.fore_shield -= self.ENERGY_RECHARGE_RATE
                if self.aft_shield > 0:
                    self.aft_shield -= self.ENERGY_RECHARGE_RATE
                if self.energy > 0 and \
                        (self.fore_shield <=0 and self.aft_shield <=0):
                    self.energy -= self.ENERGY_RECHARGE_RATE

            # launching from station
            if self.state == define.CLEARING_STATION:
                dx = self.global_x - self.planet_data.station_x
                dy = self.global_y - self.planet_data.station_y
                distance = math.sqrt( dx*dx + dy*dy )
                if distance > 170:
                    self.state = define.FLYING

            # hyperjump warm-up
            if self.jump_initiated == True:
                self.jump_countdown -= 1

        else:
            
            if self.fore_shield < self.FORE_SHIELD_MAX:
                self.fore_shield += self.ENERGY_RECHARGE_RATE
                if self.fore_shield > self.FORE_SHIELD_MAX:
                    self.fore_shield = self.FORE_SHIELD_MAX

            if self.aft_shield < self.AFT_SHIELD_MAX:
                self.aft_shield += self.ENERGY_RECHARGE_RATE
                if self.aft_shield > self.AFT_SHIELD_MAX:
                    self.aft_shield = self.AFT_SHIELD_MAX

            if self.energy < self.MAX_ENERGY and \
                    (self.fore_shield == self.FORE_SHIELD_MAX and \
                    self.aft_shield == self.AFT_SHIELD_MAX):
                self.energy += self.ENERGY_RECHARGE_RATE
                if self.energy > self.MAX_ENERGY:
                    self.energy = self.MAX_ENERGY

    def start_jump(self):

        self.jump_initiated = True
        self.jump_countdown = self.JUMP_RESET

    def add_hud_message(self, string, location, color, delay=True):

        for i in self.message_queue:
            if i.location == location:
                #i.timer = 0
                self.message_queue.remove(i)

        self.message_queue.append(HudMessage('       ' + \
            string + '       ', location, color, delay))

        pick = random.choice( \
                ['BEEP_2', 'BEEP_3', 'BEEP_4', \
                'BEEP_5', 'BEEP_6', 'BEEP_7', 'BEEP_8'] )
        flatland_engine.sound.play_sound_effect(pick)

    def install_pilot(self, p):

        self.pilot = p

    def drain_fuel(self, amount):

        if self.state != define.DOCKED:
                
            start_level = self.fuel

            self.fuel -= amount 

            if self.fuel <= 0:
                self.add_hud_message('OUT OF FUEL', 18, define.CYAN, \
                        False)
                self.fuel = 0.0
                self.throttle_ship(-1)

            end_level = self.fuel

            return (start_level - end_level)

        else:

            start_level = self.fuel

            self.fuel -= amount 

            if self.fuel <= 0:
                self.fuel = 0.0

            end_level = self.fuel

            return (start_level - end_level)

    def install_fuel(self, amount):

        start_level = self.fuel

        self.fuel += amount 

        if self.fuel > self.MAX_FUEL:
            self.fuel = self.MAX_FUEL 

        end_level = self.fuel

        return (end_level - start_level)

    def add_bounty(self, obj):

        self.pilot.cash += obj.bounty

        up = str( round(obj.bounty, 2) )
        total = round(self.pilot.cash, 2)
        t = tga_generator.int_with_commas(total)

        if obj.bounty != 0:

            if isinstance(obj, Ship):
                c = obj.name
                self.add_hud_message(c, 29, define.BLUE)

            m = '+' + up + ' credits (' + t + ' total)'
            self.add_hud_message(m.upper(), 31, define.CYAN)
            pick = random.choice( \
                    ['CASH_1', 'CASH_2'] )

    def add_direct_bounty(self, cash):

        self.pilot.cash += cash 

        up = str( round(cash, 2) )
        total = round(self.pilot.cash, 2)
        t = tga_generator.int_with_commas(total)

        m = '+' + up + ' credits (' + t + ' total)'
        self.add_hud_message(m.upper(), 31, define.CYAN)
        pick = random.choice( \
                ['CASH_1', 'CASH_2'] )


    def change_sectors(self, dx, dy):

        self.sector_x = (self.sector_x + dx) % define.GRID_SIZE
        self.sector_y = (self.sector_y + dy) % define.GRID_SIZE

    def change_target(self, planet_data):

        self.target_system = planet_data

    def jump_systems(self):

        if (self.target_system != self.planet_data) and \
                (self.graphics_state == NORMAL):

            d = self.jump_distance() 

            if d > self.fuel:

                self.add_hud_message('TARGET SYSTEM OUT OF RANGE', \
                        17, define.CYAN, False)

                return False

            else:

                self.drain_fuel(d/3)

                min_x = define.FLIGHT_W * 3
                max_x = define.FLIGHT_W * 5
                self.global_x = random.randint(min_x, max_x)

                min_y = define.FLIGHT_H * 3
                max_y = define.FLIGHT_H * 5
                self.global_y = random.randint(min_y, max_y)

                self.planet_data      = self.target_system

                self.planet_number    = self.planet_data.number

                return True

        else:

            return False

    def auto_targeting(self, draw_group):

        self.recalculate_line_of_sight()

        # p1 = game_engine.Point(self.rect.centerx, self.rect.centery)
        # p2 = game_engine.Point(self.LOS_vector.x, self.LOS_vector.y)

        # line_of_sight = game_engine.Vector(p1, p2)

        for i in draw_group:

            if i != self:
                    
                if self.LOS_vector.collision_with_circle( i.rect.centerx, \
                            i.rect.centery, i.radius) == True:

                    if i.graphics_state != DISINTEGRATING:

                        if i != self.auto_target and \
                                isinstance(i, Station) == False and \
                                isinstance(i, Star) == False and \
                                isinstance(i, Planet) == False:

                            if self.auto_target != None:
                                self.auto_target.remove_targeting_square()
                                self.auto_target.targeted = False

                            self.auto_target = i
                            i.add_targeting_square()
                            i.targeted = True
                            self.add_hud_message('* MISSILE TARGET LOCKED ON *', 26, \
                                    define.GREEN, False)
                            self.add_hud_message('(Press \'M\' to fire Missile)', 28, \
                                    define.CYAN, False)

                            self.auto_targeting_on = False


    def player_uses_ECM(self, draw_group):

        # Electronic Counter Measures will destroy all on-screen missiles,
        # including player-owned
        
        if self.ecm_attack_wait == 0: 

            if self.equipment[ECM_SYSTEM] > 0:
                                            
                for i in draw_group:
                    if isinstance(i, Missile):
                        i.damage_handler(9999)
                        self.pilot.increase_kill_count()
                        self.add_bounty(i)
                        if isinstance(i, Police) == True or \
                                isinstance(i, Trader) == True or \
                                isinstance(i, BountyHunter) == True:
                            self.pilot.increase_offense_count()

                pick = random.choice(['ECM_1','ECM_2','ECM_3'])
                flatland_engine.sound.play_sound_effect(pick)

                self.add_hud_message(\
                    'ECM ACTIVATED', 16, define.CYAN, False) 
                
                self.ecm_activated = True 
        
                self.damage_handler(50, None)   # ECM uses a lot of energy
                self.equipment[ECM_SYSTEM] -= 1 

                self.ecm_attack_wait = 60
            
            else:

                self.add_hud_message(\
                    'ELECTRONIC COUNTER MEASURES NOT INSTALLED', 18, define.BLUE, False)


    def player_uses_bomb(self, draw_group):

        if self.bomb_attack_wait == 0: 

            if self.equipment[ENERGY_BOMB] > 0:
                                            
                for i in draw_group:
                    if i != self:
                        i.damage_handler(9999)
                        self.pilot.increase_kill_count()
                        self.add_bounty(i)
                        if isinstance(i, Police) == True or \
                                isinstance(i, Trader) == True or \
                                isinstance(i, BountyHunter) == True:
                            self.pilot.increase_offense_count()
                
                pick = random.choice(['BOMB_1','BOMB_2'])
                flatland_engine.sound.play_sound_effect(pick)

                self.add_hud_message(\
                    'ENERGY BOMB DETONATED', 16, define.CYAN, False)

                self.bomb_activated = True
        
                self.damage_handler(50, None)   # bomb uses a lot of energy
                self.equipment[ENERGY_BOMB] -= 1

                self.bomb_attack_wait = 60
            
            else:

                self.add_hud_message(\
                    'ENERGY BOMB NOT INSTALLED', 18, define.BLUE, False)

    def player_fires_laser(self, draw_group, direction):
        
        if direction == FORE:
            laser_type = self.fore_laser
        elif direction == PORT:
            laser_type = self.port_laser
        elif direction == AFT:
            laser_type = self.aft_laser
        elif direction == STARBOARD:
            laser_type = self.starboard_laser

        if self.fuel > 0.0:

            target_found = False
            
            if direction == FORE:

                v = self.LOS_vector 

            elif direction == PORT:

                v = self.get_alternate_line_of_sight(90) 
            
            elif direction == AFT:

                v = self.get_alternate_line_of_sight(180) 
            
            elif direction == STARBOARD:

                v = self.get_alternate_line_of_sight(270) 

            for i in draw_group:

                if i != self:

                    if v.collision_with_circle( i.rect.centerx, \
                            i.rect.centery, i.radius) == True and \
                        i.graphics_state != DISINTEGRATING:

                        target_found = True

                        if isinstance(i, Planet) == True or \
                                isinstance(i, Star) == True or \
                                isinstance(i, Station) == True:

                            if isinstance(i, Station) == True:
                                self.fire_laser(i.rect.centerx, i.rect.centery, laser_type)
                            else:
                                self.fire_laser(v.p2.x, v.p2.y, laser_type)
                            
                        elif self.fire_laser(v.p2.x, v.p2.y, \
                                laser_type) == True:
                            i.damage_handler(self.LASER_POWER, self)

                        if isinstance(i, Police) == True or \
                                isinstance(i, Station) == True:
                            self.pilot.increase_offense_count()

                        if i.graphics_state == DISINTEGRATING:
                            self.pilot.increase_kill_count()
                            self.add_bounty(i)
                            if isinstance(i, Police) == True or \
                                    isinstance(i, Trader) == True or \
                                    isinstance(i, BountyHunter) == True:
                                self.pilot.increase_offense_count()
           
            if target_found == False:

                self.fire_laser(v.p2.x, v.p2.y, laser_type)

            self.drain_fuel(self.FUEL_DRAIN)

        else:

            self.add_hud_message('OUT OF FUEL', 18, define.CYAN, False)



    def player_fires_missile(self, draw_group):
                                    
        if self.missile_attack_wait == 0: 

            if self.equipment[MISSILE] > 0:
                                            
                if self.auto_target != None:

                    self.missile_target = self.auto_target
                    self.missile_target.targeted = True
                    self.launch_missile = True
                    self.equipment[MISSILE] -= 1
                    self.missile_attack_wait = 30

                else:
                    
                    self.add_hud_message('    NO TARGET SELECTED (Press T)    ', \
                            18, define.BLUE, False)

            else:

                self.add_hud_message('MISSILE SILOS EMPTY', \
                        18, define.BLUE, False)
    
    def jump_distance(self):

        p1 = game_engine.Point(self.planet_data.galactic_x, \
                self.planet_data.galactic_y)
        p2 = game_engine.Point(self.target_system.galactic_x, \
                self.target_system.galactic_y)

        d = game_engine.Vector(p1, p2)

        distance = d.magnitude() / 2.714285

        return distance

    def angle_of_attack(self, obj):

        # return the angle that is created from a line drawn from the ship to
        # the object. Note that the orientation of either ship or object does
        # not matter.

        dx = obj.rect.centerx - self.rect.centerx
        dy = obj.rect.centery - self.rect.centery

        if dx != 0:
            ratio = float( -dy / dx )
        else:
            ratio = 0

        theta = math.degrees( math.atan( ratio ) )

        if dx < 0:
            theta += 180
        if theta < 0:
            theta += 360

        return theta

        
    def damage_handler(self, damage, obj_source=None):

        # first: need to decide if damage hits the fore or aft shield 
        #        (this is needed regardless of if there is any charge left
        #         in the shields themselves).

        if obj_source == None:
            Object.damage_handler(self, damage)
            return

        # find dx, dy to obj (with ship at origin) 
        dx = obj_source.rect.centerx - self.rect.centerx
        dy = -(obj_source.rect.centery - self.rect.centery)

        # now find the angle to the object
        if dx != 0:
            collision_angle = math.degrees(math.atan(dy/dx))
        else:
            collision_angle = 0
      
        # set collision_angle to match orientation values (0-360)
        if dx < 0:
            collision_angle += 180
        elif dy < 0:
            collision_angle += 360
 
        # now we can compare the two (ship orientation vs. collision angle)
        # If they are less than 90 degrees, this is fore-shield collision

        if collision_angle > self.orientation:
            z = collision_angle - self.orientation
        else:
            z = self.orientation - collision_angle
        z = math.fabs(z)

        if z < 90:

            # attempt to damage the fore shield
            if self.fore_shield > 0:

                self.fore_shield -= damage 

                self.graphics_state = SHIELDS_ENGAGED
                self.graphics_state_countdown = SHIELDS_ENGAGED
                
                self.image = self.fore_shield_image
                self.rect = self.image.get_rect()
                self.rect.centerx = self.global_x % define.FLIGHT_W 
                self.rect.centery = self.global_y % define.FLIGHT_H
                self.rotation_image = self.image
                self.prerender_rotation()

                if self.fore_shield < 0:

                    self.energy += self.fore_shield  #fore_shield negative here
                    self.fore_shield = 0

                    Object.damage_handler(self, 0, obj_source)

            else:
                
                Object.damage_handler(self, damage, obj_source)

        else:

            # attempt to damage the aft shield
            if self.aft_shield > 0:

                self.aft_shield -= damage 
                
                self.graphics_state = SHIELDS_ENGAGED
                self.graphics_state_countdown = SHIELDS_ENGAGED
                
                self.image = self.aft_shield_image
                self.rect = self.image.get_rect()
                self.rect.centerx = self.global_x % define.FLIGHT_W 
                self.rect.centery = self.global_y % define.FLIGHT_H
                self.rotation_image = self.image
                self.prerender_rotation()

                if self.aft_shield < 0:

                    self.energy += self.aft_shield
                    self.aft_shield = 0
                
                    Object.damage_handler(self, 0, obj_source)
                    
            else:
                
                Object.damage_handler(self, damage, obj_source)


    def collision_detection(self, draw_group):

        if self.graphics_state == NORMAL:

            hit_list = pygame.sprite.spritecollide(self, draw_group, False, \
                    pygame.sprite.collide_circle)

            for h in hit_list:

                if h == self or h.graphics_state == DISINTEGRATING:

                    pass

                elif isinstance(h, CargoContainer) == True:

                    if self.equipment[FUEL_SCOOP] > 0:

                        item_index = 0
                        item_count = 0

                        pick = random.choice(['COLLECT_1','COLLECT_2'])
                        flatland_engine.sound.play_sound_effect(pick)

                        for j in range(17):

                            if h.hold[j] > 0:

                                item_index = j
                                item_count = h.hold[j]

                                while h.hold[j] > 0:   # transfer cargo

                                    self.cargo.add_item(j)
                                    h.hold[j] -= 1

                        h.kill()

                        s = 'COLLECTED CARGO CONTAINER (' + \
                                str(item_count) + ' OF ' + \
                                COMMODITY_NAME[item_index].strip() + ')' 

                        self.add_hud_message(s, 10, define.CYAN, False)

                    else:

                        s = 'MUST HAVE FUEL SCOOP TO COLLECT CARGO CONTAINERS'
                        self.add_hud_message(s, 10, define.YELLOW, False)

                        self.damage_handler(h.mass, h)
                        h.damage_handler(self.mass)


                elif isinstance(h, Shard) == True:

                    if self.equipment[FUEL_SCOOP] > 0:

                        pick = random.choice(['COLLECT_1','COLLECT_2'])
                        flatland_engine.sound.play_sound_effect(pick)

                        h.bounty = (random.random() * 300.00) + 50
                        self.add_bounty(h)
                        h.kill()

                        s = 'COLLECTED ASTEROID SHARD'
                        self.add_hud_message(s, 10, define.CYAN, False)

                    else:

                        s = 'MUST HAVE FUEL SCOOP TO COLLECT ASTEROID SHARDS'
                        self.add_hud_message(s, 10, define.YELLOW, False)

                        self.damage_handler(h.mass, h)
                        h.damage_handler(self.mass)



                elif isinstance(h, Station) == True:
             
                    if self.thrust > self.THRUST_WARNING and \
                            self.state != define.CLEARING_STATION and \
                            self.equipment[DOCKING_COMPUTER] == 0:

                        self.add_hud_message('DOCKING SPEED EXCEEDED', \
                                13, define.CYAN, False)

                        self.damage_handler(9999, h)   # going too fast to dock!

                    elif self.planet_data.num_thargoids > 0:

                        self.add_hud_message('STATION UNDER THARGOID CONTROL', \
                                13, define.GREEN, False)

                    else:

                        if self.state == define.FLYING:
                            self.state = define.DOCKING

                elif isinstance(h, Missile) == True:

                    if self != h.ship: 

                        h.damage_handler(1000)  # missile explodes
                        
                        self.damage_handler(h.mass, h)
                    
                        if isinstance(h.ship, PlayerShip) == True and \
                                self.graphics_state == DISINTEGRATING:
                            h.ship.pilot.increase_kill_count()
                            h.ship.add_bounty(self)
                            if isinstance(self, Police) == True or \
                                    isinstance(self, Trader) == True or \
                                    isinstance(self, BountyHunter) == True:
                                h.ship.pilot.increase_offense_count()
                    
                elif isinstance(h, EscapeCapsule) == True:

                    pass

                else:

                    self.damage_handler(h.mass, h)

                    h.damage_handler(self.mass, self)

                    if h.graphics_state == DISINTEGRATING:

                        self.pilot.increase_kill_count()
                        self.add_bounty(h)
                        if isinstance(h, Police) == True or \
                                isinstance(h, Trader) == True or \
                                isinstance(h, BountyHunter) == True:
                            self.pilot.increase_offense_count()



class ObjectController():

    # This object will be created upon each entry to a new system

    def __init__(self, surface_controller, player_ship, planet_database):

        self.planet_data        = player_ship.planet_data
        self.surface_controller = surface_controller
        self.planet_database    = planet_database

        self.draw_group         = pygame.sprite.Group()
        self.all_objects_group  = pygame.sprite.Group()
        self.flight_group       = pygame.sprite.Group() # for better AI

        # sprites
        self.planet_object      = Planet(self.planet_data)  
        self.star_object        = Star(self.planet_data)    
        self.station_object     = Station(self.planet_data)
        self.player_ship        = player_ship 
        self.escape_capsule     = None

        self.hud = hud.HudPanel(self.player_ship)
        
        self.populate_all_objects_group()

        self.laser_drawing_buffer = []

        self.docking_sequence = 0

        self.game_over = False

        self.reward_given = False

    def populate_all_objects_group(self):

        self.all_objects_group.empty()
        self.flight_group.empty()

        if self.planet_data.num_thargoids > 0:
        
            self.all_objects_group  = pygame.sprite.Group()
            self.hud = hud.HudPanel(self.player_ship)
            
            for i in range(self.planet_data.num_thargoids):
                temp = Thargoid(self.planet_data, define.THARGOID)
                self.all_objects_group.add( temp )
                self.hud.add_blip( temp )
        
        else:
        
            # reference: government type-values
            #     'Anarchy':0
            #     'Feudal':1
            #     'Multi-Government':2
            #     'Dictatorship':3
            #     'Communist':4
            #     'Confederacy':5
            #     'Democracy':6
            #     'Corporate State':7 

            self.num_asteroids = (8 - self.planet_data.government) * 2 
            self.num_hunters = (9 - self.planet_data.government) 
            self.num_pirates = int((7 - self.planet_data.government) * 3.5)
            self.num_police = int(self.planet_data.government * 1.5)
            self.num_traders = self.planet_data.government * 2 
            
            # increase police presence if player is a fugitive and flying in
            # civilized space
            if self.planet_data.government > 1:
                if self.player_ship.pilot != None:
                    if self.player_ship.pilot.legal_status == define.FUGITIVE:
                        self.num_police *= 3
                        self.num_hunters *= 3
                        self.player_ship.flagged_for_increased_police = True
                    else:
                        self.player_ship.flagged_for_increased_police = False 

            for i in range(self.num_asteroids):
                temp = Asteroid()
                self.all_objects_group.add( temp )
                self.hud.add_blip( temp )
            
            for i in range(self.num_hunters):
                h = [define.ADDER, \
                     define.KRAIT, \
                     define.KRAIT, \
                     define.MAMBA, \
                     define.KRAIT, \
                     define.VIPER, \
                     define.FER_DE_LANCE, \
                     define.FER_DE_LANCE, \
                     define.FER_DE_LANCE, \
                     define.SIDEWINDER, \
                     define.SIDEWINDER, \
                     define.BOA_CLASS_CRUISER]
                hh = random.choice(h)
                temp = BountyHunter(self.planet_data, hh)
                temp.ship_type = hh
                temp.name = define.ship_name[hh].upper()
                self.all_objects_group.add( temp )
                self.hud.add_blip( temp )
            
            for i in range(self.num_pirates):
                p = [define.ADDER, \
                     define.ASP_MK_II, \
                     define.ASP_MK_II, \
                     define.ASP_MK_II, \
                     define.FER_DE_LANCE, \
                     define.FER_DE_LANCE, \
                     define.MAMBA, \
                     define.MAMBA, \
                     define.COBRA_MK_I, \
                     define.COBRA_MK_I, \
                     define.SIDEWINDER, \
                     define.SIDEWINDER, \
                     define.GECKO, \
                     define.GECKO, \
                     define.KRAIT]
                pp = random.choice(p)
                temp = Pirate(self.planet_data, pp)
                temp.ship_type = pp 
                temp.name = define.ship_name[pp].upper()
                self.all_objects_group.add( temp )
                self.hud.add_blip( temp )

            for i in range(self.num_police):
                p = [define.VIPER, \
                    define.VIPER, \
                    define.VIPER, \
                    define.VIPER, \
                    define.VIPER, \
                    define.VIPER, \
                    define.VIPER, \
                     define.MAMBA, \
                     define.COBRA_MK_III]
                pp = random.choice(p)
                temp = Police(self.planet_data, pp)
                temp.ship_type = pp 
                temp.name = define.ship_name[pp].upper()
                self.all_objects_group.add( temp )
                self.all_objects_group.add( temp )
                self.hud.add_blip( temp )
            
            for i in range(self.num_traders):
                t = [define.COBRA_MK_I, \
                    define.COBRA_MK_I, \
                    define.COBRA_MK_I, \
                    define.COBRA_MK_I, \
                    define.BOA_CLASS_CRUISER, \
                    define.COBRA_MK_I, \
                    define.COBRA_MK_I, \
                    define.MORAY_STAR_BOAT, \
                    define.MORAY_STAR_BOAT, \
                    define.ANACONDA, \
                     define.SIDEWINDER, \
                     define.SIDEWINDER, \
                     define.MAMBA, \
                     define.MAMBA, \
                    define.ANACONDA, \
                    define.GECKO, \
                    define.GECKO, \
                     define.COBRA_MK_III]
                tt = random.choice(t)
                temp = Trader(self.planet_data, tt)
                temp.ship_type = tt 
                temp.name = define.ship_name[tt].upper()
                self.all_objects_group.add( temp )
                self.all_objects_group.add( temp )
                self.hud.add_blip( temp )

        self.all_objects_group.add(self.player_ship)
        self.all_objects_group.add(self.station_object)

        self.player_ship.color = define.YELLOW
        self.hud.add_blip(self.player_ship, 5)

        self.hud.add_blip(self.star_object, 17)
        self.hud.add_blip(self.station_object, 10)
        self.hud.add_blip(self.planet_object, 21)

        # populate flight_group only with ships (except player's ship)
        for i in self.all_objects_group:
            if isinstance(i, NonPlayerShip) == True:
                self.flight_group.add(i)

        # reset docking sequence for next time
        self.docking_sequence = 0

        self.reward_given = False

    def build_draw_group(self):
        
        if self.player_ship.state != define.ABANDONED:
            
            self.draw_group.empty()

            for i in self.all_objects_group:

                if isinstance(i, Asteroid) == True and \
                        i.converted_to_shard == True:

                    n = Shard(i.global_x, i.global_y)

                    i.kill()

                    self.all_objects_group.add(n)
                    self.draw_group.add(n)
                    self.hud.add_blip(n)

                if isinstance(i, Thargoid) == True and \
                        i.graphics_state == DISINTEGRATING and \
                        i.graphics_state_countdown == (DISINTEGRATING-1):

                    self.player_ship.add_hud_message('THARGOID DESTROYED', \
                            8, define.CYAN, False)

                    self.player_ship.planet_data.num_thargoids -= 1

                if isinstance(i, PlayerShip) == True:

                    if i.ecm_activated == True:

                        self.surface_controller.flight_surface.fill(\
                                define.NAVY)
                        self.surface_controller.flight_cover.fill(\
                                define.NAVY)
                        pygame.display.update()

                    if i.bomb_activated == True:

                        self.surface_controller.flight_surface.fill(\
                                define.ORANGE)
                        self.surface_controller.flight_cover.fill(\
                                define.ORANGE)
                        pygame.display.update()

                # missiles must be updated even when off-screen
                if isinstance(i, Missile):
                    i.off_screen_collision_detection()

                if i.sector_x == self.player_ship.sector_x and \
                   i.sector_y == self.player_ship.sector_y:

                    self.draw_group.add(i)

                    i.prerender_rotation()  # should be done here for optimization

                    if isinstance(i, Ship):

                        if i.launch_missile == True:

                            i.launch_missile = False
                            m = Missile(i, self.planet_data)
                            if isinstance(i, PlayerShip):
                                m.MAX_THRUST = 9.3
                                m.mass = 999
                            self.all_objects_group.add(m)
                            self.draw_group.add(m)
                            self.hud.add_blip(m)

                        if isinstance(i, Trader) == True or \
                                isinstance(i, Pirate) == True or \
                                isinstance(i, BountyHunter) == True:

                            if i.cargo_ejected == False and \
                                    i.graphics_state == DISINTEGRATING:

                                i.cargo_ejected = True
                                c = CargoContainer(i)
                                c.fill_with_random_cargo()

                                self.all_objects_group.add(c)
                                self.draw_group.add(c)
                                self.hud.add_blip(c)

                        if isinstance(i, PlayerShip) == True and \
                                i.state == define.EJECTING_CAPSULE:
                            
                            ec = EscapeCapsule(i)
                            self.all_objects_group.add(ec)
                            self.draw_group.add(ec)
                            self.hud.add_blip(ec)
                            i.state = define.ABANDONED
                            self.escape_capsule = ec
                            i.escape_pod = ec

            if self.reward_given == False:
                
                if self.planet_data.num_thargoids > 0 and \
                        self.planet_data.num_thargoids < 4:

                    for j in self.all_objects_group:
                        if isinstance(j, Thargoid) == True:
                            j.kill()
                    
                    self.planet_data.num_thargoids = 0 

                    name = self.planet_data.name
                    self.player_ship.add_hud_message( \
                           name.upper() + ' SYSTEM HAS BEEN LIBERATED!', \
                           16, define.PINK, False)
                    
                    self.player_ship.add_direct_bounty(1000)

                    self.player_ship.add_hud_message( \
                           '1,000 Cr REWARD RECEIVED', \
                           18, define.ORANGE, False)

                    self.player_ship.pilot.legal_status = define.CLEAN
                    self.player_ship.pilot.number_of_offenses = 0
                    
                    self.player_ship.add_hud_message( \
                           'LEGAL STATUS HAS BEEN CLEARED', \
                           20, define.SAND_BLUE, False)

                    self.player_ship.planet_data.newly_occupied = False

                    self.reward_given = True

                    # this is the best place to check for end-game (all systems
                    # free from thargoids)
                    total = 0
                    for h in self.planet_database.entry:
                        if h.num_thargoids > 0:
                            total += 1
                    if total == 0:
                        flatland_engine.thargoid_extinction = True

            self.draw_group.add(self.planet_object)
            self.draw_group.add(self.star_object)
            self.draw_group.add(self.station_object)

            self.station_object.prerender_rotation()

        else: 

            self.draw_group.empty()

            for i in self.all_objects_group:

                # missiles must be updated even when off-screen
                if isinstance(i, Missile):
                    i.off_screen_collision_detection()

                if i.sector_x == self.escape_capsule.sector_x and \
                   i.sector_y == self.escape_capsule.sector_y:

                    self.draw_group.add(i)

                    i.prerender_rotation()  # should be done here for optimization

                    if isinstance(i, Ship):

                        if i.launch_missile == True:

                            i.launch_missile = False
                            m = Missile(i, self.planet_data)
                            if isinstance(i, PlayerShip):
                                m.MAX_THRUST = 9.3
                                m.mass = 999
                            self.all_objects_group.add(m)
                            self.draw_group.add(m)
                            self.hud.add_blip(m)

                        if isinstance(i, Trader) == True or \
                                isinstance(i, Pirate) == True:

                            if i.cargo_ejected == False and \
                                    i.graphics_state == DISINTEGRATING:

                                i.cargo_ejected = True
                                c = CargoContainer(i)
                                c.fill_with_random_cargo()

                                self.all_objects_group.add(c)
                                self.draw_group.add(c)
                                self.hud.add_blip(c)

            self.draw_group.add(self.planet_object)
            self.draw_group.add(self.star_object)
            self.draw_group.add(self.station_object)

            self.station_object.prerender_rotation()

    def collision_detection(self):

        for i in self.draw_group:

            if i.graphics_state != DISINTEGRATING:

                i.collision_detection(self.draw_group)


    def run_all_pilot_AI(self):

        for i in self.draw_group:
            if isinstance(i, NonPlayerShip):
                if i.graphics_state != DISINTEGRATING:
                    i.on_screen_pilot_AI(self.draw_group)

        for i in self.flight_group:
            i.off_screen_pilot_AI(self.draw_group)

    def all_objects_update(self):

        self.all_objects_group.update()


    def clear(self):

        self.draw_group.clear( \
                self.surface_controller.flight_surface, \
                self.surface_controller.flight_cover) 

    def draw(self):

        # draw all sprites
        self.draw_group.draw( \
                self.surface_controller.flight_surface)
       
        # erase all previous lasers
        for j in self.laser_drawing_buffer:

            source_coord = j[0]
            target_coord = j[1]

            pygame.draw.line( \
                    self.surface_controller.flight_surface, \
                    define.BLACK, source_coord, target_coord, 10)

            self.laser_drawing_buffer.remove(j)

        #self.laser_drawing_buffer = []

        # draw any new lasers
        for i in self.draw_group:

            if isinstance(i, Ship) == True and i.laser_discharged == True:

                source_coord = (i.laser_coordinates[0], i.laser_coordinates[1])
                target_coord = (i.laser_coordinates[2], i.laser_coordinates[3])

                temp = (source_coord, target_coord)
                self.laser_drawing_buffer.append(temp)

                pygame.draw.line( \
                        self.surface_controller.flight_surface, \
                        i.color, source_coord, target_coord, 3)

                flatland_engine.sound.play_sound_effect(i.laser_sound)

                i.laser_discharged = False
    
    def draw_hud(self):

        self.hud.update(self.surface_controller)
        self.hud.draw(self.surface_controller)

    def repopulate_system(self):

        self.surface_controller.clear_surfaces()

        self.planet_data        = self.player_ship.planet_data

        self.draw_group         = pygame.sprite.Group()
        self.all_objects_group  = pygame.sprite.Group()
        self.flight_group       = pygame.sprite.Group() # for better AI

        # sprites
        self.planet_object      = Planet(self.planet_data)  
        self.star_object        = Star(self.planet_data)    
        self.station_object     = Station(self.planet_data)

        self.hud = hud.HudPanel(self.player_ship)
        
        self.populate_all_objects_group()
        
class Missile(Ship):

    def __init__(self, ship, planet_data):

        self.ship = ship  # ship that launched the missile

        image = pygame.image.load('images/missile.png').convert()
        image.set_colorkey(define.BLACK)
        x = ship.global_x
        y = ship.global_y

        # call parent constructor
        ship_type = define.MISSILE
        Ship.__init__(self, image, x, y, planet_data, ship_type)
       
        # adjust after Object constructor call
        self.color = define.CYAN
        self.orientation = ship.orientation 
        self.thrust = self.MAX_THRUST 
        self.recalculate_displacement()
        self.prerender_rotation()
        self.bounty = 51.99

        self.mass = 445 
        self.energy = 100

        self.time_to_live = define.FRAMERATE * 30    
        self.missile_target = self.ship.missile_target
        self.guidance_counter = 0

        flatland_engine.sound.play_sound_effect('MISSILE')

        self.name = 'MISSILE'

    def find_distance(self):

        a = self.global_x - self.missile_target.global_x
        b = self.global_y - self.missile_target.global_y
        c = math.sqrt((a*a) + (b*b))

        return c

    def update(self):

        if self.graphics_state != DISINTEGRATING:

            target = self.ship.missile_target

            if target != None:

                self.guidance_counter += 1
                if self.guidance_counter > 5:

                    self.guidance_counter = 0

                    tp = game_engine.Point(target.global_x,target.global_y)

                    # calculate 3 estimates (points): left, right, stay straight
                    turn_right = self.estimate(-1)
                    stay_straight = self.estimate(0)
                    turn_left = self.estimate(1)

                    # calculate distance to target for each, choose shortest method
                    right = game_engine.Vector(tp, turn_right)
                    straight = game_engine.Vector(tp, stay_straight)
                    left = game_engine.Vector(tp, turn_left)

                    right = right.mag
                    straight = straight.mag
                    left = left.mag

                    distance_list = [right, straight, left]
                    distance_list.sort()
                    min_dis = distance_list[0]

                    if min_dis == right:
                        self.turn_ship(-1)
                    elif min_dis == left:
                        self.turn_ship(1)

            self.thrust += self.THRUST_DELTA 
            if self.thrust > self.MAX_THRUST:
                self.thrust = self.MAX_THRUST
        
            self.time_to_live -= 1
            if self.time_to_live <= 0:
                self.damage_handler(9999)

        Object.update(self)


    def estimate(self, direction):

        # returns estimate (Point) of current ship location plus the dx,dy
        # if the ship turns left, right, or stays straight
        
        o = self.ORIENTATION_DELTA * direction

        orientation = float((self.orientation + o) % 360.0)

        dx = self.thrust * math.cos(math.radians(orientation))
        dy = self.thrust * math.sin(math.radians(orientation))
        dy = -dy   

        new_x = self.global_x + dx
        new_y = self.global_y + dy

        p = game_engine.Point(new_x,new_y)

        return p

    def off_screen_collision_detection(self):

        if self.graphics_state != DISINTEGRATING:

            target = self.ship.missile_target

            if target != None:

                a = self.global_x - target.global_x
                b = self.global_y - target.global_y

                c = int(math.sqrt( (a*a) + (b*b) ))

                if c < target.radius:

                    target.damage_handler(self.mass, self)
                    self.damage_handler(9999) # missile explodes

                    if isinstance(self.ship, PlayerShip) == True and \
                            target.graphics_state == DISINTEGRATING:
                        self.ship.pilot.increase_kill_count()
                        self.ship.add_bounty(target)
                        if isinstance(target, Police) == True or \
                                isinstance(target, Trader) == True or \
                                isinstance(target, BountyHunter) == True:
                            self.ship.pilot.increase_offense_count()



    def collision_detection(self, draw_group):

        hit_list = pygame.sprite.spritecollide(self, draw_group, False, \
                pygame.sprite.collide_circle)

        for h in hit_list:

            if h != self:   # ensure missile doesn't blow itself up

                if h.graphics_state != DISINTEGRATING:

                    if h != self.ship: # don't blow up the ship that launched missile 

                        h.damage_handler(self.mass, self)
                        self.damage_handler(1000)  # missile explodes
                    
                        if isinstance(self.ship, PlayerShip) == True and \
                                h.graphics_state == DISINTEGRATING:
                            self.ship.pilot.increase_kill_count()
                            self.ship.add_bounty(h)
                            if isinstance(h, Police) == True or \
                                    isinstance(h, Trader) == True or \
                                    isinstance(h, BountyHunter) == True:
                                self.ship.pilot.increase_offense_count()


class CargoContainer(Object):

    # this cargo container holds 17 different types of items

    def __init__(self, ship):

        self.ship = ship
 
        # core data (17 items)
        self.hold = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.total = 0
        self.CARGO_HOLD_LIMIT = 20 

        image = pygame.image.load('images/cargo_container.png').convert()
        image.set_colorkey(define.BLACK)
        x = ship.global_x
        y = ship.global_y

        # call parent constructor
        Object.__init__(self, image, x, y)
       
        # adjust after Object constructor call
        self.color = define.CYAN
        self.orientation = ship.orientation 
        self.thrust /= 2 
        self.recalculate_displacement()
        self.prerender_rotation()
        self.bounty = 0 

        self.mass = 5 
        self.energy = 5 
        
        self.MAX_THRUST = 4.0
        self.MIN_THRUST = 1.0 
        self.THRUST_DELTA = 0.18    # thrust change per frame, if thrusting
        self.ORIENTATION_DELTA = 3.8    # orientation change per frame, if turning
        
        self.spin = random.random() * random.choice([-4.5,4.5])
        self.color = define.CYAN

        self.name = 'CARGO CONTAINER'

    def update(self):

        # call parent update()
        Object.update(self)

        if self.graphics_state != DISINTEGRATING:
            self.adjust_orientation(self.spin)
    
    def add_item(self, item):

        if ( self.total < self.CARGO_HOLD_LIMIT ):
            self.hold[item] += 1
            self.total += 1

            # check for illegal purchases
            if isinstance(self.ship, PlayerShip):

                # if gov type is 4,5,6,7 (the more "civilized" systems), then
                # any buying/selling of weapons, slaves, or narcotics is illegal
                gov = self.ship.planet_data.government

                if gov > 1:

                    if item == 3 or item == 6 or item == 10:

                        self.ship.flagged_for_illegal_trading = True

    def remove_item(self, item):
  
        if self.hold[item] > 0:
            self.hold[item] -= 1
            self.total -= 1
        
            # check for illegal sales 
            if isinstance(self.ship, PlayerShip):

                # if gov type is 4,5,6,7 (the more "civilized" systems), then
                # any buying/selling of weapons, slaves, or narcotics is illegal
                gov = self.ship.planet_data.government

                if gov > 1:

                    if item == 3 or item == 6 or item == 10:

                        self.ship.flagged_for_illegal_trading = True

    def print_manifest(self):

        string_list = []
        
        temp = ''

        for i in COMMODITY_NAME:

            temp += COMMODITY_NAME[i]
            temp += '   '
            temp += str(self.hold[i])

            string_list.append(temp)

            temp = ''

        for i in COMMODITY_NAME:
            print( string_list[i] )

    def collision_detection(self, draw_group):

        hit_list = pygame.sprite.spritecollide(self, draw_group, False, \
                pygame.sprite.collide_circle)

        for h in hit_list:

            if h != self:   # ensure container doesn't blow itself up

                if isinstance(h, PlayerShip) != True:

                    if h != self.ship: # don't hurt ship that ejected container

                        h.damage_handler(self.mass)
                        self.damage_handler(1000)  # missile explodes


    def fill_with_random_cargo(self):

        random_item = random.randint(0,16)

        num_items = random.randint(3,30)

        for i in range(num_items):

            self.add_item(random_item)
