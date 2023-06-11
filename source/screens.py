# Author: Darron Vanaria
# Filesize: 107955 bytes
# LOC: 1838

import pygame
import sys
import random
import pickle

import define
import game_engine
import tga_generator
import objects
import planet_database
import flatland_engine
import trade_database


REGULAR_MENU        = 0
BUY_SUB_MENU        = 1
SELL_SUB_MENU       = 2

# SCREENS:
# 1. Flight
# 3. Commodity Trading at ...
# 4. Ship Equipment & Upgrades at...
# 5. Pilot and Ship Information
# 7. Navigation: Set Hyperdrive Target
# 8. Navigation: Target Planet Info 
# 9. Navigation: Target Market Info



class FlightScreen():  # Screen 1 - Flight, external camera

    def __init__(self, object_controller, surface_controller, trade_database, \
            planet_database):
        
        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = object_controller.player_ship
        self.planet_data        = object_controller.planet_data
        self.trade_database     = trade_database
        self.planet_database    = planet_database
        
        # drawing components
        self.tga = tga_generator.hud_info(self.player_ship)
        self.static_backgrounds = self.generate_sector_screens_2D_array()
        self.surface = None

        self.fore_laser_check = 0
        self.port_laser_check = 0
        self.aft_laser_check = 0
        self.starboard_laser_check = 0

        self.ecm_check = 0
        self.bomb_check = 0
        self.pod_check = 0
        self.missile_check = 0
        self.missile_fire_check = 0
        self.jump_check = 0


    def assume_focus(self):

        self.tga.clear(self.surface_controller.flight_surface, \
                self.surface_controller.flight_cover)
        self.tga.empty_container()

        self.player_ship.message_queue.clear()
        self.rebuild_screen()
        pygame.key.set_repeat(10,10)
           
        if(flatland_engine.tutorial['FIRST_FLIGHT_1'] == False):
            i = 15
            self.player_ship.add_hud_message( \
                    'UP and DOWN controls thrust', i, \
                     flatland_engine.tutorial_color, False)
            self.player_ship.add_hud_message( \
                    'LEFT and RIGHT controls direction', i+2, \
                     flatland_engine.tutorial_color, False)
            flatland_engine.sound.play_sound_effect('SUCCESS')
            flatland_engine.tutorial['FIRST_FLIGHT_1'] = True
        
    def loop_iteration(self, input_events):

        # check for sector change (part 1)
        if self.player_ship.state == define.ABANDONED:
            old_x = self.object_controller.escape_capsule.sector_x
            old_y = self.object_controller.escape_capsule.sector_y
        else:
            old_x = self.player_ship.sector_x
            old_y = self.player_ship.sector_y
        
        # update all objects
        self.object_controller.all_objects_update()
        
        # process input
        pygame.event.pump()

        if self.player_ship.state != define.ABANDONED:

            keys = pygame.key.get_pressed()
            if self.player_ship.graphics_state != objects.DISINTEGRATING:
                if keys[pygame.K_LEFT] or keys[pygame.K_COMMA]:
                    self.player_ship.turn_ship(1)
                if keys[pygame.K_RIGHT] or keys[pygame.K_PERIOD]:
                    self.player_ship.turn_ship(-1)
                if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
                    if self.player_ship.fuel > 0:
                        self.player_ship.throttle_ship(1)
                if keys[pygame.K_DOWN] or keys[pygame.K_SLASH]:
                    self.player_ship.throttle_ship(-1)
                if keys[pygame.K_j]:
                    if self.player_ship.jump_initiated == False:
                        if self.player_ship.target_system == None or \
                            (self.player_ship.planet_data.name == 
                                    self.player_ship.target_system.name):
                            if self.jump_check <= 0:
                                self.player_ship.add_hud_message( \
                                        'NO HYPERDRIVE TARGET SELECTED', 17, \
                                        define.RED, False)
                                self.jump_check = 60
                        else:
                            self.player_ship.start_jump()
                if keys[pygame.K_x]:
                    if self.player_ship.equipment[objects.ESCAPE_CAPSULE] > 0:
                        if self.player_ship.eject_sequence_on == False:
                            self.player_ship.eject_sequence_on = True
                    else:
                        if self.pod_check <= 0:
                            self.player_ship.add_hud_message(\
                                    'NO ESCAPE CAPSULE INSTALLED', 17, \
                                    define.RED, False)
                            self.pod_check = 60
                if keys[pygame.K_z]:
                    if self.player_ship.eject_sequence_on == True:
                        self.player_ship.eject_sequence_on = False 
                        self.player_ship.eject_countdown = self.player_ship.EJECT_RESET
                        tga_generator.hud_eject_clear(self.tga, self.player_ship)
                        self.player_ship.add_hud_message('EJECT SEQUENCE ABORTED',\
                                19, define.BLUE, False)
                if keys[pygame.K_w]:  # forward laser
                    if self.player_ship.fore_laser != None:
                        self.player_ship.player_fires_laser(\
                                self.object_controller.draw_group, objects.FORE)
                    else:
                        if self.fore_laser_check <= 0:
                            self.player_ship.add_hud_message(\
                                    'NO FORE LASER INSTALLED', 17, define.BLUE, False)
                            self.fore_laser_check = 60

                if keys[pygame.K_s]:  # aft laser
                    if self.player_ship.aft_laser != None:
                        self.player_ship.player_fires_laser(\
                                self.object_controller.draw_group, objects.AFT)
                    else:
                        if self.aft_laser_check <= 0:
                            self.player_ship.add_hud_message(\
                                    'NO AFT LASER INSTALLED', 17, define.BLUE, False)
                            self.aft_laser_check = 60
                
                if keys[pygame.K_a]:  # port laser
                    if self.player_ship.port_laser != None:
                        self.player_ship.player_fires_laser(\
                                self.object_controller.draw_group, objects.PORT)
                    else:
                        if self.port_laser_check <= 0:
                            self.player_ship.add_hud_message(\
                                    'NO PORT LASER INSTALLED', 17, define.BLUE, False)
                            self.port_laser_check = 60
                
                if keys[pygame.K_d]:  # starboard laser
                    if self.player_ship.starboard_laser != None:
                        self.player_ship.player_fires_laser(\
                                self.object_controller.draw_group, objects.STARBOARD)
                    else:
                        if self.starboard_laser_check <= 0:
                            self.player_ship.add_hud_message(\
                                    'NO STARBOARD LASER INSTALLED', 17, define.BLUE, False)
                            self.starboard_laser_check = 60

                if keys[pygame.K_e]:  # ECM 
                    if self.ecm_check <= 0:
                        self.player_ship.player_uses_ECM(self.object_controller.draw_group)
                        self.rebuild_screen()
                        self.ecm_check = 60
                if keys[pygame.K_m]:
                    if self.missile_fire_check <= 0:
                        self.player_ship.player_fires_missile(self.object_controller.draw_group)
                        self.missile_fire_check = 60
                if keys[pygame.K_TAB]:
                    if self.bomb_check <= 0:
                        self.player_ship.player_uses_bomb(self.object_controller.draw_group)
                        self.rebuild_screen()
                        self.bomb_check = 60
                if keys[pygame.K_t]:
                    if self.player_ship.auto_targeting_on == False:
                        if self.player_ship.equipment[objects.MISSILE] > 0:
                            self.player_ship.auto_targeting_on = True
                            self.player_ship.add_hud_message( \
                            'MISSILE TARGETING SYSTEM ON', 24, define.YELLOW, False)
                            self.rebuild_screen()
                        else:
                            if self.missile_check <= 0:
                                self.player_ship.add_hud_message( \
                                'MISSILE SILOS EMPTY', 24, define.BLUE, False)
                                self.rebuild_screen()
                                self.missile_check = 60

                if keys[pygame.K_u]:
                    if self.player_ship.auto_targeting_on == True:
                        self.player_ship.auto_targeting_on = False 
                        self.player_ship.add_hud_message( \
                        'MISSILE TARGETING SYSTEM OFF', 24, define.BLUE, False)
                        self.rebuild_screen()
                        if self.player_ship.auto_target != None:
                            self.player_ship.auto_target.remove_targeting_square()
                            self.player_ship.auto_target.targeted = False
                        self.player_ship.auto_target = None
                        self.rebuild_screen()
                if keys[pygame.K_i]:

                    if self.player_ship.info_display_countdown <= 0:

                        self.player_ship.info_display_countdown = 60

                        line = 17 
                        for i in range(6):
                            self.player_ship.add_hud_message('', line+(i*2), \
                                    define.BLACK, False)

                        if self.player_ship.planet_data.num_thargoids > 0:
   
                            num_systems_infected = 0
                            galaxy_wide_num_thargoids = 0
                            for q in self.planet_database.entry:
                                if q.num_thargoids > 3:
                                    num_systems_infected += 1
                                    galaxy_wide_num_thargoids += \
                                        (q.num_thargoids-3)
                            
                            line = 18
                            n_tha = self.player_ship.planet_data.num_thargoids
                            self.player_ship.add_hud_message('LOCAL NUMBER OF THARGOIDS: ' +\
                                    str(n_tha - 3), line+2, define.GREEN, False)
                            self.player_ship.add_hud_message('STAR SYSTEMS OCCUPIED: ' +\
                                    str(num_systems_infected),\
                                    line+4, define.GREEN, False)
                            self.player_ship.add_hud_message('GALAXY-WIDE NUMBER OF THARGOIDS: ' +\
                                    str(galaxy_wide_num_thargoids),\
                                    line+6, define.GREEN, False)
                        else:
                            n_ast = 0
                            n_tra = 0
                            n_pol = 0
                            n_hun = 0
                            n_pir = 0
                            for i in self.object_controller.all_objects_group:
                                if isinstance(i, objects.Asteroid) == True and \
                                  i.graphics_state != objects.DISINTEGRATING:
                                    n_ast += 1
                                elif isinstance(i, objects.Trader) == True and \
                                  i.graphics_state != objects.DISINTEGRATING:
                                    n_tra += 1
                                elif isinstance(i, objects.Police) == True and \
                                  i.graphics_state != objects.DISINTEGRATING:
                                    n_pol += 1
                                elif isinstance(i, objects.BountyHunter) == True and \
                                  i.graphics_state != objects.DISINTEGRATING:
                                    n_hun += 1
                                elif isinstance(i, objects.Pirate) == True and \
                                  i.graphics_state != objects.DISINTEGRATING:
                                    n_pir += 1
                            line = 18 
                            self.player_ship.add_hud_message('NUMBER OF ASTEROIDS: ' +\
                                    str(n_ast), line+2, define.OLIVE, False)
                            self.player_ship.add_hud_message('NUMBER OF TRADERS: ' +\
                                    str(n_tra), line+4, define.GRAY, False)
                            self.player_ship.add_hud_message('NUMBER OF POLICE: ' +\
                                    str(n_pol), line+6, define.BLUE, False)
                            self.player_ship.add_hud_message('NUMBER OF BOUNTY HUNTERS: ' +\
                                    str(n_hun), line+8, define.PURPLE, False)
                            self.player_ship.add_hud_message('NUMBER OF PIRATES: ' +\
                                    str(n_pir), line+10, define.RED, False)
                            pygame.display.update()

            pygame.event.pump()

        # check for sector change (part 2)
        if self.player_ship.state == define.ABANDONED:
            new_x = self.object_controller.escape_capsule.sector_x
            new_y = self.object_controller.escape_capsule.sector_y
        else:
            new_x = self.player_ship.sector_x
            new_y = self.player_ship.sector_y

        if (new_x != old_x) or (new_y != old_y):
            self.rebuild_screen()
            if(flatland_engine.tutorial['FIRST_FLIGHT_3'] == False):
                i = 20 
                self.player_ship.add_hud_message( \
                        'Use WASD keys to fire lasers', i, \
                         flatland_engine.tutorial_color, False)
                flatland_engine.sound.play_sound_effect('SUCCESS')
                flatland_engine.tutorial['FIRST_FLIGHT_3'] = True
            elif(flatland_engine.tutorial['FIRST_FLIGHT_3'] == True and
                    flatland_engine.tutorial['FIRST_FLIGHT_4'] == False):
                i = 20 
                self.player_ship.add_hud_message( \
                        'Press J to Jump to next system', i, \
                         flatland_engine.tutorial_color, False)
                flatland_engine.sound.play_sound_effect('SUCCESS')
                flatland_engine.tutorial['FIRST_FLIGHT_4'] = True


        # clear all objects from current screen
        self.object_controller.clear()
        self.tga.clear(self.surface_controller.flight_surface, \
                self.surface_controller.flight_cover)
            
        # build draw group
        self.object_controller.build_draw_group()

        # test for collisions
        self.object_controller.collision_detection()

        # npc AI
        self.object_controller.run_all_pilot_AI()

        # player missile targeting
        if self.player_ship.auto_targeting_on == True:
            self.player_ship.auto_targeting(self.object_controller.draw_group)

        # check for hud messages
        for i in self.player_ship.message_queue:
            if i.timer == i.delay:
                tga_generator.hud_message(self.tga, i)
            elif i.timer <= 0:
                tga_generator.hud_message_clear(self.tga, i)
                self.player_ship.message_queue.remove(i)

        # check for game over
        if self.player_ship.state != define.ABANDONED:

            if self.player_ship.graphics_state == objects.GONE:

                self.rebuild_screen()
                for i in self.player_ship.message_queue:
                    i.timer = 1
                self.tga.clear(self.surface_controller.flight_surface, \
                        self.surface_controller.flight_cover)
                self.tga.empty_container()
                self.rebuild_screen()
                tga_generator.direct_message(self.tga, "GAME OVER", \
                        19, define.ORANGE)

                if self.object_controller.game_over == False:
                    pick = random.choice( \
                            ['GAME_OVER_1','GAME_OVER_2','GAME_OVER_3',\
                            'GAME_OVER_4','GAME_OVER_5'])
                    flatland_engine.sound.play_sound_effect(pick)
                    self.object_controller.game_over = True
        
        else: 

            if self.object_controller.escape_capsule.graphics_state == objects.GONE:

                self.rebuild_screen()
                for i in self.player_ship.message_queue:
                    i.timer = 1
                self.tga.clear(self.surface_controller.flight_surface, \
                        self.surface_controller.flight_cover)
                self.tga.empty_container()
                self.rebuild_screen()
                tga_generator.direct_message(self.tga, "GAME OVER", \
                        19, define.ORANGE)

                if self.object_controller.game_over == False:
                    pick = random.choice( \
                            ['GAME_OVER_1','GAME_OVER_2','GAME_OVER_3',\
                            'GAME_OVER_4','GAME_OVER_5'])
                    flatland_engine.sound.play_sound_effect(pick)
                    self.object_controller.game_over = True


        if self.player_ship.eject_sequence_on == True: 
            if self.player_ship.eject_countdown > 0:
                tga_generator.hud_eject_count(self.tga, self.player_ship)
            else:
                tga_generator.hud_info_update(self.tga, self.player_ship)

        # to prevent spamming of WASD keys when laser bays are empty        
        if self.fore_laser_check > 0:
            self.fore_laser_check -= 1 
        if self.port_laser_check > 0:
            self.port_laser_check -= 1 
        if self.aft_laser_check > 0:
            self.aft_laser_check -= 1 
        if self.starboard_laser_check > 0:
            self.starboard_laser_check -= 1 
        if self.pod_check > 0:
            self.pod_check -= 1
        if self.bomb_check > 0:
            self.bomb_check -= 1
        if self.missile_check > 0:
            self.missile_check -= 1
        if self.ecm_check > 0:
            self.ecm_check -= 1
        if self.missile_fire_check > 0:
            self.missile_fire_check -= 1
        if self.jump_check > 0:
            self.jump_check -= 1


        # check for need to update HUD data
        if self.player_ship.hud_update_needed == True:
            tga_generator.hud_info_update( self.tga, self.player_ship )
            self.player_ship.hud_update_needed = False
        

        # draw objects to current screen
        self.object_controller.draw()
        self.tga.draw(self.surface_controller.flight_surface)
        self.object_controller.draw_hud()

        if self.player_ship.state == define.DOCKING: 

            center_x = self.object_controller.station_object.rect.centerx
            center_y = self.object_controller.station_object.rect.centery

            pick = random.choice(['DOCK','DOCK2','DOCK3'])
            flatland_engine.sound.play_sound_effect(pick)

            for i in range(5):
                
                width = 15 + (self.object_controller.docking_sequence * 240) + \
                        (i*48)
                height = 5 + (self.object_controller.docking_sequence * 120) + \
                        (i*24)
                left = center_x - (width/2)
                top = center_y - (height/2)

                draw_dock_rect = pygame.Rect(left, top, width, height) 

                if i == 4:
                    pygame.draw.rect(self.surface_controller.flight_surface, \
                            define.RED, draw_dock_rect, 2)
                    pygame.draw.rect(self.surface_controller.flight_cover, \
                            define.RED, draw_dock_rect, 2)
                else:
                    pygame.draw.rect(self.surface_controller.flight_surface, \
                            define.CYAN, draw_dock_rect, 2)
                    pygame.draw.rect(self.surface_controller.flight_cover, \
                            define.CYAN, draw_dock_rect, 2)
        
        # check for ECM/Bomb usage (to erase "colored space")
        if self.player_ship.ecm_activated == True or \
                self.player_ship.bomb_activated == True:
            self.rebuild_screen()
            self.player_ship.ecm_activated = False
            self.player_ship.bomb_activated = False

    def rebuild_screen(self):

        if self.player_ship.state != define.ABANDONED:

            self.object_controller.planet_object.update_sector_offset( \
                    self.player_ship.sector_x, self.player_ship.sector_y )
            
            self.object_controller.star_object.update_sector_offset( \
                    self.player_ship.sector_x, self.player_ship.sector_y )

            self.object_controller.station_object.update_sector_offset( \
                    self.player_ship.sector_x, self.player_ship.sector_y )

            self.surface = \
                self.static_backgrounds[self.player_ship.sector_y][self.player_ship.sector_x]

            tga_generator.hud_info_update( self.tga, self.player_ship )

            self.surface_controller.change_surface( self.surface )

        else:

            ec = self.object_controller.escape_capsule
            
            self.object_controller.planet_object.update_sector_offset( \
                    ec.sector_x, ec.sector_y )
            
            self.object_controller.star_object.update_sector_offset( \
                    ec.sector_x, ec.sector_y )

            self.object_controller.station_object.update_sector_offset( \
                    ec.sector_x, ec.sector_y )

            self.surface = \
                self.static_backgrounds[ec.sector_y][ec.sector_x]

            self.surface_controller.change_surface( self.surface )


    def generate_sector_screens_2D_array(self):

        system = []

        # build a system-sector screens (64 screens total) structure
        # 2D array in Python is a "list of lists": array[row][col]
        temp = []
        for r in range(define.GRID_SIZE):
            for c in range(define.GRID_SIZE):
                s = pygame.Surface((define.FLIGHT_W,define.FLIGHT_H))
                s.fill(define.BLACK)
                temp.append( s )
            system.append(temp)
            temp = []

        # my god, its full of stars!
        for r in range(define.GRID_SIZE):
            for c in range(define.GRID_SIZE):
                temp_screen = system[r][c]
                for i in range(19):  # number of background stars per screen
                    temp_size = random.choice([2,2,2,3])
                    temp_x = random.randint(4,define.FLIGHT_W-4)
                    temp_y = random.randint(4,define.FLIGHT_H-4)
                    pygame.draw.circle(temp_screen, define.WHITE, \
                            (temp_x,temp_y), temp_size)

        return system



