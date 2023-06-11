# Author: Darron Vanaria
# Filesize: 23344 bytes
# LOC: 543

# GAME ENGINE: SurfaceController, Clock, TextGridArray, init()
#  
#    Surfaces: 1. window_surface (may change resolution and fullscreen)
#              2. game_surface (filled color rectangle) subsurface of 1
#

import pygame
import os   # for os.enviro
import sys  # for sys.stdout.flush()
import math # for vector mathematics

import define

def init():  # early setup, calls pygame.init()

    window_pos_x = 50 
    window_pos_y = 20 

    os.environ['SDL_VIDEO_WINDOW_POS'] = \
            "%d,%d" % (window_pos_x,window_pos_y)

    #pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()  
    #pygame.key.set_repeat(200,200)
    
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    pygame.event.set_blocked(pygame.ACTIVEEVENT)
    pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
    pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
    pygame.event.set_blocked(pygame.KEYUP)

    pygame.mouse.set_visible(0)


##############################################################################
# SOUND
#
class SoundComponent:

    def __init__(self):

        # The following 3 lines are to prevent any sound delay in pygame.mixer
        pygame.mixer.quit()
        #pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.mixer.init()

        self.music = []

        self.sound_effect_dict = {} 

        self.current_volume = 0.1

    def add_sound_effect(self, name, filename):

        s = pygame.mixer.Sound(filename)

        s.set_volume( self.current_volume )

        self.sound_effect_dict[name] = s

        return len(self.sound_effect_dict)

    def change_volume_sound_fx(self, new_vol):

        self.current_volume = new_vol

        if self.current_volume < 0:
            self.current_volume = 0
        if self.current_volume > 1:
            self.current_volume = 1

        for v in self.sound_effect_dict.values():

            v.set_volume( self.current_volume )

    def play_sound_effect(self, name):

        self.sound_effect_dict[name].stop()
        self.sound_effect_dict[name].play()

    def add_music(self, filename):

        self.music.append(filename)

        return len(self.music)

    def play_music(self, index):

        #pygame.mixer.music.stop()

        pygame.mixer.music.load(self.music[index-1])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0.0)

    def stop_music(self):

        pygame.mixer.music.stop()


