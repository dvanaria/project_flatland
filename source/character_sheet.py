# Author: Darron Vanaria
# Filesize: 4160 bytes
# LOC: 104

import sys
import random

import define
import flatland_engine


class Player():

    def __init__(self, player_ship):

        self.current_ship = player_ship

        self.number_of_kills = 0 
        self.cash = 1000.00
        self.legal_status = define.CLEAN
        self.rating = define.HARMLESS
        self.number_of_offenses = 0

        self.right_on_commander = False

    def get_legal_status_string(self):

        if self.legal_status == define.CLEAN:
            return 'Clean'
        elif self.legal_status == define.OFFENDER:
            return 'Offender'
        else:
            return 'Fugitive'

    def get_condition_string(self):

        max_energy = self.current_ship.MAX_ENERGY

        if self.current_ship.state == define.DOCKED:
            return 'Docked'
        elif self.current_ship.energy < int(max_energy * .33):
            return 'Red'
        elif self.current_ship.energy < int(max_energy * .66):
            return 'Yellow'
        else:
            return 'Green'

    def get_combat_rating_string(self):

        if self.number_of_kills < 8:
            return 'Harmless'
        elif self.number_of_kills < 16:
            return 'Mostly Harmless'
        elif self.number_of_kills < 32:
            return 'Poor'
        elif self.number_of_kills < 64:
            return 'Average'
        elif self.number_of_kills < 128:
            return 'Above Average'
        elif self.number_of_kills < 512:
            return 'Competent'
        elif self.number_of_kills < 2560:
            return 'Dangerous'
        elif self.number_of_kills < 6400:
            return 'Deadly'
        else:
            return 'Elite'

    def get_next_combat_rating(self):

        if self.number_of_kills < 8:
            return (8 - self.number_of_kills) 
        elif self.number_of_kills < 16:
            return (16 - self.number_of_kills) 
        elif self.number_of_kills < 32:
            return (32 - self.number_of_kills) 
        elif self.number_of_kills < 64:
            return (64 - self.number_of_kills) 
        elif self.number_of_kills < 128:
            return (128 - self.number_of_kills) 
        elif self.number_of_kills < 512:
            return (512 - self.number_of_kills) 
        elif self.number_of_kills < 2560:
            return (2560 - self.number_of_kills) 
        elif self.number_of_kills < 6400:
            return (6400 - self.number_of_kills) 
        else:
            return 0 

    def increase_kill_count(self):

        old_rating = self.get_combat_rating_string()

        self.number_of_kills += 1

        new_rating = self.get_combat_rating_string()

        if old_rating != new_rating:
            m = 'Your combat rating is now: ' + new_rating
            self.current_ship.add_hud_message(m.upper(), 4, define.GREEN)
    
    def increase_offense_count(self):

        original_count = self.number_of_offenses

        self.number_of_offenses += 1

        if self.number_of_offenses <= 3:
            self.legal_status = define.OFFENDER
            s = self.get_legal_status_string()
            if self.number_of_offenses == 0:
                message = 'Your legal status is now ' + s
            elif self.number_of_offenses == 1:
                message = 'Your legal status is now ' + s + ' (1 strike)'
            else:
                message = 'Your legal status is now ' + s + ' (' + \
                        str(self.number_of_offenses) + ' strikes)'
        else:
            self.legal_status = define.FUGITIVE
            s = self.get_legal_status_string()
            message = 'Your legal status is now ' + s

        self.current_ship.add_hud_message(message.upper(), 6, define.ORANGE,\
                False)
            
        pick = \
            random.choice(['EXPLODE_1','EXPLODE_2','EXPLODE_3','EXPLODE_4'])
        flatland_engine.sound.play_sound_effect(pick)
        
        flatland_engine.sound.play_sound_effect('LEGAL_STATUS_UPDATE')

        updated_count = self.number_of_offenses
        if updated_count != original_count:
            self.current_ship.hud_update_needed = True