class OffScreenLoopHandler():

    def __init__(self, oc, ps):

        self.object_controller = oc
        self.player_ship = ps

    def iteration(self):

        # update all objects
        self.object_controller.all_objects_update()
        
        if self.player_ship.state == define.FLYING or \
           self.player_ship.state == define.CLEARING_STATION:

            # build draw group
            self.object_controller.build_draw_group()

            # test for collisions
            self.object_controller.collision_detection()

            # npc AI
            self.object_controller.run_all_pilot_AI()

        # draw objects to current screen
        self.object_controller.draw_hud()



class TradingScreen():   # Screen 3 - Commodity Trading at Local Market

    def __init__(self, object_controller, surface_controller, player_ship, \
            trade_database):

        self.trade_database     = trade_database
        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.player             = player_ship.pilot 

        i = self.player_ship.planet_data.number
        self.market = self.trade_database.get_market_by_index(i)
        self.tga = tga_generator.trading_screen(self.market, self.player_ship)
        self.surface = pygame.image.load('images/data.png').convert()
        
        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)
        
        self.tga.draw(self.surface) # now surface holds all static text

    def assume_focus(self):
       
        i = self.player_ship.planet_data.number
        self.market = self.trade_database.get_market_by_index(i)
        self.tga = tga_generator.trading_screen(self.market, self.player_ship)
        self.add_dynamic_text()
        pygame.key.set_repeat(180,90)

    def loop_iteration(self, input_events):
       
        self.loop.iteration()

        cash = self.player.cash

        # process input
        if self.player_ship.graphics_state != objects.DISINTEGRATING:
            for e in input_events:

                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_LEFT:

                        # sell item? must have it in cargo hold
                        item = self.tga.cursor_row - 7
                        if self.player_ship.cargo.hold[item] > 0:
                            self.player_ship.cargo.remove_item(item)
                            self.player.cash += self.market.prices[item]
                            flatland_engine.sound.play_sound_effect('SELL')
                            string = '    ' + 'SELLING ' + \
                                trade_database.commodity_name[item].strip() + \
                                     '    '
                            tga_generator.trading_screen_add_message(self.tga, \
                                    string.upper(), define.MAGENTA)
                            self.market.stock[item] += 1
                        else:
                            tga_generator.trading_screen_add_message(self.tga, \
                                    '    ITEM NOT IN CARGO HOLD    ')
                        self.add_dynamic_text()

                    if e.key == pygame.K_RIGHT:

                        # buy item? must be in stock, must have enough money,
                        # and must have enough space in cargo hold
                        item = self.tga.cursor_row - 7
                        if self.market.stock[item] > 0:
                            if cash > self.market.prices[item]:

                                if self.player_ship.cargo.total < \
                                        self.player_ship.cargo.CARGO_HOLD_LIMIT:
                                    self.player_ship.cargo.add_item(item)
                                    self.player.cash -= self.market.prices[item]
                                    self.market.stock[item] -= 1
                                    string = '    ' + 'BUYING ' + \
                                        trade_database.commodity_name[item].strip() + \
                                             '    '
                                    tga_generator.trading_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    flatland_engine.sound.play_sound_effect('BUY')
                                else:
                                    tga_generator.trading_screen_add_message(self.tga, \
                                            '        CARGO HOLD FULL        ')

                            else:
                                tga_generator.trading_screen_add_message(self.tga, \
                                        '        NOT ENOUGH CREDITS        ')
                        else:
                            tga_generator.trading_screen_add_message(self.tga, \
                                    '        ITEM NOT AVAILABLE        ')
                        self.add_dynamic_text()

                    if e.key == pygame.K_UP: 

                        tga_generator.trading_screen_add_message(self.tga, '')
                        tga_generator.trading_screen_move_cursor(self.tga, -1)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

                    if e.key == pygame.K_DOWN:

                        tga_generator.trading_screen_add_message(self.tga, '')
                        tga_generator.trading_screen_move_cursor(self.tga, 1)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

    def add_dynamic_text(self):

        tga_generator.trading_screen_data(self.tga, self.player_ship, \
                self.market)

        self.tga.draw(self.surface) # now surface holds all static text

        self.surface_controller.change_surface( self.surface )




