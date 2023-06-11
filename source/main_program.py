# Author: Darron Vanaria
# Filesize: 30094 bytes
# LOC: 653

import pygame
import sys     # for sys.exit()
import pickle
import random
import math
import os

import define
import game_engine
import flatland_engine
import planet_database
import trade_database
import objects
import screens
import character_sheet
import tga_generator
import hud

# This part is specific for pyinstaller, as a step in compiling
# this python/pygame program into an .exe file
if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    basedir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    basedir = os.path.dirname(__file__)


game_engine.init()

# program control objects (these persist throughout entire game session)
clock               = game_engine.Clock(define.FRAMERATE)  
surface_controller  = flatland_engine.SurfaceController()
p_database          = planet_database.Database()
t_database          = trade_database.Database(p_database)
player_ship         = objects.PlayerShip(p_database)
object_controller   = objects.ObjectController(surface_controller, player_ship, p_database)
player              = character_sheet.Player(player_ship)


# initialize game part 1
player_ship.dock()
player_ship.install_pilot(player)
object_controller.build_draw_group()
flatland_engine.sound.play_sound_effect('GAME_START')


# screens
flight_screen          = screens.FlightScreen(object_controller, \
                             surface_controller, t_database, p_database)
market_screen          = screens.MarketInfoScreen(object_controller, \
                             surface_controller, t_database)
galactic_chart_screen  = screens.GalacticChartScreen(object_controller, \
                             surface_controller, p_database, t_database)
status_screen          = screens.StatusScreen(object_controller, \
                             surface_controller, player)
trading_screen         = screens.TradingScreen(object_controller, \
                             surface_controller, player_ship, t_database)
cargo_screen           = screens.CargoScreen(object_controller, \
                             surface_controller, player_ship, t_database)
equipment_screen       = screens.EquipmentPurchaseScreen(object_controller, \
                             surface_controller, player_ship)
world_data_screen      = screens.WorldDataScreen(object_controller, \
                             surface_controller, player_ship)
main_menu_screen       = screens.MainMenuScreen(object_controller, \
                             surface_controller, player_ship, clock)
pause_menu_screen      = screens.PauseMenuScreen(object_controller, \
                             surface_controller, player_ship, \
                             p_database, t_database)
end_game_screen        = screens.EndGameScreen(object_controller, \
                             surface_controller, player_ship, \
                             p_database, t_database)
ship_upgrades_screen   = screens.EquipmentViewingScreen(object_controller, \
                             surface_controller, player_ship)

def construct_game():

    global player_ship
    global object_controller
    global player
    global current_screen
    global state_machine
    global flight_screen
    global market_screen
    global galactic_chart_screen
    global status_screen
    global trading_screen
    global cargo_screen
    global equipment_screen
    global world_data_screen
    global main_menu_screen
    global pause_menu_screen
    global end_game_screen
    global ship_upgrades_screen

    surface_controller.clear_surfaces()

    player_ship.dock()
    player_ship.install_pilot(player)

    object_controller.populate_all_objects_group()
    object_controller.build_draw_group()

    flight_screen          = screens.FlightScreen(object_controller, \
                                 surface_controller, t_database, p_database)
    market_screen          = screens.MarketInfoScreen(object_controller, \
                                 surface_controller, t_database)
    galactic_chart_screen  = screens.GalacticChartScreen(object_controller, \
                                 surface_controller, p_database, \
                                 t_database)
    status_screen          = screens.StatusScreen(object_controller, \
                                 surface_controller, player)
    trading_screen         = screens.TradingScreen(object_controller, \
                                 surface_controller, player_ship, t_database)
    cargo_screen           = screens.CargoScreen(object_controller, \
                                 surface_controller, player_ship, t_database)
    equipment_screen       = screens.EquipmentPurchaseScreen(object_controller, \
                                 surface_controller, player_ship)
    world_data_screen      = screens.WorldDataScreen(object_controller, \
                                 surface_controller, player_ship)
    main_menu_screen       = screens.MainMenuScreen(object_controller, \
                                 surface_controller, player_ship, clock)
    pause_menu_screen      = screens.PauseMenuScreen(object_controller, \
                                 surface_controller, player_ship, \
                                 p_database, t_database)
    end_game_screen        = screens.EndGameScreen(object_controller, \
                                 surface_controller, player_ship, \
                                 p_database, t_database)
    ship_upgrades_screen   = screens.EquipmentViewingScreen(object_controller, \
                                 surface_controller, player_ship)
       
    player_ship.state = define.DOCKED
    
    current_screen = status_screen
    current_screen.assume_focus()
    state_machine = play_game

    pygame.display.update()



