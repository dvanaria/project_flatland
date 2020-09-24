# Author: Darron Vanaria
# Filesize: 7742 bytes
# LOC: 140

import pygame
import random

import game_engine
import define
import tga_generator



# cross-file instance to play sounds
sound = game_engine.SoundComponent()

sound.add_sound_effect('GAME_START', 'sounds/bbc_micro_reset.wav')
sound.add_sound_effect('LASER_1', 'sounds/pulse_laser.wav')
sound.add_sound_effect('LASER_2', 'sounds/pulse_laser2.wav')
sound.add_sound_effect('LASER_3', 'sounds/pulse_laser3.wav')
sound.add_sound_effect('LASER_4', 'sounds/pulse_laser4.wav')
sound.add_sound_effect('LASER_5', 'sounds/pulse_laser5.wav')
sound.add_sound_effect('LASER_6', 'sounds/pulse_laser6.wav')
sound.add_sound_effect('MINOR_EXPLOSION_1', 'sounds/minor_explosion.wav')
sound.add_sound_effect('MINOR_EXPLOSION_2', 'sounds/minor_explosion2.wav')
sound.add_sound_effect('MINOR_EXPLOSION_3', 'sounds/minor_explosion3.wav')
sound.add_sound_effect('MINOR_EXPLOSION_4', 'sounds/minor_explosion4.wav')
sound.add_sound_effect('EXPLODE_1', 'sounds/explosion.wav')
sound.add_sound_effect('EXPLODE_2', 'sounds/explosion2.wav')
sound.add_sound_effect('EXPLODE_3', 'sounds/explosion3.wav')
sound.add_sound_effect('EXPLODE_4', 'sounds/explosion4.wav')
sound.add_sound_effect('UNDOCK', 'sounds/launch.wav')
sound.add_sound_effect('UNDOCK2', 'sounds/launch2.wav')
sound.add_sound_effect('UNDOCK3', 'sounds/launch3.wav')
sound.add_sound_effect('DOCK', 'sounds/docking.wav')
sound.add_sound_effect('DOCK2', 'sounds/docking2.wav')
sound.add_sound_effect('DOCK3', 'sounds/docking3.wav')
sound.add_sound_effect('COLLECT_1', 'sounds/collect.wav')
sound.add_sound_effect('COLLECT_2', 'sounds/collect2.wav')
sound.add_sound_effect('SELECTION_BAR', 'sounds/selection_bar.wav')
sound.add_sound_effect('JUMP_1', 'sounds/Jump.wav')
sound.add_sound_effect('JUMP_2', 'sounds/Jump2.wav')
sound.add_sound_effect('JUMP_3', 'sounds/Jump3.wav')
sound.add_sound_effect('JUMP_4', 'sounds/Jump4.wav')
sound.add_sound_effect('JUMP_5', 'sounds/jump5.wav')
sound.add_sound_effect('ECM_1', 'sounds/ecm.wav')
sound.add_sound_effect('ECM_2', 'sounds/ecm2.wav')
sound.add_sound_effect('ECM_3', 'sounds/ecm3.wav')
sound.add_sound_effect('BOMB_1', 'sounds/bomb.wav')
sound.add_sound_effect('BOMB_2', 'sounds/bomb2.wav')
sound.add_sound_effect('SUCCESS', 'sounds/success.wav')
sound.add_sound_effect('BUY', 'sounds/buy.wav')
sound.add_sound_effect('SELL', 'sounds/cash.wav')
sound.add_sound_effect('BEEP', 'sounds/bbc_beep.wav')
sound.add_sound_effect('BEEP_2', 'sounds/beep2.wav')
sound.add_sound_effect('BEEP_3', 'sounds/beep3.wav')
sound.add_sound_effect('BEEP_4', 'sounds/beep4.wav')
sound.add_sound_effect('BEEP_5', 'sounds/beep5.wav')
sound.add_sound_effect('BEEP_6', 'sounds/beep6.wav')
sound.add_sound_effect('BEEP_7', 'sounds/beep7.wav')
sound.add_sound_effect('BEEP_8', 'sounds/beep8.wav')
sound.add_sound_effect('CASH_1', 'sounds/cash.wav')
sound.add_sound_effect('CASH_2', 'sounds/cash2.wav')
sound.add_sound_effect('GAME_OVER_1', 'sounds/game_over_1.wav')
sound.add_sound_effect('GAME_OVER_2', 'sounds/game_over_2.wav')
sound.add_sound_effect('GAME_OVER_3', 'sounds/game_over_3.wav')
sound.add_sound_effect('GAME_OVER_4', 'sounds/game_over_2.wav')
sound.add_sound_effect('GAME_OVER_5', 'sounds/game_over_3.wav')
sound.add_sound_effect('LEGAL_STATUS_UPDATE', 'sounds/status_update.wav')
sound.add_sound_effect('MISSILE', 'sounds/missile.wav')
sound.add_sound_effect('INVASION', 'sounds/invasion.wav')
sound.add_sound_effect('INVASION2', 'sounds/invasion2.wav')
sound.add_sound_effect('LIBERTY', 'sounds/liberty.wav')
sound.add_sound_effect('VOICE_1', 'sounds/thargoid_voice_1.wav')
sound.add_sound_effect('VOICE_2', 'sounds/thargoid_voice_2.wav')
sound.add_sound_effect('VOICE_3', 'sounds/thargoid_voice_3.wav')
sound.add_sound_effect('VOICE_4', 'sounds/thargoid_voice_4.wav')
sound.add_sound_effect('VOICE_5', 'sounds/thargoid_voice_5.wav')
sound.add_sound_effect('VOICE_6', 'sounds/thargoid_voice_6.wav')
sound.add_sound_effect('VOICE_7', 'sounds/thargoid_voice_7.wav')
sound.add_sound_effect('VOICE_8', 'sounds/thargoid_voice_8.wav')
sound.add_sound_effect('VOICE_9', 'sounds/thargoid_voice_9.wav')
sound.add_sound_effect('MISSILE_ARMED', 'sounds/missile_armed.wav')