class EquipmentPurchaseScreen():   # Screen 4 - Ship Equipment and Upgrades 

    def __init__(self, object_controller, surface_controller, player_ship):

        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.player             = player_ship.pilot 
        self.planet             = player_ship.planet_data

        self.tga = tga_generator.equipment_purchase_screen(self.planet, self.player_ship)
        self.surface = pygame.image.load('images/data.png').convert()
        
        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)
        
        self.tga.draw(self.surface) # now surface holds all static text
    
    def assume_focus(self):
       
        self.surface = pygame.image.load('images/data.png').convert()
        self.planet = self.player_ship.planet_data 
        self.tga = tga_generator.equipment_purchase_screen(self.planet, self.player_ship)
        self.add_dynamic_text()
        pygame.key.set_repeat(280,180)
         
        self.mode = REGULAR_MENU

    def loop_iteration(self, input_events):
       
        self.loop.iteration()

        if self.mode == REGULAR_MENU:

            cash = self.player.cash
                
            # process input
            for e in input_events:

                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_LEFT:

                        # sell item? must have it on ship 
                        item = self.tga.cursor_row - 7

                        if item == objects.FUEL:

                            if self.player_ship.fuel == 0.0:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       FUEL TANK EMPTY      ')
                                self.add_dynamic_text()
                            else:
                                fuel_amount = self.player_ship.drain_fuel(1)
                                temp = self.planet.equipment[item]
                                price = (temp[1] * fuel_amount)
                                self.player.cash += price 
                                flatland_engine.sound.play_sound_effect('SELL')
                                string = '    ' + 'SELLING ' + \
                                    planet_database.equipment_name[item].strip() + \
                                         '    '
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        string.upper(), define.MAGENTA)
                                self.add_dynamic_text()

                            self.player_ship.equipment[0] = self.player_ship.fuel

                        elif item == objects.MISSILE:

                            if self.player_ship.equipment[objects.MISSILE] <= 0:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       MISSILE SILOS EMPTY      ')
                                self.add_dynamic_text()
                            else:
                                self.player_ship.equipment[objects.MISSILE] -= 1
                                temp = self.planet.equipment[item]
                                price = temp[1]
                                self.player.cash += price 
                                flatland_engine.sound.play_sound_effect('SELL')
                                string = '    ' + 'SELLING ' + \
                                    planet_database.equipment_name[item].strip() + \
                                         '    '
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        string.upper(), define.MAGENTA)
                                self.add_dynamic_text()

                        elif item == objects.ECM_SYSTEM:

                            if self.player_ship.equipment[objects.ECM_SYSTEM] <= 0:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       NO ECM SYSTEMS INSTALLED       ')
                                self.add_dynamic_text()
                            else:
                                self.player_ship.equipment[objects.ECM_SYSTEM] -= 1
                                temp = self.planet.equipment[item]
                                price = temp[1]
                                self.player.cash += price 
                                flatland_engine.sound.play_sound_effect('SELL')
                                string = '    ' + 'SELLING ' + \
                                    planet_database.equipment_name[item].strip() + \
                                         '    '
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        string.upper(), define.MAGENTA)
                                self.add_dynamic_text()

                        
                        elif item == objects.ENERGY_BOMB:

                            if self.player_ship.equipment[objects.ENERGY_BOMB] <= 0:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       NO ENERGY BOMBS INSTALLED       ')
                                self.add_dynamic_text()
                            else:
                                self.player_ship.equipment[objects.ENERGY_BOMB] -= 1
                                temp = self.planet.equipment[item]
                                price = temp[1]
                                self.player.cash += price 
                                flatland_engine.sound.play_sound_effect('SELL')
                                string = '    ' + 'SELLING ' + \
                                    planet_database.equipment_name[item].strip() + \
                                         '    '
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        string.upper(), define.MAGENTA)
                                self.add_dynamic_text()

                        elif item == objects.EXTRA_ENERGY_UNIT:
     
                            if self.player_ship.equipment[item] > 0:

                                self.player_ship.equipment[item] = 0
                                temp = self.planet.equipment[item]
                                price = temp[1]
                                self.player.cash += price 
                                flatland_engine.sound.play_sound_effect('SELL')
                                string = '    ' + 'SELLING ' + \
                                    planet_database.equipment_name[item].strip() + \
                                         '    '
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        string.upper(), define.MAGENTA)
                                self.add_dynamic_text()

                            else:
                                
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       ITEM NOT INSTALLED ON SHIP       ')
                                self.add_dynamic_text()


                        elif item == objects.LARGE_CARGO_BAY:

                            if self.player_ship.equipment[item] > 0:

                                if self.player_ship.cargo.total > 0:

                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '    CARGO BAY MUST BE EMPTIED FIRST    ')

                                else:

                                    self.player_ship.equipment[item] = 0
                                    temp = self.planet.equipment[item]
                                    price = temp[1]
                                    self.player.cash += price 
                                    flatland_engine.sound.play_sound_effect('SELL')
                                    string = '    ' + 'SELLING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.MAGENTA)
                                    self.add_dynamic_text()

                                    self.player_ship.cargo.CARGO_HOLD_LIMIT = 20

                            else:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       ITEM NOT INSTALLED ON SHIP       ')

                        elif item == objects.PULSE_LASER: 

                            if self.player_ship.equipment[objects.PULSE_LASER] > 0:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       SELECT WHICH PULSE LASER TO SELL       ')

                                self.laser_selection = objects.PULSE
                                 
                                self.change_mode(SELL_SUB_MENU)

                            else:
                                
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       NO PULSE LASERS TO SELL       ')

                        elif item == objects.BEAM_LASER: 

                            if self.player_ship.equipment[objects.BEAM_LASER] > 0:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       SELECT WHICH BEAM LASER TO SELL       ')

                                self.laser_selection = objects.BEAM
                                
                                self.change_mode(SELL_SUB_MENU)

                            else:
                                
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       NO BEAM LASERS TO SELL       ')

                        elif item == objects.MINING_LASER: 

                            if self.player_ship.equipment[objects.MINING_LASER] > 0:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       SELECT WHICH MINING LASER TO SELL       ')

                                self.laser_selection = objects.MINING
                                
                                self.change_mode(SELL_SUB_MENU)

                            else:
                                
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       NO MINING LASERS TO SELL       ')

                        elif item == objects.MILITARY_LASER: 

                            if self.player_ship.equipment[objects.MILITARY_LASER] > 0:

                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       SELECT WHICH MILITARY LASER TO SELL       ')

                                self.laser_selection = objects.MILITARY
                                
                                self.change_mode(SELL_SUB_MENU)

                            else:
                                
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '       NO MILITARY LASERS TO SELL       ')

                        elif self.player_ship.equipment[item] > 0:

                            self.player_ship.equipment[item] = 0
                            temp = self.planet.equipment[item]
                            price = temp[1]
                            self.player.cash += price 
                            flatland_engine.sound.play_sound_effect('SELL')
                            string = '    ' + 'SELLING ' + \
                                planet_database.equipment_name[item].strip() + \
                                     '    '
                            tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                    string.upper(), define.MAGENTA)
                            self.add_dynamic_text()

                        else:

                            tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                    '       ITEM NOT INSTALLED ON SHIP       ')

                        self.add_dynamic_text()

                    elif e.key == pygame.K_RIGHT:
        
                        # buy item? need enough cash and open space on ship
                        item = self.tga.cursor_row - 7

                        if item == objects.FUEL:

                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.fuel < (self.player_ship.MAX_FUEL):

                                if cash > price:

                                    fuel_amount = self.player_ship.install_fuel(1)
                                    self.player.cash -= (price * fuel_amount)
                                    flatland_engine.sound.play_sound_effect('BUY')
                                    string = '    ' + 'BUYING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    self.add_dynamic_text()
                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                               

                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '          FUEL TANK FULL          ')

                            self.player_ship.equipment[0] = self.player_ship.fuel
                            self.add_dynamic_text()

                        elif item == objects.MISSILE:

                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.equipment[objects.MISSILE] < 4:

                                if cash > price:

                                    self.player_ship.equipment[objects.MISSILE] += 1
                                    self.player.cash -= price 
                                    flatland_engine.sound.play_sound_effect('BUY')
                                    string = '    ' + 'BUYING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    self.add_dynamic_text()
                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '      MISSILE SILOS FULL      ')

                            self.add_dynamic_text()
                        
                        elif item == objects.ECM_SYSTEM:

                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.equipment[objects.ECM_SYSTEM] < 3:

                                if cash > price:

                                    self.player_ship.equipment[objects.ECM_SYSTEM] += 1
                                    self.player.cash -= price 
                                    flatland_engine.sound.play_sound_effect('BUY')
                                    string = '    ' + 'BUYING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    self.add_dynamic_text()
                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '      LIMIT 3 ECM SYSTEMS REACHED      ')

                            self.add_dynamic_text()
                        
                        elif item == objects.ENERGY_BOMB:

                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.equipment[objects.ENERGY_BOMB] < 3:

                                if cash > price:

                                    self.player_ship.equipment[objects.ENERGY_BOMB] += 1
                                    self.player.cash -= price 
                                    flatland_engine.sound.play_sound_effect('BUY')
                                    string = '    ' + 'BUYING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    self.add_dynamic_text()
                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '      LIMIT 3 ENERGY BOMBS REACHED      ')

                            self.add_dynamic_text()

                        elif item == objects.LARGE_CARGO_BAY:

                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.equipment[item] == 0:

                                if cash > price:

                                    self.player_ship.equipment[item] = 1
                                    self.player.cash -= price 
                                    flatland_engine.sound.play_sound_effect('BUY')
                                    string = '    ' + 'BUYING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    self.add_dynamic_text()
                                    self.player_ship.cargo.CARGO_HOLD_LIMIT = 35
                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '      LARGE CARGO BAY ALREADY INSTALLED      ')

                            self.add_dynamic_text()

                        elif item == objects.EXTRA_ENERGY_UNIT:

                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.equipment[item] == 0:

                                if cash > price:

                                    self.player_ship.equipment[item] = 1
                                    self.player.cash -= price 
                                    flatland_engine.sound.play_sound_effect('BUY')
                                    string = '    ' + 'BUYING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    self.add_dynamic_text()
                                
                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '      EXTRA ENERGY UNIT ALREADY INSTALLED      ')

                            self.add_dynamic_text()

                        elif item == objects.PULSE_LASER or \
                                item == objects.BEAM_LASER or \
                                item == objects.MINING_LASER or \
                                item == objects.MILITARY_LASER:
                            
                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.equipment[item] < 4:

                                if cash > price:
                            
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                       '       SELECT WHERE TO INSTALL LASER       ')

                                    if item == objects.PULSE_LASER:
                                        self.laser_selection = objects.PULSE
                                    elif item == objects.BEAM_LASER:
                                        self.laser_selection = objects.BEAM
                                    elif item == objects.MINING_LASER:
                                        self.laser_selection = objects.MINING
                                    elif item == objects.MILITARY_LASER:
                                        self.laser_selection = objects.MILITARY

                                    self.change_mode(BUY_SUB_MENU)

                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '      ALL LASER BAYS TAKEN      ')

                        else:
                            
                            temp = self.planet.equipment[item]
                            price = temp[1]

                            if self.player_ship.equipment[item] == 0: 

                                if cash > price:
                                   
                                    # now buy/install desired item 
                                    temp = self.planet.equipment[item]
                                    price = temp[1]
                                    self.player_ship.equipment[item] = 1
                                    temp = self.planet.equipment[item]
                                    self.player.cash -= price 
                                    flatland_engine.sound.play_sound_effect('BUY')
                                    string = '    ' + 'BUYING ' + \
                                        planet_database.equipment_name[item].strip() + \
                                             '    '
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            string.upper(), define.CYAN)
                                    self.add_dynamic_text()
                                
                                else:
                                    tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                            '        NOT ENOUGH CREDITS        ')
                            else:
                                tga_generator.equipment_purchase_screen_add_message(self.tga, \
                                        '        ITEM ALREADY INSTALLED ON SHIP        ')
                           
                        self.add_dynamic_text()
       
                    elif e.key == pygame.K_UP:
        
                        self.move_cursor(-1)

                    elif e.key == pygame.K_DOWN:
        
                        self.move_cursor(1)
            

        elif self.mode == SELL_SUB_MENU:

            cash = self.player.cash

            # process input
            for e in input_events:

                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_LEFT or e.key == pygame.K_RETURN or \
                            e.key == pygame.K_RIGHT:

                        loc = self.tga.cursor_row - 30 
                        
                        self.sell_laser_at_location(loc)

                    elif e.key == pygame.K_ESCAPE:
                                    
                        self.change_mode(REGULAR_MENU)

                    elif e.key == pygame.K_UP:

                        self.move_cursor(-1)

                    elif e.key == pygame.K_DOWN:
        
                        self.move_cursor(1)
        
        elif self.mode == BUY_SUB_MENU:

            cash = self.player.cash

            # process input
            for e in input_events:

                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_ESCAPE:
                        
                        self.change_mode(REGULAR_MENU)

                    elif e.key == pygame.K_RIGHT or e.key == pygame.K_RETURN or\
                            e.key == pygame.K_LEFT:
                                    
                        loc = self.tga.cursor_row - 30 
                        
                        self.buy_laser_at_location(loc)

                    elif e.key == pygame.K_UP:

                        self.move_cursor(-1)

                    elif e.key == pygame.K_DOWN:
        
                        self.move_cursor(1)

    def move_cursor(self, direction):

        tga_generator.equipment_purchase_screen_add_message(self.tga, \
                '                                              ')
        tga_generator.equipment_purchase_screen_move_cursor(self.tga, direction)
        self.tga.draw(self.surface_controller.flight_surface) 
        flatland_engine.sound.play_sound_effect('SELECTION_BAR')

    def change_mode(self, mode):

        if mode == REGULAR_MENU:
                   
            self.tga.highlight_row(self.tga.cursor_row, \
                    define.BLACK)
            self.tga.min_cursor_row = 7 
            self.tga.max_cursor_row = 6 + \
                  len(self.player_ship.planet_data.equipment)
            self.tga.cursor_row = 7 
            self.tga.highlight_row(7, define.RED)

        elif mode == SELL_SUB_MENU or mode == BUY_SUB_MENU:

            self.tga.highlight_row(self.tga.cursor_row, \
                    define.BLACK)
            self.tga.min_cursor_row = 30 
            self.tga.max_cursor_row = 33
            self.tga.cursor_row = 30 
            self.tga.highlight_row(30, define.RED)

        self.mode = mode
                                
        self.add_dynamic_text()

    def sell_laser_at_location(self, location):

        # sell laser at this hardpoint location

        if location == objects.FORE:
            laser_type = self.player_ship.fore_laser
        elif location == objects.PORT:
            laser_type = self.player_ship.port_laser
        elif location == objects.AFT:
            laser_type = self.player_ship.aft_laser
        elif location == objects.STARBOARD:
            laser_type = self.player_ship.starboard_laser

        if laser_type != self.laser_selection: 

            n = define.LASER_NAME[self.laser_selection]
            tga_generator.equipment_purchase_screen_add_message(self.tga, \
             '       NO ' + n + ' INSTALLED HERE       ')
            self.change_mode(REGULAR_MENU)

        else:

            if self.laser_selection == objects.PULSE:
                self.player_ship.equipment[objects.PULSE_LASER] -= 1
                temp = self.planet.equipment[objects.PULSE_LASER]
            elif self.laser_selection == objects.BEAM:
                self.player_ship.equipment[objects.BEAM_LASER] -= 1
                temp = self.planet.equipment[objects.BEAM_LASER]
            elif self.laser_selection == objects.MINING:
                self.player_ship.equipment[objects.MINING_LASER] -= 1
                temp = self.planet.equipment[objects.MINING_LASER]
            elif self.laser_selection == objects.MILITARY:
                self.player_ship.equipment[objects.MILITARY_LASER] -= 1
                temp = self.planet.equipment[objects.MILITARY_LASER]

            price = temp[1] 
            self.player.cash += price 
            flatland_engine.sound.play_sound_effect('SELL')
            tga_generator.equipment_purchase_screen_add_message(self.tga, \
                    '                                ')
            if location == objects.FORE:
                self.player_ship.fore_laser = None
            elif location == objects.PORT:
                self.player_ship.port_laser = None
            elif location == objects.AFT:
                self.player_ship.aft_laser = None
            elif location == objects.STARBOARD:
                self.player_ship.starboard_laser = None
    
            self.change_mode(REGULAR_MENU)

    def buy_laser_at_location(self, location):

        # sell laser at this hardpoint location

        if location == objects.FORE:
            laser_type = self.player_ship.fore_laser
        elif location == objects.PORT:
            laser_type = self.player_ship.port_laser
        elif location == objects.AFT:
            laser_type = self.player_ship.aft_laser
        elif location == objects.STARBOARD:
            laser_type = self.player_ship.starboard_laser

        if laser_type != None: 

            tga_generator.equipment_purchase_screen_add_message(self.tga, \
             '       LASER BAY NOT AVAILABLE       ')
            self.change_mode(REGULAR_MENU)

        else:

            if self.laser_selection == objects.PULSE:
                self.player_ship.equipment[objects.PULSE_LASER] += 1
                temp = self.planet.equipment[objects.PULSE_LASER]
            elif self.laser_selection == objects.BEAM:
                self.player_ship.equipment[objects.BEAM_LASER] += 1
                temp = self.planet.equipment[objects.BEAM_LASER]
            elif self.laser_selection == objects.MINING:
                self.player_ship.equipment[objects.MINING_LASER] += 1
                temp = self.planet.equipment[objects.MINING_LASER]
            elif self.laser_selection == objects.MILITARY:
                self.player_ship.equipment[objects.MILITARY_LASER] += 1
                temp = self.planet.equipment[objects.MILITARY_LASER]

            price = temp[1] 
            self.player.cash -= price 
            flatland_engine.sound.play_sound_effect('BUY')
            tga_generator.equipment_purchase_screen_add_message(self.tga, \
                    '                                ')
            if location == objects.FORE:
                self.player_ship.fore_laser = self.laser_selection 
            elif location == objects.PORT:
                self.player_ship.port_laser = self.laser_selection
            elif location == objects.AFT:
                self.player_ship.aft_laser = self.laser_selection 
            elif location == objects.STARBOARD:
                self.player_ship.starboard_laser = self.laser_selection 
    
            self.change_mode(REGULAR_MENU)

    def add_dynamic_text(self):

        tga_generator.equipment_purchase_screen_data(self.tga, self.player_ship, \
                self.planet)

        self.tga.draw(self.surface) # now surface holds all static text

        self.surface_controller.change_surface( self.surface )