def load_saved_game():

    global player_ship
    global object_controller
    global player
    global p_database
    global t_database

    try:

        input_file = open("files/savefile.bin", "rb")

        flatland_engine.sound.play_sound_effect('GAME_START')
        tga_generator.main_menu_screen_add_message(main_menu_screen.tga, \
                'LOADING PREVIOUS GAME...')
        main_menu_screen.add_dynamic_text()
        pygame.display.update()
        
        for i in p_database.entry:
            i.num_thargoids = pickle.load(input_file)
            i.newly_occupied = pickle.load(input_file)
            i.newly_liberated = pickle.load(input_file)

        planet_number       = pickle.load(input_file)
        player_ship         = objects.PlayerShip(p_database, planet_number)
        object_controller   = objects.ObjectController(surface_controller, player_ship, p_database)
        player              = character_sheet.Player(player_ship)

        player_ship.energy = pickle.load(input_file)
        player_ship.fuel = pickle.load(input_file)

        for i in range(objects.NUM_EQUIPMENT_TYPES):
            player_ship.equipment[i] = pickle.load(input_file)
            
        for i in objects.COMMODITY_NAME:
            player_ship.cargo.hold[i] = pickle.load(input_file)

        player_ship.cargo.total = pickle.load(input_file)
        player_ship.fore_shield = pickle.load(input_file)
        player_ship.aft_shield = pickle.load(input_file)
        player_ship.flagged_for_illegal_trading = pickle.load(input_file)
        player_ship.flagged_for_increased_police = pickle.load(input_file)
        player_ship.cargo.CARGO_HOLD_LIMIT = pickle.load(input_file)
        player_ship.ENERGY_RECHARGE_RATE = pickle.load(input_file)
        player_ship.fore_laser = pickle.load(input_file)
        player_ship.aft_laser = pickle.load(input_file)
        player_ship.port_laser = pickle.load(input_file)
        player_ship.starboard_laser = pickle.load(input_file)

        player.number_of_kills = pickle.load(input_file)
        player.cash = pickle.load(input_file)
        player.legal_status = pickle.load(input_file)
        player.rating = pickle.load(input_file)
        player.number_of_offenses = pickle.load(input_file)
            
        p = []
        for i in objects.COMMODITY_NAME:
            p.append(pickle.load(input_file))
        t_database.update_price(planet_number, p)

        s = []
        for i in objects.COMMODITY_NAME:
            s.append(pickle.load(input_file))
        t_database.update_stock(planet_number, s)
            
        player_ship.flagged_for_cleared_record = pickle.load(input_file) 

        flatland_engine.next_thargoid_invasion = pickle.load(input_file)
        flatland_engine.next_liberation = pickle.load(input_file)
        flatland_engine.thargoid_extinction = pickle.load(input_file)
        flatland_engine.end_game_presented = pickle.load(input_file)

        input_file.close()

        construct_game()

    except FileNotFoundError:

        tga_generator.main_menu_screen_add_message(main_menu_screen.tga, \
                'SAVE FILE NOT AVAILABLE ')
        main_menu_screen.add_dynamic_text()
        pygame.display.update()


def game_over():
    
    global current_screen
    global state_machine
    global object_controller

    # start main loop timer (a test for framerate drops)
    clock.start_loop_timer()
    
    # collect all user input events 
    input_events = pygame.event.get()
    
    # process basic user input events (like screen changes)
    for e in input_events:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q or e.key == pygame.K_ESCAPE or \
                    e.key == pygame.K_p:
                current_screen = pause_menu_screen
                current_screen.assume_focus()
                state_machine = pause_menu
        elif e.type == pygame.QUIT:
            clock.print_info()
            sys.exit()

    input_events = []
    current_screen.loop_iteration(input_events)

    # update screen 
    pygame.display.update()
    
    # stop loop timer 
    clock.stop_loop_timer()

    # lock FPS
    clock.lock_framerate()