sound.add_music('sounds/title_music.wav')


next_thargoid_invasion = \
        random.randint(define.COUNTDOWN_MIN, define.THARGOID_COUNTDOWN) 
next_liberation = \
        random.randint(define.COUNTDOWN_MIN, define.LIBERTY_COUNTDOWN) 

thargoid_extinction = False

end_game_presented = False

thargoid_voice = 30 * random.randint(5, 20)

class SurfaceController():

    # Use this instead of game_engine's SurfaceController to control the two
    # main surfaces that are specific to Elite Flatland: flight_surface and
    # hud_surface.
    #
    # Instead of game_surface, you'll be using flight_surface and hud_surface,
    # which are their own clipping rectangles (because they are subsurfaces of
    # game_surface).
    #
    # This controller also maintains cover backgrounds for each surface (flight
    # and hud).

    def __init__(self):

        self.controller = \
                game_engine.SurfaceController( \
                define.GAME_W, define.GAME_H, define.YELLOW)

        self.flight_surface = self.controller.game_surface.subsurface(define.FLIGHT_RECT)
        self.flight_surface.fill(define.BLACK)
        self.flight_cover = self.flight_surface.copy() 

        self.hud_surface = self.controller.game_surface.subsurface(define.HUD_RECT)
        hud_image = pygame.image.load('images/hud.png').convert()
        self.hud_surface.blit(hud_image, (0,0))
        self.hud_cover = self.hud_surface.copy() 

    def clear_surfaces(self):

        self.flight_surface = self.controller.game_surface.subsurface(define.FLIGHT_RECT)
        self.flight_surface.fill(define.BLACK)
        self.flight_cover = self.flight_surface.copy() 

        self.hud_surface = self.controller.game_surface.subsurface(define.HUD_RECT)
        hud_image = pygame.image.load('images/hud.png').convert()
        self.hud_surface.blit(hud_image, (0,0))
        self.hud_cover = self.hud_surface.copy() 

    def toggle_fullscreen(self):

        # note: this uses surface backgrounds as backup copies

        flight_backup = self.flight_cover.copy()
        hud_backup = self.hud_surface.copy()   # copy front surface as backup

        self.controller.toggle_fullscreen()
       
        self.set_subsurfaces(flight_backup, hud_backup)

    def toggle_resolution(self):
        
        # note: this uses surface backgrounds as backup copies

        flight_backup = self.flight_cover.copy()
        hud_backup = self.hud_surface.copy()

        self.controller.toggle_resolution()
        
        self.set_subsurfaces(flight_backup, hud_backup)

    def sync_flight_cover(self):

        # After making changes to flight_surface, you may want to link the
        # flight_cover surface to match (for example, you want to use a
        # starfield background). Call this function to do that.

        self.flight_cover = self.flight_surface.copy() 

    def change_surface(self, new_surface):

        self.flight_surface.blit(new_surface, (0,0))
        self.sync_flight_cover()

    # private
    def set_subsurfaces(self, flight, hud):

        self.flight_surface = self.controller.game_surface.subsurface(define.FLIGHT_RECT)
        self.flight_surface.blit(flight, (0,0)) 
        self.flight_cover = self.flight_surface.copy() 

        self.hud_surface = self.controller.game_surface.subsurface(define.HUD_RECT)
        self.hud_surface.blit(hud, (0,0))