##############################################################################
# SURFACE CONTROLLER
#
class SurfaceController():

    def __init__(self, w, h, color):

        # w,h will at first be used for both window size and game resolution
        # color is used to fill the game_surface, a solid rectangle

        self.fullscreen = False 
        self.game_w = w  # this will always be the size of the game_surface
        self.game_h = h
        
        # get maximum possible resolution
        infoObject = pygame.display.Info()
        self.max_w = infoObject.current_w
        self.max_h = infoObject.current_h
        print()
        print('  NATIVE SCREEN RESOLUTION: ' + str(self.max_w) + ' x ' + str(self.max_h))
        sys.stdout.flush()

        if self.max_w < w or self.max_h < h:
            print()
            print('This game requires at least ' + str(w) + ' x ' + str(h) + \
                    ' native resolution to play.')
            print()
            sys.stdout.flush()
            sys.exit()

        self.window_surface = None
        self.game_surface = None

        # set up window surface

        if self.fullscreen == True:
            self.window_surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
            res = (self.max_w, self.max_h)
        else:
            self.window_surface = pygame.display.set_mode((w, h))

        # set up game surface, at first it will overlap window_surface exactly

        self.game_surface = \
            self.window_surface.subsurface(self.window_surface.get_rect())

        self.game_surface_color = color
        self.game_surface.fill( self.game_surface_color )
       
        # build supported resolutions list
        
        self.res_list = []
        self.res_list.append((self.game_w, self.game_h))
        self.res_list.append((640,480))    # 4:3
        self.res_list.append((800,600))    # 4:3
        self.res_list.append((960,720))    # 4:3 
        self.res_list.append((1024,768))   # 4:3
        self.res_list.append((1280,720))   # 16:9
        self.res_list.append((1280,768))   # near 8:5
        self.res_list.append((1280,800))   # 8:5
        self.res_list.append((1280,1024))  # 5:4
        self.res_list.append((1366,768))   # near 16:9
        self.res_list.append((1440,900))   # 8:5

        # remove any resolutions that are smaller than the initial resolution
        for i in self.res_list[:]:
            if i[0] < self.game_w or i[1] < self.game_h:
                self.res_list.remove(i)

        # remove resolutions that are bigger than native display
        for i in self.res_list[:]:
            if i[0] > self.max_w or i[1] > self.max_h:
                self.res_list.remove(i)

        # remove any duplicates of initial resolution 
        count = 0
        for i in self.res_list[:]:
            if i[0] == self.game_w and i[1] == self.game_h:
                count += 1
                if count > 1:
                    self.res_list.remove(i)

        print()
        print('  SUPPORTED RESOLUTIONS:')
        print()
        for i in self.res_list:
            print('    ' + str(i))
        print()
        sys.stdout.flush()

        # current resolution
        self.index = 0

    def get_info(self):

        rect = self.window_surface.get_rect()

        string_list = []

        i = "  RESOLUTION: " + str(rect.width) + " x " + str(rect.height) 

        string_list.append(i)

        i = "MODE: "
        if self.fullscreen == True:
            i += "FULLSCREEN"
        else:
            i += "WINDOWED"

        string_list.append(i)

        return string_list

    def toggle_fullscreen(self):

        if self.fullscreen == False:
            self.fullscreen = True
            pygame.mouse.set_visible(0)
        else:
            self.fullscreen = False
            pygame.mouse.set_visible(1)

        self.rebuild_window_surface()

    def toggle_resolution(self):

        self.index += 1 

        if self.index > len(self.res_list) - 1:
            self.index = 0

        self.rebuild_window_surface()

    # private
    def rebuild_window_surface(self):

        res = (self.res_list[self.index][0], \
               self.res_list[self.index][1])

        safe_copy = self.game_surface.copy()  # backup copy of game_surface

        self.window_surface = None
        self.game_surface = None

        # set up window surface

        if self.fullscreen == True:
            self.window_surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
            res = (self.max_w, self.max_h)
        else:
            self.window_surface = pygame.display.set_mode(res)

        # set up game surface

        rect = self.window_surface.get_rect()
        
        new_offset_x = int( rect.width / 2.0 )
        new_offset_x -= int ( self.game_w / 2.0 )

        new_offset_y = int( rect.height / 2.0 )
        new_offset_y -= int ( self.game_h / 2.0 )

        new_rect = ( \
                (new_offset_x, new_offset_y, self.game_w, self.game_h))

        self.game_surface = self.window_surface.subsurface( new_rect )
        self.game_surface.blit(safe_copy, (0,0))  # restore backup copy


##############################################################################
# TIMER 
#
class Clock():

    # this one object is used for all timers, as well as a framerate lock.
    # a function print_info() is available to track overall game performance.

    def __init__(self, framerate):

        self.clock = pygame.time.Clock()
        self.total_time = 0
        self.loop_counter = 0
        self.warnings = 0
        self.max_iteration_time = int(1000 / float(framerate))

        self.framerate = framerate

    def start_loop_timer(self):

        self.start_time = pygame.time.get_ticks()

    def stop_loop_timer(self):

        self.end_time = pygame.time.get_ticks()
        
        iteration_time = (self.end_time - self.start_time)
        
        self.total_time += iteration_time 

        self.loop_counter += 1
        """
        if iteration_time > self.max_iteration_time: 
            print('  FRAMERATE DROP: ' + str(iteration_time) + ' ms')
            sys.stdout.flush()
            self.warnings += 1
        """

    def lock_framerate(self):

        self.clock.tick(self.framerate)

    def print_info(self):

        if self.loop_counter != 0:
            avg = float(self.total_time / self.loop_counter)
            avg = round(avg,2)
            print('  AVERAGE GAME-LOOP ITERATION: ' + str(avg) + ' ms')
            # print('  Number of warnings: ' + str(self.warnings) + ' (framerate drops)')
            print()
            sys.stdout.flush()

##############################################################################
# TEXT COMPONENTS (this is mostly used internally by the game engine)
#