class StatusScreen():  # Screen 5 - Pilot and Ship Information

    def __init__(self, object_controller, surface_controller, player):

        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = object_controller.player_ship
        self.player             = player 

        self.tga = tga_generator.status_screen(self.player)
        self.surface = pygame.image.load('images/data.png').convert()
        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)

    def assume_focus(self):
       
        self.surface = pygame.image.load('images/data.png').convert()
        self.tga = tga_generator.status_screen(self.player)
        self.rebuild_screen()
        pygame.key.set_repeat(0,0)

        
    def loop_iteration(self, input_events):

        self.loop.iteration()
    
    def rebuild_screen(self):

        self.object_controller.planet_object.update_sector_offset( \
                self.player_ship.sector_x, self.player_ship.sector_y )
        
        self.object_controller.star_object.update_sector_offset( \
                self.player_ship.sector_x, self.player_ship.sector_y )

        self.object_controller.station_object.update_sector_offset( \
                self.player_ship.sector_x, self.player_ship.sector_y )

        tga_generator.status_screen_update(self.tga, self.player)
        
        if(flatland_engine.tutorial['BEGIN_NEW_GAME'] == False):
            i = 27 
            self.tga.print_centered('Use number keys 3,4,5 and 7,8,9', i, 
                    flatland_engine.tutorial_color, define.BLACK, False)
            self.tga.print_centered('to view different on-board computer screens.', i+1, 
                    flatland_engine.tutorial_color, define.BLACK, False)
            self.tga.print_centered('Use number key 1 to launch from station!', i+3, 
                    flatland_engine.tutorial_color, define.BLACK, False)
            flatland_engine.sound.play_sound_effect('SUCCESS')
            flatland_engine.tutorial['BEGIN_NEW_GAME'] = True

        self.tga.draw(self.surface)
        
        self.surface_controller.change_surface( self.surface )