def play_game():

    global current_screen
    global state_machine
    global object_controller

    # start main loop timer (a test for framerate drops)
    clock.start_loop_timer()
    
    # collect all user input events 
    input_events = pygame.event.get()
    
    # process basic user input events (like screen changes)
    for e in input_events:

        if e.type == pygame.KEYDOWN:

            if e.key == pygame.K_q or e.key == pygame.K_ESCAPE or \
                    e.key == pygame.K_p:
                current_screen = pause_menu_screen
                current_screen.assume_focus()
                state_machine = pause_menu


            if e.key == pygame.K_F1 or e.key == pygame.K_1:
                if player_ship.state == define.DOCKED:
                    player_ship.state = define.LAUNCHING
                else:
                    if current_screen != flight_screen:
                        current_screen = flight_screen
                        current_screen.assume_focus()

            elif e.key == pygame.K_F3 or e.key == pygame.K_3:
                if player_ship.state == define.DOCKED:
                    current_screen = trading_screen
                    current_screen.assume_focus()
                elif current_screen != cargo_screen:
                    current_screen = cargo_screen
                    current_screen.assume_focus()
        
            elif e.key == pygame.K_F4 or e.key == pygame.K_4:
                if player_ship.state == define.DOCKED:
                    current_screen = equipment_screen
                    current_screen.assume_focus()
                elif current_screen != ship_upgrades_screen:
                    current_screen = ship_upgrades_screen
                    current_screen.assume_focus()
            
            elif e.key == pygame.K_F5 or e.key == pygame.K_5:
                if current_screen != status_screen:
                    current_screen = status_screen
                    current_screen.assume_focus()

            elif e.key == pygame.K_F7 or e.key == pygame.K_7:
                if current_screen != galactic_chart_screen:
                    current_screen = galactic_chart_screen
                    current_screen.assume_focus()
            
            elif e.key == pygame.K_SPACE and \
                    current_screen == galactic_chart_screen:
                current_screen.assume_focus()
            
            elif e.key == pygame.K_F8 or e.key == pygame.K_8:
                if current_screen != world_data_screen:
                    current_screen = world_data_screen
                    current_screen.assume_focus()
            
            elif e.key == pygame.K_F9 or e.key == pygame.K_9:
                if current_screen != market_screen:
                    current_screen = market_screen
                    current_screen.assume_focus()

            elif e.key == pygame.K_LEFTBRACKET:
                j = flatland_engine.sound.current_volume
                flatland_engine.sound.change_volume_sound_fx(j - 0.1)
            
            elif e.key == pygame.K_RIGHTBRACKET:
                j = flatland_engine.sound.current_volume
                flatland_engine.sound.change_volume_sound_fx(j + 0.1)

            elif e.key == pygame.K_h:
                current_screen = pause_menu_screen
                current_screen.assume_focus()
                state_machine = pause_menu

        elif e.type == pygame.QUIT:
            clock.print_info()
            sys.exit()

    # call current mode handler
    current_screen.loop_iteration(input_events)

    # update screen 
    pygame.display.update()
    
    # check for player docking
    if player_ship.state == define.DOCKING:

        if object_controller.docking_sequence >= 10:
            current_screen = status_screen
            current_screen.assume_focus()
            object_controller.docking_sequence = 0
            player_ship.dock()
            player_ship.state = define.DOCKED
        else:
            object_controller.docking_sequence += 1

    elif player_ship.state == define.LAUNCHING:
        
        current_screen = flight_screen
        current_screen.assume_focus()
        pick = random.choice(['UNDOCK','UNDOCK2','UNDOCK3'])
        flatland_engine.sound.play_sound_effect(pick)
        player_ship.launch()
        object_controller.hud.fuel.warning_on = False
        object_controller.hud.compass.blip_group.empty()
        object_controller.hud.compass.blip_group.add( \
                hud.CompassBlip(player_ship))
        if player_ship.flagged_for_illegal_trading == True:
            player_ship.pilot.increase_offense_count()
            player_ship.flagged_for_illegal_trading = False
        if player_ship.flagged_for_cleared_record == True:
            player_ship.add_hud_message('POLICE RECORD CLEARED', 15, \
                    define.PINK, False)
            player_ship.flagged_for_cleared_record = False

    elif player_ship.state == objects.GONE:
        current_screen = flight_screen
        current_screen.assume_focus()

    elif player_ship.state == define.ABANDONED:
        if object_controller.escape_capsule.successful_return == True:
            flatland_engine.sound.play_sound_effect('SUCCESS')
            player_ship.pilot.legal_status = define.CLEAN
            player_ship.escape_pod = None
            player_ship.pilot.number_of_offenses = 0
            player_ship.state = define.DOCKING
            player_ship.flagged_for_cleared_record = True 
            player_ship.cargo = objects.CargoContainer(player_ship)
            player_ship.flagged_for_illegal_trading = False
            player_ship.jump_countdown = player_ship.JUMP_RESET
            player_ship.jump_initiated = False
            player_ship.eject_sequence_on = False
            player_ship.eject_countdown = player_ship.EJECT_RESET
            object_controller.escape_capsule.kill()
            player_ship.equipment[objects.ESCAPE_CAPSULE] = 0
            player_ship.equipment[objects.FUEL] = player_ship.MAX_FUEL
            player_ship.energy = player_ship.MAX_ENERGY
            player_ship.fore_shield = player_ship.FORE_SHIELD_MAX 
            player_ship.aft_shield = player_ship.AFT_SHIELD_MAX 
            if player_ship.equipment[objects.LARGE_CARGO_BAY] == 1:
                player_ship.cargo.CARGO_HOLD_LIMIT = 35
            surface_controller.clear_surfaces()
            object_controller.hud.forced_update(surface_controller)
            current_screen = status_screen
            current_screen.assume_focus()
            pygame.display.update()
    
    if object_controller.game_over == True:
        state_machine = game_over
        current_screen = flight_screen
        current_screen.assume_focus()
 
    if flatland_engine.thargoid_extinction == False:

        # check for next thargoid invasion
        flatland_engine.next_thargoid_invasion -= 1
        if flatland_engine.next_thargoid_invasion <= 0:
            execute_invasion()
            flatland_engine.next_thargoid_invasion = \
                random.randint(define.COUNTDOWN_MIN, define.THARGOID_COUNTDOWN) 
        
        # check for next liberation 
        flatland_engine.next_liberation -= 1
        if flatland_engine.next_liberation <= 0:
            execute_liberation()
            flatland_engine.next_liberation = \
                random.randint(define.COUNTDOWN_MIN, define.LIBERTY_COUNTDOWN) 

        # update random thargoid "voices" counter
        if player_ship.planet_data.num_thargoids > 0:
            flatland_engine.thargoid_voice -= 1
            if flatland_engine.thargoid_voice <= 0:
                flatland_engine.thargoid_voice = 30 * random.randint(5, 20)
                pick = random.choice(['VOICE_1','VOICE_2','VOICE_3','VOICE_4', \
                        'VOICE_5','VOICE_6','VOICE_7','VOICE_8','VOICE_9'])
                flatland_engine.sound.play_sound_effect(pick)
   
    # handle jump
    if player_ship.jump_initiated == True:

        if player_ship.jump_countdown <= 0:

            player_ship.jump_initiated = False

            if player_ship.jump_systems() == True:
            
                pick = random.choice(['JUMP_1', 'JUMP_2', 'JUMP_3', \
                        'JUMP_4', 'JUMP_5'])
                flatland_engine.sound.play_sound_effect(pick)

                current_screen = flight_screen

                flight_screen.rebuild_screen()
                pygame.display.update()

                for i in range(90):

                    r1 = surface_controller.flight_surface.get_rect()
                    x = r1.centerx
                    y = r1.centery

                    temp_image = pygame.transform.rotate(flight_screen.surface, i*2)
                    temp_image.set_colorkey(define.BLACK)

                    r2 = temp_image.get_rect()
                    new_x = r2.centerx
                    new_y = r2.centery

                    offset_x = x - new_x
                    offset_y = y - new_y

                    surface_controller.flight_surface.blit(temp_image,\
                            (offset_x, offset_y))
                    pygame.display.update()

                m = player_ship.planet_data.number
                t_database.rebuild_market(m)  # new prices!
                object_controller.repopulate_system()  # new objects!
                for i in player_ship.message_queue:
                    i.timer = 1
                flight_screen.rebuild_screen()
                flight_screen.tga.clear(surface_controller.flight_surface, \
                        surface_controller.flight_cover)
                flight_screen.tga.empty_container()
                m = 'Arrived in ' + player_ship.planet_data.name + \
                        ' system'
                player_ship.add_hud_message(m.upper(), 17, define.BLUE)

                if player_ship.planet_data.num_thargoids > 0:
                    player_ship.add_hud_message( \
                    'THARGOID OCCUPIED SYSTEM', 20, \
                            define.PINK, False)
                elif player_ship.flagged_for_increased_police == True:
                    player_ship.add_hud_message( \
                    'INCREASED POLICE PRESENCE DETECTED', 20, \
                            define.PINK, False)

                object_controller.build_draw_group()
                pygame.display.update()

                object_controller.reward_given = False;

            else:
                
                player_ship.add_hud_message('JUMP FAILED', 17, define.BLUE)

        else:
            
            tga_generator.hud_jump_count(flight_screen.tga, player_ship)

        pygame.display.update()

    # check for end game
    if flatland_engine.thargoid_extinction == True and \
            flatland_engine.end_game_presented == False:
        player_wins_game()

    # check for encouragement
    if player_ship.pilot.number_of_kills % 256 == 255:

        if player_ship.pilot.right_on_commander == False:

            player_ship.pilot.right_on_commander = True
            player_ship.add_hud_message('RIGHT ON COMMANDER!', 17, define.CYAN)

    else:

        player_ship.pilot.right_on_commander = False

    # stop loop timer 
    clock.stop_loop_timer()

    # lock FPS
    clock.lock_framerate()