class TextGridArray():

    # this object holds all the characters on a given "screen".
    # you can use multiple objects for different screens and retain in memory.

    def __init__(self, w, h):

        # (w,h) are how many characters will fit on the surface that will be
        # used to draw on (passed directly to the draw() function).

        self.text_group = pygame.sprite.Group()

        self.font_manager = FontManager()

        self.GRID_WIDTH  = w
        self.GRID_HEIGHT = h

        self.cursor_row = 0
        self.min_cursor_row = 0
        self.max_cursor_row = self.GRID_HEIGHT - 1

    def draw(self, surface):

        # this will draw all Sprites in the text_group onto the supplied 
        # surface. 

        self.text_group.draw(surface)

    def clear(self, surface, background):

        # 2 surfaces: 'surface' and 'background'
        # this function will erase the last Sprites that were drawn using the
        # draw() function, covering them up with the background surface.

        self.text_group.clear(surface, background)

    def empty_container(self):

        self.text_group.empty()
      
    def print(self, string, col, row, fg, bg, transparent=False):

        char_list = list(string)

        count = 0

        for c in char_list:

            self.add_char(c, col + count, row, fg, bg, transparent)
            count += 1
    
    def print_centered(self, string, row, fg, bg, transparent=False):

        half_length = int(len(string) / 2)
        mid_point = ((self.GRID_WIDTH-1) / 2) + 1
        col = mid_point - half_length

        char_list = list(string)

        count = 0

        for c in char_list:

            self.add_char(c, col + count, row, fg, bg, transparent)
            count += 1

    def unhighlight_row(self, row, highlight_color):

        for i in self.text_group:

            if i.r == row:

                i.image.set_colorkey(i.bg, pygame.RLEACCEL)

    def highlight_row(self, row, highlight_color, transparent=False):

        # this will only highlight existing characters in this row

        for i in self.text_group:
            if i.r == row:
                self.add_char(i.char, i.c, i.r, i.fg, highlight_color, \
                        transparent)
                self.text_group.remove(i)

    def move_cursor(self, direction):

        new_loc = self.cursor_row + direction

        if new_loc >= self.min_cursor_row and new_loc <= self.max_cursor_row:
            self.cursor_row += direction

    # private
    def add_char(self, char, c, r, fg, bg, transparent=False):
       
        if c >= 0 and c < self.GRID_WIDTH:

            if r >= 0 and r < self.GRID_HEIGHT:
        
                glyph = self.font_manager.get_glyph_copy(char)

                # replace WHITE/BLACK with desired fg/bg colors
                pixObj = pygame.PixelArray(glyph)
                pixObj.replace(define.WHITE, fg)
                pixObj.replace(define.BLACK, bg)
                del pixObj
       
                letter = TextCell(char, glyph, c, r, fg, bg, transparent)
               
                # check if there is already an existing character at this 
                # location, if there is, remove the old object (3rd argument)
                pygame.sprite.spritecollide(letter, self.text_group, True)

                self.text_group.add(letter)

    def add_char_by_index(self, index, c, r, fg, bg, transparent=False):
       
        if c >= 0 and c < self.GRID_WIDTH:

            if r >= 0 and r < self.GRID_HEIGHT:
        
                glyph = self.font_manager.get_glyph_by_index(index)

                # replace WHITE/BLACK with desired fg/bg colors
                pixObj = pygame.PixelArray(glyph)
                pixObj.replace(define.WHITE, fg)
                pixObj.replace(define.BLACK, bg)
                del pixObj

                char = 'SPECIAL' 
       
                letter = TextCell(char, glyph, c, r, fg, bg, transparent)
               
                # check if there is already an existing character at this 
                # location, if there is, remove the old object (3rd argument)
                pygame.sprite.spritecollide(letter, self.text_group, True)

                self.text_group.add(letter)

    # untested 
    def add_file_contents(self, filename, fg, bg, transparent=False):

        # all text source files must end with the word 'END'

        # open file read contents into a list called "lines"
        f = open(filename, 'r')
        lines = []
        line = f.readline() 
        line = line.rstrip()
        while line != 'END':
            lines.append(line)
            line = f.readline()
            line = line.rstrip()
        f.close()

        # parse "lines" and add a new String for each
        row = 0
        for i in lines:
            self.print(i, 0, row, fg, bg, transparent)
            row += 1
    
    def add_file_contents_at(self, filename, row, col, fg, bg, transparent=False):

        # all text source files must end with the word 'END'

        # open file read contents into a list called "lines"
        f = open(filename, 'r')
        lines = []
        line = f.readline() 
        while line != 'END':
            lines.append(line)
            line = f.readline()
        f.close()

        # parse "lines" and add a new String for each
        for i in lines:
            self.print(i, col, row, fg, bg, transparent)
            row += 1