class GalacticChartScreen():   # Screen 7 - Navigation Set Hyperdrive Target

    def __init__(self, object_controller, surface_controller, planet_database, \
            trade_database):
        
        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = object_controller.player_ship
        self.planet_database    = planet_database
        self.trade_database     = trade_database
        
        self.cursor = pygame.image.load('images/galactic_chart_cursor.png').convert()
        self.cursor.set_colorkey(define.BLACK)
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_x = self.player_ship.planet_data.galactic_x
        self.cursor_y = self.player_ship.planet_data.galactic_y

        self.origin = pygame.image.load('images/galactic_chart_origin.png').convert()
        self.origin.set_colorkey(define.BLACK)

        self.target_market = None

        # drawing components
        self.map_rect = None
        self.tga = None
        self.static_background = self.get_galactic_chart_surface()
        self.surface = self.static_background.copy() 

        self.move_cursor(0,0)
        self.rebuild_screen()
        
        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)

    def assume_focus(self):

        self.static_background = \
                self.get_galactic_chart_surface()
        self.surface = \
                self.static_background.copy() 
        
        i = self.player_ship.target_system.number
        self.target_market = self.trade_database.get_market_by_index(i)

        self.rebuild_screen()
        self.recenter_cursor()
        self.surface_controller.change_surface( self.surface ) 
        pygame.key.set_repeat(40,40)

    def loop_iteration(self, input_events):
       
        # erase objects
        self.clear_cursor() 
        self.clear_text()

        # process input
        for e in input_events:

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_UP:
                    self.move_cursor(0,-4)
                elif e.key == pygame.K_DOWN:
                    self.move_cursor(0,4)
                elif e.key == pygame.K_LEFT:
                    self.move_cursor(-2,0)
                elif e.key == pygame.K_RIGHT:
                    self.move_cursor(2,0)
                elif e.key == pygame.K_o or e.key == pygame.K_0:
                    self.player_ship.target_system = \
                        self.player_ship.planet_data
                    self.recenter_cursor()

        # draw objects 
        self.draw_cursor()
        self.draw_text()

        self.loop.iteration()

    def move_cursor(self, dx, dy):

        # Note: cursor_x and cursor_y are always in 0-255 range
        #  and cursor_rect.centerx and cursor_rect.centery are adjusted
        #  accordingly (multiplied by SCALE_W and SCALE_H

        if self.cursor_x + dx >= 0 and self.cursor_x + dx <= 255:
            self.cursor_x = self.cursor_x + dx

        if self.cursor_y + dy >= 0 and self.cursor_y + dy <= 255:
            self.cursor_y = self.cursor_y + dy 
        
        self.cursor_rect.centerx = (self.cursor_x * \
                define.GALACTIC_CHART_SCALE_W) + self.map_rect.x
        self.cursor_rect.centery = (self.cursor_y * \
                define.GALACTIC_CHART_SCALE_H) + self.map_rect.y

        self.parse_target()

        i = self.player_ship.target_system.number
        self.target_market = self.trade_database.get_market_by_index(i)
        
    def draw_cursor(self):

        self.surface_controller.flight_surface.blit(self.cursor, \
                (self.cursor_rect.x, self.cursor_rect.y))
    
    def clear_cursor(self):

        self.surface_controller.flight_surface.blit(self.surface_controller.flight_cover, \
                (self.cursor_rect.x, self.cursor_rect.y), self.cursor_rect)

    def draw_text(self):

        tga_generator.galactic_chart_update(self.tga, self.player_ship, 
                self.target_market)

        self.tga.draw(self.surface_controller.flight_surface)

    def clear_text(self):
       
        self.tga.clear(self.surface_controller.flight_surface, \
                self.surface_controller.flight_cover)

    def get_galactic_chart_surface(self):
        
        # larger surface to blit everything onto
        temp_surf = pygame.image.load('images/data.png').convert()

        # yellow square serves as outer border
        w = define.GALACTIC_CHART_SIZE_W + (define.BORDER * 2)
        h = define.GALACTIC_CHART_SIZE_H + (define.BORDER * 2)
        border = pygame.Surface((w,h))
        border.fill(define.YELLOW)

        # black square drawing surface
        background = \
                pygame.Surface(( \
                define.GALACTIC_CHART_SIZE_W,define.GALACTIC_CHART_SIZE_H))
        background.fill(define.BLACK)
        
        # individual stars
        new_occ = pygame.Surface((15,15))
        new_occ.fill(define.RED)
        mark = pygame.Surface((9,9))
        mark.fill(define.GREEN)
        b = pygame.Surface((7,7))
        b.fill(define.BLACK)
        star = pygame.Surface((3,3))
        star.fill(define.WHITE)
        for i in range(256):
            p = self.planet_database.get_planet_by_index(i)

            if p.num_thargoids > 0:
                if p.newly_occupied == True:
                    background.blit(new_occ, (p.galactic_chart_x-7, p.galactic_chart_y-7))
                background.blit(mark, (p.galactic_chart_x-4, p.galactic_chart_y-4))
                background.blit(b, (p.galactic_chart_x-3, p.galactic_chart_y-3))
            
            background.blit(star, (p.galactic_chart_x-1, p.galactic_chart_y-1))


        # blit starfield background onto yellow border
        border.blit(background, (define.BORDER,define.BORDER))
       
        # build chart_rect 
        w = define.GALACTIC_CHART_SIZE_W + (define.BORDER * 2)
        h = define.GALACTIC_CHART_SIZE_H + (define.BORDER * 2)

        # where to place galactic map on data screen? The following coordinates all 
        # correspond to the full data.png image that the chart is centered on.
        top = 50  # first pixel below the data-screen title-bar
        bottom = 593
        left = 0
        right = 791 
        data_midpoint_x = int((right - left)/2)         # midpoint = center of map
        data_midpoint_y = int((bottom - top)/2) + top   # area on data.png

        # chart by itself, find midpoint
        chart_midpoint_x = int(w/2)
        chart_midpoint_y = int(h/2)

        # chart_rect is the galactic map including the yellow border (x and y
        # are coordinates on data.png)
        chart_x = data_midpoint_x - chart_midpoint_x
        chart_y = data_midpoint_y - chart_midpoint_y
        chart_w = w
        chart_h = h
        chart_rect = pygame.Rect(chart_x, chart_y, chart_w, chart_h)
        
        # blit chart onto larger surface
        temp_surf.blit(border, chart_rect)

        self.tga = tga_generator.galactic_chart()
        self.tga.draw(temp_surf)

        # map_rect is the galactic map inside the yellow border. This will be
        # used later to draw a cursor and jump circle on the map.
        self.map_rect = pygame.Rect( \
                chart_rect.x + 4, \
                chart_rect.y + 4, \
                chart_rect.w - 8, \
                chart_rect.h - 8 )

        return temp_surf

    def rebuild_screen(self):

        self.surface.blit(self.static_background, (0,0))

        # draw current system (crosshair) 
        origin_rect = self.origin.get_rect()
        p = self.player_ship.planet_data 
        origin_rect.centerx = p.galactic_chart_x + self.map_rect.x
        origin_rect.centery = p.galactic_chart_y + self.map_rect.y

        # temporarily set clipping rectangle so objects don't extend over border
        self.surface.set_clip( self.map_rect )

        # draw origin crosshair
        self.surface.blit(self.origin, origin_rect)
      
        # draw current jump circle 
        if self.player_ship.fuel > 0:
            width = int(self.player_ship.fuel * 12.3)
            height = width / 2.0
            start_x = origin_rect.centerx - (width / 2)
            start_y = origin_rect.centery - (height / 2)
            rect = pygame.Rect(start_x, start_y, width, height)
            pygame.draw.ellipse(self.surface, define.SAND_BLUE, rect, 3)

        # remove clipping rect
        self.surface.set_clip()
    
        # update text 
        tga_generator.galactic_chart_update(self.tga, self.player_ship, \
                self.target_market)
        self.tga.draw(self.surface)

    def recenter_cursor(self):

        self.clear_cursor()

        self.cursor_x = self.player_ship.target_system.galactic_x
        self.cursor_y = self.player_ship.target_system.galactic_y

        self.parse_target()

        self.move_cursor(0,0)

    def parse_target(self):

        # This looks for a system near the cursor crosshair
        # Note: self.cursor_x and self.cursor_y are always within 0-255

        target = self.planet_database.get_nearest_planet( \
                self.cursor_x, self.cursor_y )
 
        if target != None:
            
            if self.player_ship.target_system.name != target.name:
            
                self.player_ship.change_target(target)