def player_wins_game():

    global current_screen
    global state_machine

    current_screen = end_game_screen
    current_screen.assume_focus()
    state_machine = end_game_pause

    player.cash += 1000000
    
    flatland_engine.end_game_presented = True

def main_menu():

    global current_screen
    global state_machine
    global player_ship
    global object_controller
    global player
    global p_database
    global t_database

    # start main loop timer (a test for framerate drops)
    clock.start_loop_timer()
    
    # collect all user input events 
    input_events = pygame.event.get()
    
    # process basic user input events 
    for e in input_events:
        if e.type == pygame.QUIT:
            clock.print_info()
            sys.exit()

    # call current mode handler
    current_screen.loop_iteration(input_events)

    # update screen 
    pygame.display.update()
    
    # check for game ready to play
    if current_screen.request_new_game == True:
        
        #reset all tutorials since this is a new game
        for key in flatland_engine.tutorial:
            flatland_engine.tutorial[key] = False 

        tga_generator.main_menu_screen_add_message(main_menu_screen.tga, \
                '  CREATING NEW GAME...  ')
        
        flatland_engine.next_thargoid_invasion = \
            random.randint(define.COUNTDOWN_MIN, define.THARGOID_COUNTDOWN) 
        flatland_engine.next_liberation = \
            random.randint(define.COUNTDOWN_MIN, define.LIBERTY_COUNTDOWN) 

        flatland_engine.thargoid_extinction = False

        main_menu_screen.add_dynamic_text()
        pygame.display.update()

        current_screen.request_new_game = False

        p_database          = planet_database.Database()
        t_database          = trade_database.Database(p_database)
        player_ship         = objects.PlayerShip(p_database)
        object_controller   = objects.ObjectController(surface_controller, player_ship, p_database)
        player              = character_sheet.Player(player_ship)

        flatland_engine.sound.play_sound_effect('GAME_START')

        construct_game()
    

    elif current_screen.request_saved_game == True:
        
        #remove all tutorials since this is an existing game
        for key in flatland_engine.tutorial:
            flatland_engine.tutorial[key] = True

        current_screen.request_saved_game = False
        load_saved_game()

    # stop loop timer 
    clock.stop_loop_timer()

    # lock FPS
    clock.lock_framerate()