def swap_colors(sprite, original_color, replacement_color):

    pixObj = pygame.PixelArray(sprite)
    pixObj.replace(original_color, replacement_color)
    del pixObj

class Point():

    def __init__(self, x, y):

        self.x = x
        self.y = y

class Vector():

    def __init__(self, p1, p2):

        # a vector is created from two points, we say "vector from p1->p2"

        self.x = p2.x - p1.x
        self.y = -(p2.y - p1.y)

        self.mag = self.magnitude()
        self.dir = self.direction()

        self.p1 = p1  # save original points
        self.p2 = p2

    def magnitude(self):

        a = self.x * self.x
        b = self.y * self.y

        c = math.sqrt(a+b)

        self.mag = c

        return c

    def direction(self):

        # 360 degrees, 0 = East

        radians = math.atan2(self.y, self.x)

        degrees = math.degrees(radians) % 360

        self.dir = degrees

        return degrees

    def collision_with_circle(self, x, y, r):

        # returns True if this vector intersects the circle centered at x,y

        #     (x3-x1)(x2-x1) + (y3-y1)(y2-y1)
        # u = -------------------------------
        #              ||p2-p1||^2

        x1 = self.p1.x
        x2 = self.p2.x
        x3 = x

        y1 = self.p1.y
        y2 = self.p2.y
        y3 = y

        mag_squared = self.mag * self.mag

        n1 = (x3-x1) * (x2-x1)
        n2 = (y3-y1) * (y2-y1)

        if mag_squared != 0:
            u = (n1 + n2) / mag_squared
        else:
            return False 

        if u <= 0 or u >= 1:    
            return False       

        # intersection of where tangent hits vector
        i_x = x1 + (u * (x2-x1))
        i_y = y1 + (u * (y2-y1))

        # The distance therefore between the point P3 and the line is the 
        # distance between (x,y) above and P3. 
        p1 = Point(i_x,i_y)
        p2 = Point(x3,y3)

        test_vector = Vector(p1,p2)
        if test_vector.mag > r or test_vector.mag < -r:
            return False
        else:
            return True


    def distance_to_circle_origin(self, x, y, r):

        #     (x3-x1)(x2-x1) + (y3-y1)(y2-y1)
        # u = -------------------------------
        #              ||p2-p1||^2

        x1 = self.p1.x
        x2 = self.p2.x
        x3 = x

        y1 = self.p1.y
        y2 = self.p2.y
        y3 = y

        mag_squared = self.mag * self.mag

        n1 = (x3-x1) * (x2-x1)
        n2 = (y3-y1) * (y2-y1)

        if mag_squared != 0:
            u = (n1 + n2) / mag_squared
        else:
            return False 

        if u <= 0 or u >= 1:
            return False

        # intersection of where tangent hits vector
        i_x = x1 + (u * (x2-x1))
        i_y = y1 + (u * (y2-y1))

        # The distance therefore between the point P3 and the line is the 
        # distance between (x,y) above and P3. 
        p1 = Point(i_x,i_y)
        p2 = Point(x3,y3)

        test_vector = Vector(p1,p2)

        return test_vector.mag

def format_and_save_image(photo):

    # normalize pixels to game engine's palette
    rect = photo.get_rect()
    c_max = rect.width
    r_max = rect.height

    for c in range(c_max):

        for r in range(r_max):

            color = photo.get_at((c,r))

            if color.r >= 0 and color.r <= 64:
                color.r = 0
            elif color.r > 64 and color.r <= 192:
                color.r = 127
            else:
                color.r = 255
            
            if color.g >= 0 and color.g <= 64:
                color.g = 0
            elif color.g > 64 and color.g <= 192:
                color.g = 127
            else:
                color.g = 255
            
            if color.b >= 0 and color.b <= 64:
                color.b = 0
            elif color.b > 64 and color.b <= 192:
                color.b = 127
            else:
                color.b = 255

            photo.set_at((c,r), color)
   
    pygame.image.save(photo, 'images/formatted_and_saved_image.png')
            