class WorldDataScreen():   # Screen 8 - Navigation Target Planet Info

    def __init__(self, object_controller, surface_controller, player_ship):

        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.planet             = player_ship.target_system

        self.tga = tga_generator.world_data_screen(self.planet, self.player_ship)
        self.surface = pygame.image.load('images/data.png').convert()
        
        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)
        
        self.tga.draw(self.surface) # now surface holds all static text
        
    def assume_focus(self):
       
        self.planet = self.player_ship.target_system
        self.tga = tga_generator.world_data_screen(self.planet, self.player_ship)
        pygame.key.set_repeat(0,0)

        self.screen_refresh()

    def loop_iteration(self, input_events):
       
        self.loop.iteration()

    def screen_refresh(self):

        self.tga = tga_generator.world_data_screen(self.planet, self.player_ship)
        self.surface = pygame.image.load('images/data.png').convert()
        self.tga.draw(self.surface) # now surface holds all static text

        self.surface_controller.change_surface( self.surface )





class MarketInfoScreen():  # Screen 9 - Navigation Target Market Info

    def __init__(self, object_controller, surface_controller, trade_database):

        # For performance reasons, a static copy of each market screen is kept
        # in a 256 entry array. The generation of the TGA is just too costly
        # to do on the fly. The array itself is filled on the fly, but once a
        # market screen is generated once in the game, it will always be 
        # available.
        
        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = object_controller.player_ship
        self.planet_data        = object_controller.planet_data
        self.trade_database     = trade_database
        
        self.static_background = pygame.image.load('images/data.png').convert()
        self.surface = None

        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)

    def assume_focus(self):
        
        self.set_market_data_surface()
        self.surface_controller.change_surface(self.surface) 
        pygame.key.set_repeat(0,0)

    def loop_iteration(self, input_events):

        self.loop.iteration()

    def set_market_data_surface(self):

        i = self.player_ship.target_system.number
        temp_market = self.trade_database.get_market_by_index(i)
        temp_tga = tga_generator.market_info(temp_market)
        self.surface = self.static_background 
        temp_tga.draw(self.surface)









####################

class CargoScreen():   # Screen 3 while flying, shows what is in cargo hold

    def __init__(self, object_controller, surface_controller, player_ship, \
            trade_database):

        self.trade_database     = trade_database
        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.player             = player_ship.pilot 

        i = self.player_ship.target_system.number
        self.market = self.trade_database.get_market_by_index(i)
        self.tga = tga_generator.cargo_screen(self.market, self.player_ship)
        self.surface = pygame.image.load('images/data.png').convert()
        
        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)
        
        self.tga.draw(self.surface) # now surface holds all static text

    def assume_focus(self):
       
        i = self.player_ship.target_system.number
        self.market = self.trade_database.get_market_by_index(i)
        self.tga = tga_generator.cargo_screen(self.market, self.player_ship)
        pygame.key.set_repeat(180,90)
        self.add_dynamic_text()

    def loop_iteration(self, input_events):
        
        self.loop.iteration()
       
        # process input
        if self.player_ship.graphics_state != objects.DISINTEGRATING:

            for e in input_events:

                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_LEFT:

                        # eject item? must have it in cargo hold
                        item = self.tga.cursor_row - 7
                        if self.player_ship.cargo.hold[item] > 0:
                            self.player_ship.cargo.remove_item(item)
                            tga_generator.cargo_screen_add_message(self.tga, \
                                    '    ITEM JETTISONED   ')
                        else:
                            tga_generator.cargo_screen_add_message(self.tga, \
                                    '    ITEM NOT IN CARGO HOLD    ')
                        self.add_dynamic_text()

                    if e.key == pygame.K_UP: 

                        tga_generator.cargo_screen_add_message(self.tga, '')
                        tga_generator.cargo_screen_move_cursor(self.tga, -1)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

                    if e.key == pygame.K_DOWN:

                        tga_generator.cargo_screen_add_message(self.tga, '')
                        tga_generator.cargo_screen_move_cursor(self.tga, 1)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 



    def add_dynamic_text(self):

        tga_generator.cargo_screen_data(self.tga, self.player_ship, \
                self.market)

        self.tga.draw(self.surface) # now surface holds all static text

        self.surface_controller.change_surface( self.surface )








