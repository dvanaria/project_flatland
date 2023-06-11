# Author: Darron Vanaria
# Filesize: 5451 bytes
# LOC: 152

import pygame  # for color

FRAMERATE = 30 

GAME_W = 800
GAME_H = 708
BORDER = 4
FLIGHT_W = 792   
FLIGHT_H = 594 
HUD_W = 792  
HUD_H = 102

# each star system is composed of 8 x 8 screens (64 total)
GRID_SIZE = 8  
SYSTEM_W = FLIGHT_W * GRID_SIZE  # actual pixel size of each system
SYSTEM_H = FLIGHT_H * GRID_SIZE

SCANNER_W = 120
SCANNER_H = 90
SCANNER_SCALE_W = (FLIGHT_W * 3) / SCANNER_W
SCANNER_SCALE_H = (FLIGHT_H * 3) / SCANNER_H

COMPASS_W = 64
COMPASS_H = 48
COMPASS_SCALE_W = SYSTEM_W / COMPASS_W 
COMPASS_SCALE_H = SYSTEM_H / COMPASS_H

# rects to place flight_surface and hud_surface within game_surface
FLIGHT_RECT = (BORDER, BORDER, FLIGHT_W, FLIGHT_H)
HUD_RECT = (BORDER, BORDER + FLIGHT_H + BORDER, HUD_W, HUD_H)

# text grid (always on flight_surface)
FONT_W = 16
FONT_H = 16
TEXT_GRID_W = 49  # 0-48     # data.py screen: rows 3-36, cols 1-48 (inclusive) 
TEXT_GRID_H = 37  # 0-36
TEXT_GRID_TITLE_ROW = 1
TEXT_GRID_DATA_ROW = 3  # first row of data on any data screen

# special characters from the font set
CHAR_UP    = 1
CHAR_DOWN  = 3
CHAR_LEFT  = 4
CHAR_RIGHT = 2

# galactic chart
GALACTIC_CHART_SIZE_W = 512  # size of chart in pixels 
GALACTIC_CHART_SIZE_H = 256  # size of chart in pixels (75% of 512 = 384)
GALACTIC_CHART_SCALE_W = GALACTIC_CHART_SIZE_W / 256   # float (ex: 2.0) 
GALACTIC_CHART_SCALE_H = GALACTIC_CHART_SIZE_H / 256   # float (ex: 1.5) 

# player ship state
FLYING             = 0
DOCKING            = 1
DOCKED             = 2
LAUNCHING          = 3
CLEARING_STATION   = 4
EJECTING_CAPSULE   = 5
ABANDONED          = 6  

# color (27 total, 24-bit RGB sets, using three values: 0, 127, and 255)
BLACK                = pygame.Color(000, 000, 000)
NAVY                 = pygame.Color(000, 000, 127)
BLUE                 = pygame.Color(000, 000, 255)
FOREST_GREEN         = pygame.Color(000, 127, 000)
TEAL                 = pygame.Color(000, 127, 127)
BLUE_GREEN           = pygame.Color(000, 127, 255)
GREEN                = pygame.Color(000, 255, 000)
PALE_GREEN           = pygame.Color(000, 255, 127)
CYAN                 = pygame.Color(000, 255, 255)
MAROON               = pygame.Color(127, 000, 000)
PURPLE               = pygame.Color(127, 000, 127)
INDIGO               = pygame.Color(127, 000, 255)
OLIVE                = pygame.Color(127, 127, 000)
GRAY                 = pygame.Color(127, 127, 127)
SAND_BLUE            = pygame.Color(127, 127, 255)
KERMIT_GREEN         = pygame.Color(127, 255, 000)
POND_SCUM            = pygame.Color(127, 255, 127)
AQUA                 = pygame.Color(127, 255, 255)
RED                  = pygame.Color(255, 000, 000)
BARBIE               = pygame.Color(255, 000, 127)
MAGENTA              = pygame.Color(255, 000, 255)
ORANGE               = pygame.Color(255, 127, 000)
CORAL                = pygame.Color(255, 127, 127)
PINK                 = pygame.Color(255, 127, 255)
YELLOW               = pygame.Color(255, 255, 000)
KHAKI                = pygame.Color(255, 255, 127)
WHITE                = pygame.Color(255, 255, 255)

# legal status
CLEAN     = 0
OFFENDER  = 1 # shot at trader/bounty_hunter, illegal goods, shot space station
FUGITIVE  = 2 # shot at police, killed trader or bounty_hunter

# combat ranking (value = number of kills required) * notice: not linear
HARMLESS        = 0	
MOSTLY_HARMLESS = 8 
POOR            = 16 
AVERAGE         = 32 
ABOVE_AVERAGE   = 64 
COMPETENT       = 128 
DANGEROUS       = 512 
DEADLY          = 2560 
ELITE           = 6400 
    
LASER_NAME = ['PULSE LASER', 'BEAM LASER', 'MINING LASER', 'MILITARY LASER']

# ship types
ADDER               = 0
ANACONDA            = 1
ASP_MK_II           = 2
BOA_CLASS_CRUISER   = 3
COBRA_MK_I          = 4
COBRA_MK_III        = 5
FER_DE_LANCE        = 6
GECKO               = 7
KRAIT               = 8
MAMBA               = 9
MORAY_STAR_BOAT     = 10
PYTHON              = 11
SIDEWINDER          = 12
THARGOID            = 13
TRANSPORTER         = 14
VIPER               = 15
MISSILE             = 16


ship_image_pathname = [ \
        'images/ships/adder.png', \
        'images/ships/anaconda.png', \
        'images/ships/asp_mk_ii.png', \
        'images/ships/boa_class_cruiser.png', \
        'images/ships/cobra_mk_i.png', \
        'images/ships/cobra_mk_iii.png', \
        'images/ships/fer_de_lance.png', \
        'images/ships/gecko.png', \
        'images/ships/krait.png', \
        'images/ships/mamba.png', \
        'images/ships/moray_star_boat.png', \
        'images/ships/python.png', \
        'images/ships/sidewinder.png', \
        'images/ships/thargoid.png', \
        'images/ships/transporter.png', \
        'images/ships/viper.png', \
        'images/missile.png']

ship_name = [ \
        'adder', \
        'anaconda', \
        'asp mk ii', \
        'boa class cruiser', \
        'cobra mk i', \
        'cobra mk iii', \
        'fer de lance', \
        'gecko', \
        'krait', \
        'mamba', \
        'moray star boat', \
        'python', \
        'sidewinder', \
        'thargoid', \
        'transporter', \
        'viper', \
        'missile']

THARGOID_COUNTDOWN = 30 * 60 * 45   # every 35 minutes
LIBERTY_COUNTDOWN = 30 * 60 * 30  # every 20 minutes 
COUNTDOWN_MIN = 30 * 60 * 25