# private to game engine #####################################################
class TextCell(pygame.sprite.Sprite):

    # bitmap to hold local copy of a glyph (with specific colors)

    def __init__(self, char, glyph, c, r, fg, bg, isTransparent):

        pygame.sprite.Sprite.__init__(self)

        self.char = char
        self.c = c
        self.r = r
        self.fg = fg
        self.bg = bg
        self.isTransparent = isTransparent

        self.image = glyph 

        if isTransparent == True:
            self.image.set_colorkey(self.bg, pygame.RLEACCEL)

        self.rect = self.image.get_rect()
        self.rect.x = FontManager.FONT_WIDTH * c
        self.rect.y = FontManager.FONT_HEIGHT * r

class FontManager():

    # This class will be used to load a single .png file that contains all
    # 128 characters (bitmaps) in an ASCII font set. It then builds a list of
    # subsurfaces (this list has 128 indices, 0 to 127).
    #
    # A function will be available that makes a copy of a given glyph and
    # returns the copy. The copy can be modified freely (changing colors for
    # example). This will allow multiple copies of the same glyph to be 
    # manipulated independently.

    FONT_FILE = 'fonts/c64_font_size_2.png'
    FONT_WIDTH = 16 
    FONT_HEIGHT = 16 
    GLYPHS_ACROSS = 16
    GLYPHS_DOWN = 8

    def __init__(self):

        self.font_set_master_surface = \
                pygame.image.load(FontManager.FONT_FILE).convert()

        self.master_glyph_set = []

        self.build_master_glyph_set()

    def build_master_glyph_set(self):

        index_w = 0
        index_h = 0

        for row in range(FontManager.GLYPHS_DOWN):
            for col in range(FontManager.GLYPHS_ACROSS):
                self.master_glyph_set.append( \
                        self.font_set_master_surface.subsurface(\
                        (index_w, index_h, FontManager.FONT_WIDTH, \
                        FontManager.FONT_HEIGHT)))
                index_w += FontManager.FONT_WIDTH 
            index_h += FontManager.FONT_HEIGHT 
            index_w = 0

    def get_glyph_copy(self, char):

        # Python built-in function ord('a') returns the ASCII index 97

        index = ord(char)

        return self.master_glyph_set[index].copy()
    
    def get_glyph_by_index(self, index):

        return self.master_glyph_set[index].copy()

# end of private to game engine ##############################################




'''
# Test Suite #################################################################
def test_func_1(x,y):

    print()
    p1 = Point(19,16)
    p2 = Point(x,y)
    v = Vector(p1,p2)
    print('   vector x = ' + str(v.x))
    print('   vector y = ' + str(v.y))
    print('   magnitude = ' + str(v.magnitude()))
    print('   direction = ' + str(v.direction()))
    print('   collision with circle? ' + str(v.collision_with_circle(25,10,3)))
    print('   P1: ' + str(p1.x) + ',' + str(p1.y))
    print('   P2: ' + str(p2.x) + ',' + str(p2.y))

def test_func_2(v):

    print()
    print('         p2 = ' + str(v.p2.x) + ',' + str(v.p2.y))
    print('   vector x = ' + str(v.x))
    print('   vector y = ' + str(v.y))
    print('   magnitude = ' + str(v.magnitude()))
    print('   direction = ' + str(v.direction()))
    print('   collision with circle? ' + str(v.collision_with_circle(23,8,5)))
    print('   P1: ' + str(v.p1.x) + ',' + str(v.p1.y))
    print('   P2: ' + str(v.p2.x) + ',' + str(v.p2.y))

print()
print(' Test of module game_engine.py...')
p1 = Point(19,16)

p2 = Point(11,24)
fore_LOS = Vector(p1,p2)
test_func_2(fore_LOS)

p2 = Point(27,24)
fore_LOS = Vector(p1,p2)
test_func_2(fore_LOS)

p2 = Point(27,8)
fore_LOS = Vector(p1,p2)
test_func_2(fore_LOS)

p2 = Point(11,8)
fore_LOS = Vector(p1,p2)
test_func_2(fore_LOS)
'''