class MainMenuScreen():

    NEW_GAME   = 27 
    SAVED_GAME = 29 
    CHANGE_RES = 31 
    CHANGE_FUL = 33 
    EXIT       = 35 

    def __init__(self, object_controller, surface_controller, player_ship, clock):

        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.pilot              = self.player_ship.pilot
        self.clock              = clock

        # surfaces
        self.surface_without_help = pygame.Surface((define.FLIGHT_W,define.FLIGHT_H))
        self.surface_without_help.fill(define.BLACK)
        self.surface_with_help = pygame.image.load('images/help.png').convert()

        self.tga = tga_generator.main_menu_screen(self.surface_controller)
        self.tga.cursor_row = MainMenuScreen.NEW_GAME

        self.surface = self.surface_without_help

        self.add_dynamic_text()
        
        self.request_new_game = False
        self.request_saved_game = False

        self.title_ship = TitleShip()
        self.draw_group = pygame.sprite.Group()
        self.draw_group.add(self.title_ship)

        self.showing_help = False

    def assume_focus(self):
      
        self.add_dynamic_text()
        pygame.key.set_repeat(180,90)

        self.showing_help = False
        
        if(flatland_engine.tutorial['WELCOME'] == False):
            i = 17 
            tga_generator.main_menu_screen_add_message_at(self.tga, 
                'Use UP and DOWN arrow keys', i+3, flatland_engine.tutorial_color)
            tga_generator.main_menu_screen_add_message_at(self.tga, 
                'to highlight menu item, then ENTER', i+5, flatland_engine.tutorial_color)
            flatland_engine.sound.play_sound_effect('SUCCESS')
            flatland_engine.tutorial['WELCOME'] = True

    def loop_iteration(self, input_events):

        for e in input_events:

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_UP: 
                   
                    if self.tga.cursor_row - 2 >= MainMenuScreen.NEW_GAME: 

                        tga_generator.main_menu_screen_move_cursor(self.tga, -2)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

                    else:
                        
                        tga_generator.main_menu_screen_move_cursor(self.tga, 8)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

                    self.add_dynamic_text()


                elif e.key == pygame.K_DOWN:
                    
                    if self.tga.cursor_row + 2 <= MainMenuScreen.EXIT:

                        tga_generator.main_menu_screen_move_cursor(self.tga, 2)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 
                    
                    else:
                        
                        tga_generator.main_menu_screen_move_cursor(self.tga, -8)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 
                    
                    self.add_dynamic_text()

                elif e.key == pygame.K_RETURN:
                    
                    if self.tga.cursor_row == MainMenuScreen.CHANGE_RES:
                        self.surface_controller.toggle_resolution()
                        self.add_dynamic_text()

                    elif self.tga.cursor_row == MainMenuScreen.CHANGE_FUL:
                        self.surface_controller.toggle_fullscreen()
                        self.add_dynamic_text()

                    elif self.tga.cursor_row == MainMenuScreen.EXIT:
                        self.clock.print_info()
                        sys.exit()

                    elif self.tga.cursor_row == MainMenuScreen.NEW_GAME:
                        self.request_new_game = True
                    
                    elif self.tga.cursor_row == MainMenuScreen.SAVED_GAME:
                        self.request_saved_game = True

                else:
                    
                    tga_generator.main_menu_clear_screen(self.tga)

                    self.surface = self.surface_with_help
                    
                    self.add_dynamic_text()

                    self.showing_help = True
            


        
        if self.showing_help == False:
        
            self.add_dynamic_text()

            self.draw_group.clear(self.surface_controller.flight_surface, \
                    self.surface_controller.flight_cover)
            
            self.title_ship.spin_right()

            self.draw_group.draw(self.surface_controller.flight_surface)

    def add_dynamic_text(self):

        tga_generator.main_menu_screen_data(self.tga, self.surface_controller)
        self.tga.draw(self.surface) 
        self.surface_controller.change_surface(self.surface)


class PauseMenuScreen():

    SAVE_GAME       = 27 
    RETURN_TO_GAME  = 29 
    CHANGE_RES      = 31 
    CHANGE_FUL      = 33 
    MAIN_MENU       = 35 

    def __init__(self, object_controller, surface_controller, player_ship,\
            planet_database, trade_database):

        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.pilot              = self.player_ship.pilot
        self.trade_database     = trade_database
        self.planet_database    = planet_database
        
        self.surface = pygame.image.load('images/help.png').convert()

        self.tga = tga_generator.pause_menu_screen(self.surface_controller)
        self.tga.print_centered(' GAME PAUSED ', 0, define.BLUE, \
                define.YELLOW, False)
        self.tga.cursor_row = PauseMenuScreen.SAVE_GAME
        
        self.add_dynamic_text()

        self.return_to_game = False
        self.return_to_main_menu = False

    def assume_focus(self):
        
        tga_generator.pause_menu_screen_clear_message(self.tga)
        
        self.tga.cursor_row = PauseMenuScreen.SAVE_GAME
        
        self.add_dynamic_text()

        pygame.key.set_repeat(180,90)

    def loop_iteration(self, input_events):

        for e in input_events:

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_UP: 

                    if self.tga.cursor_row - 2 >= PauseMenuScreen.SAVE_GAME: 

                        tga_generator.pause_menu_screen_move_cursor(self.tga, -2)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 
                    
                    else:
                        
                        tga_generator.pause_menu_screen_move_cursor(self.tga, 8)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

                elif e.key == pygame.K_DOWN:

                    if self.tga.cursor_row + 2 <= PauseMenuScreen.MAIN_MENU:

                        tga_generator.pause_menu_screen_move_cursor(self.tga, 2)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 
                    
                    else:
                        
                        tga_generator.pause_menu_screen_move_cursor(self.tga, -8)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 
                    
                elif e.key == pygame.K_RETURN:

                    if self.tga.cursor_row == PauseMenuScreen.SAVE_GAME:
                        if self.player_ship.state != define.DOCKED:
                            tga_generator.pause_menu_screen_add_message(self.tga, \
                                    'PLAYER SHIP MUST BE DOCKED TO SAVE')
                            self.add_dynamic_text()
                        elif self.player_ship.graphics_state == objects.GONE:
                            tga_generator.pause_menu_screen_add_message(self.tga, \
                                    'CANNOT SAVE AFTER GAME OVER')
                            self.add_dynamic_text()
                        else:
                            self.save_game()
                            self.return_to_game = True
                    
                    elif self.tga.cursor_row == PauseMenuScreen.RETURN_TO_GAME:
                        self.return_to_game = True 

                    elif self.tga.cursor_row == PauseMenuScreen.CHANGE_RES:
                        self.surface_controller.toggle_resolution()
                        self.add_dynamic_text()

                    elif self.tga.cursor_row == PauseMenuScreen.CHANGE_FUL:
                        self.surface_controller.toggle_fullscreen()
                        self.add_dynamic_text()

                    elif self.tga.cursor_row == PauseMenuScreen.MAIN_MENU:
                        self.return_to_main_menu = True 

                elif e.key == pygame.K_s:
                    self.return_to_game = True

                elif e.key == pygame.K_g:
                    self.return_to_game = True 

                elif e.key == pygame.K_r:
                    self.tga.cursor_row = PauseMenuScreen.CHANGE_RES
                    self.surface_controller.toggle_resolution()
                    self.add_dynamic_text()

                elif e.key == pygame.K_f:
                    self.tga.cursor_row = PauseMenuScreen.CHANGE_FUL
                    self.surface_controller.toggle_fullscreen()
                    self.add_dynamic_text()

                elif e.key == pygame.K_m:
                    self.return_to_main_menu = True 


    def add_dynamic_text(self):

        tga_generator.pause_menu_screen_data(self.tga, self.surface_controller)
        self.tga.draw(self.surface) 
        self.surface_controller.change_surface(self.surface)

    def save_game(self):

        try:

            output_file = open("files/savefile.bin", "wb")
            
            for i in self.planet_database.entry:
                pickle.dump(i.num_thargoids, output_file)
                pickle.dump(i.newly_occupied, output_file)
                pickle.dump(i.newly_liberated, output_file)
 
            pickle.dump(self.player_ship.planet_number, output_file)
            pickle.dump(self.player_ship.energy, output_file)
            pickle.dump(self.player_ship.fuel, output_file)
            for i in self.player_ship.equipment:
                pickle.dump(i, output_file)
            for i in self.player_ship.cargo.hold:
                pickle.dump(i, output_file)
            pickle.dump(self.player_ship.cargo.total, output_file)
            pickle.dump(self.player_ship.fore_shield, output_file)
            pickle.dump(self.player_ship.aft_shield, output_file)
            pickle.dump(self.player_ship.flagged_for_illegal_trading, output_file)
            pickle.dump(self.player_ship.flagged_for_increased_police, output_file)
            pickle.dump(self.player_ship.cargo.CARGO_HOLD_LIMIT, output_file)
            pickle.dump(self.player_ship.ENERGY_RECHARGE_RATE, output_file)
            pickle.dump(self.player_ship.fore_laser, output_file)
            pickle.dump(self.player_ship.aft_laser, output_file)
            pickle.dump(self.player_ship.port_laser, output_file)
            pickle.dump(self.player_ship.starboard_laser, output_file)
    
            pickle.dump(self.pilot.number_of_kills, output_file)
            pickle.dump(self.pilot.cash, output_file)
            pickle.dump(self.pilot.legal_status, output_file)
            pickle.dump(self.pilot.rating, output_file)
            pickle.dump(self.pilot.number_of_offenses, output_file)
       
            n = self.player_ship.planet_data.number
            m = self.trade_database.get_market_by_index(n)
            for i in m.prices:
                pickle.dump(i, output_file)
            for i in m.stock:
                pickle.dump(i, output_file)

            pickle.dump(self.player_ship.flagged_for_cleared_record, output_file)

            pickle.dump(flatland_engine.next_thargoid_invasion, output_file)
            pickle.dump(flatland_engine.next_liberation, output_file)
            pickle.dump(flatland_engine.thargoid_extinction, output_file)
            pickle.dump(flatland_engine.end_game_presented, output_file)

            output_file.close()

        except FileNotFoundError:

            tga_generator.pause_menu_screen_add_message(self.tga, \
                    'SAVE FILE COULD NOT BE CREATED')
            self.add_dynamic_text()



class TitleShip(pygame.sprite.Sprite):
 
    def __init__(self):
        
        pygame.sprite.Sprite.__init__(self) 

        self.image = pygame.image.load('images/title_ship.png').convert()
        self.image.set_colorkey(define.WHITE)
        self.original = self.image.copy()
        
        self.rect = self.image.get_rect()
        self.rect.centerx = (define.FLIGHT_W / 2)
        self.rect.centery = (define.FLIGHT_H / 2) - 55 
        
        self.orientation = random.randint(0,359) 

        # needed to track incremental changes to rect (it only has ints)
        # rotations will always use these floats to reposition sprite
        self.rect_float_x = float(self.rect.centerx)
        self.rect_float_y = float(self.rect.centery)
       
        # rotate image due to initial orientation
        self.image = pygame.transform.rotate(self.original, self.orientation)   
        self.rect = self.image.get_rect()
        self.rect.centerx = self.rect_float_x
        self.rect.centery = self.rect_float_y

        # ship specs
        self.turn_rate   = 1.9       

    def spin_right(self):

        self.orientation -= self.turn_rate

        if self.orientation < 0:
            self.orientation = self.orientation + 360 
        
        self.image = pygame.transform.rotate(self.original, self.orientation)   
        self.rect = self.image.get_rect()
        self.rect.centerx = self.rect_float_x
        self.rect.centery = self.rect_float_y