def pause_menu():

    global current_screen
    global state_machine

    # start main loop timer (a test for framerate drops)
    clock.start_loop_timer()
    
    # collect all user input events 
    input_events = pygame.event.get()
    
    # process basic user input events 
    for e in input_events:
        if e.type == pygame.QUIT:
            clock.print_info()
            sys.exit()

    # call current mode handler
    current_screen.loop_iteration(input_events)

    # update screen 
    pygame.display.update()
   
    # check for return to game
    if current_screen.return_to_game == True:
        if player_ship.state == define.DOCKED:
            current_screen.return_to_game = False
            current_screen = status_screen
            current_screen.assume_focus()
            state_machine = play_game 
        else:
            current_screen.return_to_game = False
            current_screen = flight_screen
            current_screen.assume_focus()
            state_machine = play_game 
    elif current_screen.return_to_main_menu == True:
        current_screen.return_to_main_menu = False
        current_screen = main_menu_screen
        current_screen.assume_focus()
        state_machine = main_menu 

    # stop loop timer 
    clock.stop_loop_timer()

    # lock FPS
    clock.lock_framerate()


def end_game_pause():

    global current_screen
    global state_machine
       
    # start main loop timer (a test for framerate drops)
    clock.start_loop_timer()
    
    # collect all user input events 
    input_events = pygame.event.get()
    
    # process basic user input events 
    for e in input_events:
        if e.type == pygame.QUIT:
            clock.print_info()
            sys.exit()

    # call current mode handler
    current_screen.loop_iteration(input_events)

    # update screen 
    pygame.display.update()
   
    # check for return to game
    if current_screen.return_to_game == True:
        if player_ship.state == define.DOCKED:
            current_screen.return_to_game = False
            current_screen = status_screen
            current_screen.assume_focus()
            state_machine = play_game 
        else:
            current_screen.return_to_game = False
            current_screen = flight_screen
            current_screen.assume_focus()
            state_machine = play_game 
    elif current_screen.return_to_main_menu == True:
        current_screen.return_to_main_menu = False
        current_screen = main_menu_screen
        current_screen.assume_focus()
        state_machine = main_menu 

    # stop loop timer 
    clock.stop_loop_timer()

    # lock FPS
    clock.lock_framerate()