class EndGameScreen():

    SAVE_GAME            = 30 
    CONTINUE_PLAYING     = 32 
    MAIN_MENU            = 34 

    def __init__(self, object_controller, surface_controller, player_ship,\
            planet_database, trade_database):

        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.pilot              = self.player_ship.pilot
        self.planet_database    = planet_database
        self.trade_database     = trade_database
       
        temp = pygame.image.load('images/data.png').convert()
        photo = pygame.image.load('images/photo.png').convert()


        temp.blit(photo, (0,0))

        self.surface = temp.copy()
        self.surface_copy = self.surface.copy()
        
        self.surface_controller.change_surface(self.surface)

        self.tga = tga_generator.end_game_screen(self.surface_controller)
        self.tga.cursor_row = EndGameScreen.SAVE_GAME 
        self.add_dynamic_text()

        self.return_to_game = False
        self.return_to_main_menu = False
      
        
        row = 7 
        self.tga.print('                                              ', 2, \
                row-1, define.BLUE, define.BLUE, False)
        f = open('files/end_game_message.txt','r')
        for i in f:
            self.tga.print('                                              ', 2, \
                    row, define.BLUE, define.BLUE, False)
            self.tga.print_centered(i.strip(), row, define.YELLOW, define.BLUE, False)
            row += 1
        f.close()
        self.tga.print('                                              ', 2, \
                row, define.BLUE, define.BLUE, False)

        self.message_cleared = False

    def show_photo(self):
        
        temp = pygame.image.load('images/data.png').convert()
        photo = pygame.image.load('images/photo.png').convert()

        temp.blit(photo, (0,0))

        self.surface = temp.copy()
        self.surface_copy = self.surface.copy()
        
        self.surface_controller.change_surface(self.surface)

        self.tga = tga_generator.end_game_screen(self.surface_controller)
        self.tga.cursor_row = EndGameScreen.SAVE_GAME 
        self.add_dynamic_text()

        row = 22 
        self.tga.print('                                              ', 2, \
                row-1, define.BLUE, define.BLUE, False)
        f = open('files/end_game_message.txt','r')
        count = 0
        for i in f:
            count += 1
            if count > 15:
                self.tga.print('                                              ', 2, \
                        row, define.BLUE, define.BLUE, False)
                self.tga.print_centered(i.strip(), row, define.YELLOW, define.BLUE, False)
                row += 1
        f.close()
        self.tga.print('                                              ', 2, \
                row, define.BLUE, define.BLUE, False)


    
    def add_dynamic_text(self):

        self.tga.clear(self.surface, self.surface_copy)
        tga_generator.end_game_screen_data(self.tga, self.surface_controller)
        self.tga.draw(self.surface) 
        self.surface_controller.change_surface(self.surface)

    def assume_focus(self):
      
        flatland_engine.sound.play_music(0)
        self.add_dynamic_text()
        pygame.key.set_repeat(180,90)

    def loop_iteration(self, input_events):
       
        for e in input_events:

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_UP: 

                    if self.tga.cursor_row - 2 >= EndGameScreen.SAVE_GAME: 

                        if self.message_cleared != True:
                            self.message_cleared = True
                            self.show_photo()
                        self.surface_controller.change_surface(self.surface_copy)
                        tga_generator.end_game_screen_add_message(self.tga, '')
                        tga_generator.end_game_screen_move_cursor(self.tga, -2)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 
                    
                    else:
                        
                        if self.message_cleared != True:
                            self.message_cleared = True
                            self.show_photo()
                        self.surface_controller.change_surface(self.surface_copy)
                        tga_generator.end_game_screen_add_message(self.tga, '')
                        tga_generator.end_game_screen_move_cursor(self.tga, 4)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

                elif e.key == pygame.K_DOWN:

                    if self.tga.cursor_row + 2 <= EndGameScreen.MAIN_MENU:

                        if self.message_cleared != True:
                            self.message_cleared = True
                            self.show_photo()
                        self.surface_controller.change_surface(self.surface_copy)
                        tga_generator.end_game_screen_add_message(self.tga, '')
                        tga_generator.end_game_screen_move_cursor(self.tga, 2)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 
                    
                    else:
                        
                        if self.message_cleared != True:
                            self.message_cleared = True
                            self.show_photo()
                        self.surface_controller.change_surface(self.surface_copy)
                        tga_generator.end_game_screen_add_message(self.tga, '')
                        tga_generator.end_game_screen_move_cursor(self.tga, -4)
                        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
                        self.tga.draw(self.surface_controller.flight_surface) 

                elif e.key == pygame.K_RETURN:

                    if self.tga.cursor_row == EndGameScreen.SAVE_GAME:
                        if self.player_ship.state != define.DOCKED:
                            tga_generator.end_game_screen_add_message(self.tga, \
                                    'PLAYER SHIP MUST BE DOCKED TO SAVE')
                            self.add_dynamic_text()
                        elif self.player_ship.graphics_state == objects.GONE:
                            tga_generator.end_game_screen_add_message(self.tga, \
                                    'CANNOT SAVE AFTER GAME OVER')
                            self.add_dynamic_text()
                        else:
                            self.save_game()
                            self.return_to_game = True
                            #flatland_engine.sound.stop_music()
                    
                    elif self.tga.cursor_row == EndGameScreen.CONTINUE_PLAYING:
                        self.return_to_game = True 
                        #flatland_engine.sound.stop_music()

                    elif self.tga.cursor_row == EndGameScreen.MAIN_MENU:
                        self.return_to_main_menu = True 
                        #flatland_engine.sound.stop_music()

                elif e.key == pygame.K_s:
                    self.return_to_game = True

                elif e.key == pygame.K_g:
                    self.return_to_game = True 

                elif e.key == pygame.K_m:
                    self.return_to_main_menu = True 

    def save_game(self):

        try:

            output_file = open("files/savefile.bin", "wb")
 
            pickle.dump(self.player_ship.planet_number, output_file)
            pickle.dump(self.player_ship.energy, output_file)
            pickle.dump(self.player_ship.fuel, output_file)
            for i in self.player_ship.equipment:
                pickle.dump(i, output_file)
            for i in self.player_ship.cargo.hold:
                pickle.dump(i, output_file)
            pickle.dump(self.player_ship.cargo.total, output_file)
            pickle.dump(self.player_ship.fore_shield, output_file)
            pickle.dump(self.player_ship.aft_shield, output_file)
            pickle.dump(self.player_ship.flagged_for_illegal_trading, output_file)
            pickle.dump(self.player_ship.cargo.CARGO_HOLD_LIMIT, output_file)
            pickle.dump(self.player_ship.ENERGY_RECHARGE_RATE, output_file)
            pickle.dump(self.player_ship.fore_laser, output_file)
            pickle.dump(self.player_ship.aft_laser, output_file)
            pickle.dump(self.player_ship.port_laser, output_file)
            pickle.dump(self.player_ship.starboard_laser, output_file)
    
            pickle.dump(self.pilot.number_of_kills, output_file)
            pickle.dump(self.pilot.cash, output_file)
            pickle.dump(self.pilot.legal_status, output_file)
            pickle.dump(self.pilot.rating, output_file)
            pickle.dump(self.pilot.number_of_offenses, output_file)
       
            n = self.player_ship.planet_data.number
            m = self.trade_database.get_market_by_index(n)
            for i in m.prices:
                pickle.dump(i, output_file)
            for i in m.stock:
                pickle.dump(i, output_file)

            for i in self.planet_database.entry:
                pickle.dump(i.num_thargoids, output_file)
                pickle.dump(i.newly_occupied, output_file)
                pickle.dump(i.newly_liberated, output_file)
            
            pickle.dump(self.player_ship.flagged_for_cleared_record, output_file)

            pickle.dump(flatland_engine.next_thargoid_invasion, output_file)
            pickle.dump(flatland_engine.next_liberation, output_file)
            pickle.dump(flatland_engine.thargoid_extinction, output_file)

            output_file.close()

        except FileNotFoundError:

            tga_generator.end_game_screen_add_message(self.tga, \
                    'SAVE FILE COULD NOT BE CREATED')
            self.add_dynamic_text()





class EquipmentViewingScreen():   # Screen 3 IN-FLIGHT Ship Equipment and Upgrades

    def __init__(self, object_controller, surface_controller, player_ship):

        self.object_controller  = object_controller
        self.surface_controller = surface_controller
        self.player_ship        = player_ship
        self.player             = player_ship.pilot 
        self.planet             = player_ship.planet_data

        self.tga = tga_generator.equipment_viewing_screen(self.planet, self.player_ship)
        self.surface = pygame.image.load('images/data.png').convert()
        
        self.loop = OffScreenLoopHandler(object_controller, self.player_ship)
        
        self.tga.draw(self.surface) # now surface holds all static text
    
    def assume_focus(self):
       
        self.surface = pygame.image.load('images/data.png').convert()
        self.planet = self.player_ship.planet_data 
        self.tga = tga_generator.equipment_viewing_screen(self.planet, self.player_ship)
        self.add_dynamic_text()
        pygame.key.set_repeat(0,0)
         
        self.mode = REGULAR_MENU

    def loop_iteration(self, input_events):
       
        self.loop.iteration()

        # process input
        for e in input_events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.move_cursor(-1)
                elif e.key == pygame.K_DOWN:
                    self.move_cursor(1)
            
    def move_cursor(self, direction):

        tga_generator.equipment_viewing_screen_add_message(self.tga, \
                '                                              ')
        tga_generator.equipment_viewing_screen_move_cursor(self.tga, direction)
        self.tga.draw(self.surface_controller.flight_surface) 
        flatland_engine.sound.play_sound_effect('SELECTION_BAR')
    
    def add_dynamic_text(self):

        tga_generator.equipment_viewing_screen_data(self.tga, self.player_ship, \
                self.planet)

        self.tga.draw(self.surface) # now surface holds all static text

        self.surface_controller.change_surface( self.surface )