def execute_invasion():
    
    global current_screen
    global state_machine

    # pick a currently invaded system, then find next closest UNOCCUPIED
    # system to invade.

    # this is also where to check for win-game or end-game

    occupied_list = []
    free_list = []

    for i in p_database.entry:
        if i.num_thargoids > 0:
            occupied_list.append(i)
        else:
            free_list.append(i)

    if len(occupied_list) == 0 and flatland_engine.thargoid_extinction == False:

        player_wins_game()

    else:

        r = random.choice(occupied_list)
        min_distance = 99999
        target = None
        for i in free_list:
            a = i.galactic_chart_x - r.galactic_chart_x 
            b = i.galactic_chart_y - r.galactic_chart_y 
            c = math.sqrt((a*a) + (b*b))
            if c < min_distance:
                min_distance = c
                target = i

        if target != None and target != player_ship.planet_data:

            target.num_thargoids = random.randint(3,23)

            s = random.choice(['INVASION', 'INVASION2'])
            flatland_engine.sound.play_sound_effect(s)

            m = 'thargoids have invaded ' + target.name + '!'
            player_ship.add_hud_message(m.upper(), 18, define.GREEN, False) 

            for j in p_database.entry:
                if j.newly_occupied == True:
                    j.newly_occupied = False
                if j.newly_liberated == True:
                    j.newly_liberated = False

            target.newly_occupied = True
            
            galactic_chart_screen.static_background = \
                    galactic_chart_screen.get_galactic_chart_surface()
            galactic_chart_screen.surface = \
                    galactic_chart_screen.static_background.copy() 
            galactic_chart_screen.rebuild_screen()

            if current_screen == galactic_chart_screen:
                current_screen.assume_focus()
            
            tga_generator.galactic_chart_special_message( \
                    galactic_chart_screen.tga, p_database)


def execute_liberation():

    global current_screen
    global state_machine

    occupied_list = []
    free_list = []

    for i in p_database.entry:
        if i.num_thargoids > 0 and \
                i != player_ship.planet_data:   # don't auto-liberate current system
            occupied_list.append(i)
        else:
            free_list.append(i)

    if len(occupied_list) > 1:  # player MUST defeat last infected system

        r = random.choice(occupied_list)

        r.num_thargoids = 0
        r.newly_occupied = False
        r.newly_liberated = True

        flatland_engine.sound.play_sound_effect('LIBERTY')

        m = r.name + ' system has been liberated!'
        player_ship.add_hud_message(m.upper(), 18, define.CYAN, False) 

        galactic_chart_screen.static_background = \
                galactic_chart_screen.get_galactic_chart_surface()
        galactic_chart_screen.surface = \
                galactic_chart_screen.static_background.copy() 
        galactic_chart_screen.rebuild_screen()

        if current_screen == galactic_chart_screen:
            current_screen.assume_focus()
        
        tga_generator.galactic_chart_special_message( \
                galactic_chart_screen.tga, p_database)



# initialize game part 2
current_screen = main_menu_screen
current_screen.assume_focus()
state_machine = main_menu

surface_controller.toggle_fullscreen()


while(True):

    state_machine()
