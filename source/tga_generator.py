# Author: Darron Vanaria
# Filesize: 52300 bytes
# LOC: 1079

import sys
import pygame
import math

import game_engine
import define
import objects
import trade_database
import planet_database
import flatland_engine

gov_name = []
gov_name.append('Anarchy')
gov_name.append('Feudal')
gov_name.append('Multi-Government')
gov_name.append('Dictatorship')
gov_name.append('Communist')
gov_name.append('Confederacy')
gov_name.append('Democracy')
gov_name.append('Corporate State')

eco_name = []
eco_name.append('Rich Industrial')
eco_name.append('Average Industrial')
eco_name.append('Poor Industrial')
eco_name.append('Mainly Industrial')
eco_name.append('Mainly Agricultural')
eco_name.append('Rich Agricultural')
eco_name.append('Average Agricultural')
eco_name.append('Poor Agricultural')

def galactic_chart():

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)

    tga.print_centered('NAVIGATION: SET HYPERDRIVE TARGET', \
            1, define.WHITE, define.BLACK, False)
    
    x = 4 
    y = 4 
    c1 = define.WHITE
    c2 = define.RED
    tga.print('     U ', \
            x,y, define.CYAN, define.BLACK, False)
    tga.print('Use LDR to move cursor (Hyperdrive Target) ', \
            x,y+1, define.CYAN, define.BLACK, False)
    tga.add_char_by_index(define.CHAR_UP, x+5, y, c1, c2, False)
    tga.add_char_by_index(define.CHAR_DOWN, x+5, y+1, c1, c2, False)
    tga.add_char_by_index(define.CHAR_LEFT, x+4, y+1, c1, c2, False)
    tga.add_char_by_index(define.CHAR_RIGHT, x+6, y+1, c1, c2, False)

    tga.print('Press SPACE to center cursor on nearest star', \
            x-1,y+3, define.CYAN, define.BLACK, False)
    tga.add_char('S', x+5, y+3, c1, c2, False)
    tga.add_char('P', x+6, y+3, c1, c2, False)
    tga.add_char('A', x+7, y+3, c1, c2, False)
    tga.add_char('C', x+8, y+3, c1, c2, False)
    tga.add_char('E', x+9, y+3, c1, c2, False)

    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[7]'        
    tga.print(s, 35, 35, define.YELLOW, define.BLACK, False)
    
    return tga

def galactic_chart_special_message(tga, planet_database):
   
    row = 34 

    for i in planet_database.entry:
        if i.newly_occupied == True:
            m = 'thargoids have invaded ' + i.name + '!'
            tga.print_centered('          ' + m.upper() + '          ', \
                    row, define.GREEN, define.BLACK, False)
        if i.newly_liberated == True:
            m = i.name + ' system has been liberated!'
            tga.print_centered('          ' + m.upper() + '          ', \
                    row, define.CYAN, define.BLACK, False)

def galactic_chart_update(tga, player_ship, market):
           
    tga.print("                                                   ", \
            26, 9, define.BLACK, define.BLACK, False)
    tga.print("                                                   ", \
            26, 10, define.BLACK, define.BLACK, False)

    tga.print('   CURRENT SYSTEM: ', \
            7,9, define.WHITE, define.BLACK, False)
    tga.print(player_ship.planet_data.name, \
            26,9, define.BLUE, define.BLACK, False)

    tga.print('JUMP TARGET SYSTEM: ', \
            6,10, define.WHITE, define.BLACK, False)
    tga.print(player_ship.target_system.name, \
            26,10, define.CYAN, define.BLACK, False)
    
    d = player_ship.jump_distance()
    f = player_ship.fuel
    tga.print('    JUMP DISTANCE: ', \
            7, 29, define.WHITE, define.BLACK)
    if f > d:
        tga.print(str(round(d, 1)) + ' Light Years       ', \
            26, 29, define.CYAN, define.BLACK)
    else:
        tga.print('OUT OF RANGE            ', \
            26, 29, define.RED, define.BLACK)

    g = player_ship.target_system.government
    tga.print('TARGET GOVERNMENT: ', \
            7,30, define.WHITE, define.BLACK, False)
    if player_ship.target_system.num_thargoids > 0:
        m = 'Thargoid Occupied (' + \
                str(player_ship.target_system.num_thargoids-3) + ')  '
        tga.print(m, 26, 30, define.RED, define.BLACK, False)
    else:
        tga.print(gov_name[g] + '                     ', \
                26,30, define.CYAN, define.BLACK, False)

    if market != None:    
        tga.print('     CHIEF IMPORT: ', \
                7,31, define.WHITE, define.BLACK, False)
        tga.print(market.chief_import, \
                26,31, define.CYAN, define.BLACK, False)
    
    if market != None:    
        tga.print('       TECH LEVEL: ', \
                7,32, define.WHITE, define.BLACK, False)
        tga.print(str(player_ship.target_system.tech_level) + '  ', \
                26,32, define.CYAN, define.BLACK, False)
    
    g = player_ship.target_system.economy
    tga.print('   TARGET ECONOMY: ', \
            7,33, define.WHITE, define.BLACK, False)
    tga.print(eco_name[g] + '                     ', \
            26,33, define.CYAN, define.BLACK, False)
    
def market_info(market):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)

    string_list = market.string_list()

    row = 0
    for i in string_list:

        if 'IMPORT' in i:
            tga.print(i + '                ', 1, row, define.CYAN, define.BLACK, False)

        elif 'EXPORT' in i:
            tga.print(i + '                ', 1, row, define.MAGENTA, define.BLACK, False)

        elif 'UNIT' in i:
            tga.print(i + '                ', 1, row, define.GREEN, define.BLACK, False)

        elif ('Thargoid' in i) or ('do not apply' in i) or \
                ('Illegal' in i) or ('system (' in i):
            tga.print(i + '                        ', 1, row, define.GREEN, define.BLACK, False)

        elif ('punishable' in i) or ('system!' in i):
            tga.print(i + '                ', 1, row, define.RED, define.BLACK, False)

        else:
            tga.print(i, 1, row, define.WHITE, define.BLACK, False)

        row += 1

    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[9]'        
    tga.print(s, 43, 35, define.YELLOW, define.BLACK, False)

    return tga

def test_screen(w,h):

    tga = game_engine.TextGridArray(w,h)

    tga.print("012345678901234567890123456789012345678901234567890", \
            0, 0, define.WHITE, define.BLACK, True)
    tga.print("          1         2         3         4         5", \
            0, 1, define.WHITE, define.BLACK, True)

    # fill screen with numbers
    for i in range(tga.GRID_HEIGHT):
        tga.print("012345678901234567890123456789012345678901234567890", \
                0, i+2, define.WHITE, define.BLACK, True)

    # print numbers along left edge, to count rows
    for i in range(60):
        tga.print(str(i), 0, i, define.RED, define.BLUE, False)

    return tga 

def hud_jump_count(tga, player_ship):

    count = str(int(player_ship.jump_countdown/10))
    point_a = player_ship.planet_data.name.upper()
    point_b = player_ship.target_system.name.upper()

    tga.print_centered('     JUMPING FROM ' + point_a + ' TO ' + point_b + ' IN ' + \
            count + ' SECONDS     ', \
            17, define.CYAN, define.BLACK, True)

def hud_eject_count(tga, player_ship):

    count = str(int(player_ship.eject_countdown/10))

    tga.print_centered('ESCAPE CAPSULE EJECTING IN ' + count + ' SECONDS', \
            19, define.CYAN, define.BLACK, True)
    
    tga.print_centered('(PRESS \'Z\' TO ABORT)', \
            21, define.ORANGE, define.BLACK, True)

def hud_eject_clear(tga, player_ship):

    count = str(int(player_ship.eject_countdown/10))

    tga.print_centered('                                                  ', \
            19, define.BLUE, define.BLACK, True)
    
    tga.print_centered('                                                  ', \
            21, define.BLACK, define.BLACK, True)

def hud_message(tga, m):

    tga.print_centered('                    ' + m.string + \
                       '                    ', m.location, m.color, define.BLACK, True)
        
def hud_message_clear(tga, m):

    tga.print_centered("                                                ", \
                   m.location, define.BLACK, define.BLACK, True)
    
def hud_info_update(tga, player_ship):

    if player_ship.state != define.ABANDONED:
    
        tga.print("                                                   ", \
                0, 0, define.BLACK, define.BLACK, True)
        tga.print("                                                   ", \
                0, 1, define.BLACK, define.BLACK, True)

        tga.print('CURRENT SYSTEM: ', 1, 2, define.WHITE, define.BLACK, True)
        g = gov_name[player_ship.target_system.government]
        m =  player_ship.planet_data.name.upper() + ' (' + g + ')'
        tga.print(m, 17, 2, define.YELLOW, define.BLACK, True)

        if player_ship.planet_data.name != player_ship.target_system.name:
            tga.print('HYPERSPACE TARGET: ', \
                    1,1, define.WHITE, define.BLACK, True)
            tga.print(player_ship.target_system.name.upper() + ' (Press J to Jump)', \
                    20,1, define.YELLOW, define.BLACK, True)
        else:
            tga.print('HYPERSPACE TARGET: ', \
                    1,1, define.WHITE, define.BLACK, True)
            tga.print('NO TARGET SELECTED (Press 5)', \
                    20,1, define.RED, define.BLACK, True)
       
        tga.print('LEGAL STATUS: ', 1, 35, define.WHITE, define.BLACK, True)
        if player_ship.pilot.legal_status == define.CLEAN:
            tga.print('CLEAN          ', \
                    15,35, define.GREEN, define.BLACK, True)
        elif player_ship.pilot.legal_status == define.OFFENDER:
            tga.print('OFFENDER       ', \
                    15,35, define.YELLOW, define.BLACK, True)
        else:
            tga.print('FUGITIVE       ', \
                    15,35, define.RED, define.BLACK, True)

        tga.print('ECM: ', \
                1,33, define.WHITE, define.BLACK, True)
        if player_ship.equipment[objects.ECM_SYSTEM] > 0:
            tga.print(str(player_ship.equipment[objects.ECM_SYSTEM]) + \
                ' (Press E)', \
                    6,33, define.YELLOW, define.BLACK, True)
        else:
            tga.print('0                        ', 6,33, define.RED, define.BLACK, True)

        tga.print('BOMBS: ', \
                1,34, define.WHITE, define.BLACK, True)
        if player_ship.equipment[objects.ENERGY_BOMB] > 0:
            tga.print(str(player_ship.equipment[objects.ENERGY_BOMB]) + \
                ' (Press TAB)', \
                    8,34, define.YELLOW, define.BLACK, True)
        else:
            tga.print('0                        ', 8,34, define.RED, define.BLACK, True)
   
    else:
        
        tga.print("                                                   ", \
                0, 0, define.BLACK, define.BLACK, True)
        tga.print("                                                   ", \
                0, 1, define.BLACK, define.BLACK, True)

        m =  player_ship.planet_data.name
        s = '      ESCAPE CAPSULE EN ROUTE TO ' + m + ' STATION      '
        tga.print_centered(s.upper(), 2, define.CYAN, define.BLACK, True)

        a = player_ship.escape_pod.global_x - player_ship.planet_data.station_x
        b = player_ship.escape_pod.global_y - player_ship.planet_data.station_y
        c = math.sqrt((a*a) + (b*b))

        s = '                                                                '
        tga.print_centered(s.upper(), 33, define.BLACK, define.BLACK, True)

        s = '            DISTANCE TO STATION: ' + str(int(c)) + '            '
        tga.print_centered(s.upper(), 34, define.CYAN, define.BLACK, True)
        
        s = '                                                                '
        tga.print_centered(s.upper(), 35, define.BLACK, define.BLACK, True)

def hud_info(player_ship):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)
 
    hud_info_update(tga, player_ship)
    
    return tga

def status_screen_update(tga, player):
 
    label_color = define.WHITE
    data_color = define.GREEN
   
    start = 0

    tga.print('PILOT INFORMATION', \
            1, start+4, label_color, define.BLACK, False)

    tga.print('Name:', \
            3, start+6, label_color, define.BLACK, False)
    tga.print('Commander Jameson', \
            9, start+6, data_color, define.BLACK, False)
    
    tga.print('Account: ', \
            3, start+7, label_color, define.BLACK, False)
    m = round(player.cash,2)
    tga.print(int_with_commas(m) + ' Cr                  ', \
            12, start+7, data_color, define.BLACK, False)

    tga.print('Legal Status: ', \
            3, start+8, label_color, define.BLACK, False)
    strikes = player.number_of_offenses
    if strikes == 0:
        tga.print(player.get_legal_status_string() + \
                '                                       ', \
                17, start+8, data_color, define.BLACK, False)
    elif strikes == 1:
        tga.print(player.get_legal_status_string() + ' (' + str(strikes) + \
                ' strike total)', \
                17, start+8, data_color, define.BLACK, False)
    else:
        tga.print(player.get_legal_status_string() + ' (' + str(strikes) + \
                ' strikes total)', \
                17, start+8, data_color, define.BLACK, False)

    tga.print('Number of Kills: ', \
            3, start+9, label_color, define.BLACK, False)
    tga.print(str(player.number_of_kills), \
            20, start+9, data_color, define.BLACK, False)

    tga.print('Rating: ', \
            3, start+10, label_color, define.BLACK, False)
    cr = player.get_next_combat_rating()
    if cr == 1:
        tga.print(player.get_combat_rating_string() + \
                ' (' + str(cr) + \
                ' more kill needed)             ', \
                11, start+10, data_color, define.BLACK, False)
    else:
        tga.print(player.get_combat_rating_string() + \
                ' (' + str(cr) + \
                ' more kills needed)             ', \
                11, start+10, data_color, define.BLACK, False)

    start = 12

    tga.print('SHIP INFORMATION', \
            1, start, label_color, define.BLACK, False)
    
    tga.print('Present System: ', \
            3, start+2, label_color, define.BLACK, False)
    tga.print(player.current_ship.planet_data.name + '                  ', \
            19, start+2, data_color, define.BLACK, False)

    tga.print('Condition: ', \
            3, start+3, label_color, define.BLACK, False)
    tga.print(player.get_condition_string() + '                 ', \
            14, start+3, data_color, define.BLACK, False)

    tga.print('Fuel: ', \
            3, start+4, label_color, define.BLACK, False)
    tga.print(str(round(player.current_ship.fuel, 1))+ ' Light Years        ', \
            9, start+4, data_color, define.BLACK, False)
   
    tga.print('Targeted Hyperspace System: ', \
            3, start+5, label_color, define.BLACK, False)
    if player.current_ship.target_system.name == player.current_ship.planet_data.name:
        tga.print('None                                    ', \
                31, start+5, data_color, define.BLACK, False)
    else:
        j = round(player.current_ship.jump_distance(), 1)
        tga.print(player.current_ship.target_system.name + ' (' + \
                str(j) + ' ly)                 ', \
                31, start+5, data_color, define.BLACK, False)

    tga.print('Equipment: ', \
            3, start+6, label_color, define.BLACK, False)

    list_row = start+6
    item_counter = 1
    for i in range(objects.NUM_EQUIPMENT_TYPES - 1):
        if player.current_ship.equipment[i+1] > 0:
            s = planet_database.equipment_name[i+1]
            tga.print(s, 14, list_row, data_color, define.BLACK, False)
            list_row += 1
            item_counter += 1
        if item_counter <= 1:
            s = 'No Upgrades Installed'
            tga.print(s, 14, list_row, data_color, define.BLACK, False)
    
    if player.current_ship.flagged_for_cleared_record == True:
        tga.print_centered('   *** IMPORTANT NOTICE! ***   ', \
                30, define.ORANGE, define.BLACK, False)
        tga.print_centered('SHIP REINSTATED AS PER INSURANCE POLICY', \
                31, define.PINK, define.BLACK, False)
        tga.print_centered('ALL CARGO LOST', \
                32, define.PINK, define.BLACK, False)
        tga.print_centered('YOUR POLICE RECORD HAS BEEN CLEARED', \
                33, define.PINK, define.BLACK, False)
    
    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[5]'        
    tga.print(s, 30, 35, define.YELLOW, define.BLACK, False)

def status_screen(player):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)

    tga.print_centered('PILOT & SHIP INFORMATION', \
            1, define.WHITE, define.BLACK, False)
        
    status_screen_update(tga, player)
    

    return tga

def direct_message(tga, string, row, color):

    tga.print_centered(string, row, color, define.BLACK, True)

def trading_screen(market, player_ship):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)
    economy = player_ship.planet_data.economy
    price_diffs = market.price_diff(market.prices, economy)

    title = '    COMMODITY TRADING AT ' + \
      market.planet.name + ' MARKET    '

    tga.print_centered(title.upper(), \
            1, define.WHITE, define.BLACK, False)

    tga.print('                    PRICE   AVERAGE  IN     ON ', \
            0, 4, define.WHITE, define.BLACK, True)

    tga.print('  PRODUCT    UNIT   HERE    PRICE    STOCK  SHIP ', \
            0, 5, define.WHITE, define.BLACK, True)

    for i in objects.COMMODITY_NAME:
        tga.print(' ' + objects.COMMODITY_NAME[i] + '                 ', \
                1, 7+i, define.WHITE, define.BLACK)
        tga.print(trade_database.unit_name[i] + '                  ', \
                15, 7+i, define.WHITE, define.BLACK)
        s = str(round(market.prices[i], 2))
        tga.print(s.rjust(5) + '             ', \
                19, 7+i, define.WHITE, define.BLACK)

        s = ''
        if price_diffs[i] > 0:
            s = '+' + str(round(price_diffs[i], 1)) + '             '
        elif price_diffs[i] < 0:
            s = str(round(price_diffs[i], 1)) + '             '
        else:
            s = ' ' + str(round(price_diffs[i], 1)) + '             '
        tga.print(s.rjust(17), 29, 7+i, define.WHITE, define.BLACK)

        tga.print('       ', \
                41, 7+i, define.WHITE, define.BLACK)
    
    x = 11
    y = 25 
    c1 = define.WHITE
    c2 = define.RED
    tga.print('Use U and D to select item', \
            x,y, define.CYAN, define.BLACK, False)
    tga.add_char_by_index(define.CHAR_UP, x+4, y, c1, c2, False)
    tga.add_char_by_index(define.CHAR_DOWN, x+10, y, c1, c2, False)

    tga.print('    Use L to sell             Use R to buy   ', \
           x-10,y+2, define.CYAN, define.BLACK, False)
    tga.add_char_by_index(define.CHAR_LEFT, x-2, y+2, c1, c2, False)
    tga.add_char_by_index(define.CHAR_RIGHT, x+24, y+2, c1, c2, False)
    
    tga.print('       Bank Account:                 ', \
            0, 31, define.GREEN, define.BLACK)
    
    tga.print('         Cargo Hold:                 ', \
            0, 33, define.GREEN, define.BLACK)
    
    tga.min_cursor_row = 7
    tga.max_cursor_row = 23
    tga.cursor_row = tga.min_cursor_row 
    
    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[3]'        
    tga.print(s, 22, 35, define.YELLOW, define.BLACK, False)

    return tga
        
def trading_screen_move_cursor(tga, direction):

    d = 0 

    current_row = tga.cursor_row
    next_row = current_row + direction
    if next_row < tga.min_cursor_row:
        d += (tga.max_cursor_row - tga.min_cursor_row)
    elif next_row > tga.max_cursor_row:
        d -= (tga.max_cursor_row - tga.min_cursor_row)
    else:
        d = direction
    
    tga.highlight_row(tga.cursor_row, define.BLACK)
    tga.move_cursor(d) 
    tga.highlight_row(tga.cursor_row, define.RED)

def trading_screen_add_message(tga, message, color=define.RED):

    tga.print_centered('                                           ',\
            29, define.BLACK, define.BLACK)

    tga.print_centered(message, 29, color, define.BLACK)

def trading_screen_data(tga, player_ship, market):

    for i in objects.COMMODITY_NAME:
        tga.print('  ' + str(round(market.stock[i], 2)).rjust(2) + '  ', \
                36, 7+i, define.WHITE, define.BLACK)
        if player_ship.cargo.hold[i] > 0:
            tga.print(str(player_ship.cargo.hold[i]) + ' ', \
                    45, 7+i, define.YELLOW, define.BLACK)
        else:
            tga.print(str(player_ship.cargo.hold[i]), \
                    45, 7+i, define.GRAY, define.BLACK)

    m = round(player_ship.pilot.cash,2)
    tga.print(int_with_commas(m) + \
            ' Cr   ', 22, 31, define.GREEN, define.BLACK)
   
    tga.print(str(player_ship.cargo.total) + \
            ' items (capacity ' + \
            str(player_ship.cargo.CARGO_HOLD_LIMIT) + \
            ')       ', 22, 33, define.GREEN, define.BLACK)
    
    tga.highlight_row(tga.cursor_row, define.RED)

def cargo_screen(market, player_ship):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)
    economy = player_ship.planet_data.economy
    price_diffs = market.price_diff(market.prices, economy)

    title = '      Cargo Manifest and Jettison Control      '

    tga.print_centered(title.upper(), \
            1, define.WHITE, define.BLACK, False)

    tga.print('                                             ON ', \
            0, 4, define.WHITE, define.BLACK, True)

    tga.print('  PRODUCT    UNIT                           SHIP ', \
            0, 5, define.WHITE, define.BLACK, True)

    for i in objects.COMMODITY_NAME:
        tga.print(' ' + objects.COMMODITY_NAME[i] + '                 ', \
                1, 7+i, define.WHITE, define.BLACK)
        tga.print(trade_database.unit_name[i] + '                  ', \
                15, 7+i, define.WHITE, define.BLACK)
        tga.print('                    ', \
                28, 7+i, define.WHITE, define.BLACK)

    x = 11
    y = 25 
    c1 = define.WHITE
    c2 = define.RED
    tga.print('Use U and D to select item', \
            x,y, define.CYAN, define.BLACK, False)
    tga.add_char_by_index(define.CHAR_UP, x+4, y, c1, c2, False)
    tga.add_char_by_index(define.CHAR_DOWN, x+10, y, c1, c2, False)

    tga.print('  Use L to jettison item', \
           x,y+2, define.CYAN, define.BLACK, False)
    tga.add_char_by_index(define.CHAR_LEFT, x+6, y+2, c1, c2, False)
    
    tga.min_cursor_row = 7
    tga.max_cursor_row = 23
    tga.cursor_row = tga.min_cursor_row 
    
    tga.print('       Bank Account:                 ', \
            0, 31, define.GREEN, define.BLACK)
    
    tga.print('         Cargo Hold:                 ', \
            0, 33, define.GREEN, define.BLACK)
    
    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[3]'        
    tga.print(s, 22, 35, define.YELLOW, define.BLACK, False)

    return tga
        
def cargo_screen_move_cursor(tga, direction):

    tga.highlight_row(tga.cursor_row, define.BLACK)
    tga.move_cursor(direction) 
    tga.highlight_row(tga.cursor_row, define.RED)

def cargo_screen_add_message(tga, message):

    tga.print_centered('                                           ',\
            29, define.BLACK, define.BLACK)

    tga.print_centered(message, 29, define.RED, define.BLACK)

def cargo_screen_data(tga, player_ship, market):

    for i in objects.COMMODITY_NAME:
        
        if player_ship.cargo.hold[i] > 0:
            tga.print(str(player_ship.cargo.hold[i]) + ' ', \
                    45, 7+i, define.YELLOW, define.BLACK)
        else:
            tga.print(str(player_ship.cargo.hold[i]), \
                    45, 7+i, define.GRAY, define.BLACK)

    m = round(player_ship.pilot.cash,2)
    tga.print(int_with_commas(m) + \
            ' Cr   ', 22, 31, define.GREEN, define.BLACK)
   
    tga.print(str(player_ship.cargo.total) + \
            ' items (capacity ' + \
            str(player_ship.cargo.CARGO_HOLD_LIMIT) + \
            ')       ', 22, 33, define.GREEN, define.BLACK)
    
    tga.highlight_row(tga.cursor_row, define.RED)

    if player_ship.cargo.hold[3] > 0 or \
       player_ship.cargo.hold[6] > 0 or \
       player_ship.cargo.hold[10] > 0: 

       tga.print_centered('  * WARNING: ILLEGAL ITEMS ON BOARD *  ', \
                29, define.RED, define.BLACK, False)

    else:
       
       tga.print_centered('                                       ', \
                29, define.RED, define.BLACK, False)

def equipment_purchase_screen(planet, player_ship):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)

    title = 'SHIP EQUIPMENT & UPGRADES AT ' + planet.name + ' STATION'

    tga.print_centered(title.upper(), \
            1, define.WHITE, define.BLACK, False)

    tga.print('                                       INSTALLED     ', \
            0, 5, define.WHITE, define.BLACK, True)  
    tga.print('   ITEM                       PRICE     ON SHIP      ', \
            0, 5, define.WHITE, define.BLACK, True)

    item_number = 0
    for i in planet.equipment:
        name = i[0]
        price = i[1]
        tga.print(' ' + name + '               ', \
                2, 7+item_number, define.WHITE, define.BLACK)

        pad = ''
        if price < 10:
            pad = '    ' 
        elif price < 100:
            pad = '   ' 
        elif price < 1000:
            pad = '  '
        elif price < 10000:
            pad = ' '

        if item_number == 0:
            tga.print(pad + str(round(price, 1)) + '  ', \
                    28, 7+item_number, define.WHITE, define.BLACK)
        else:
            tga.print(pad + str(round(price, 1)) + '     ', \
                    28, 7+item_number, define.WHITE, define.BLACK)

        item_number += 1
    
    x = 11
    y = 21 
    c1 = define.WHITE
    c2 = define.RED
    tga.print('Use U and D to select item', \
            x,y, define.CYAN, define.BLACK, False)
    tga.add_char_by_index(define.CHAR_UP, x+4, y, c1, c2, False)
    tga.add_char_by_index(define.CHAR_DOWN, x+10, y, c1, c2, False)

    tga.print('    Use L to sell             Use R to buy   ', \
           x-10,y+2, define.CYAN, define.BLACK, False)
    tga.add_char_by_index(define.CHAR_LEFT, x-2, y+2, c1, c2, False)
    tga.add_char_by_index(define.CHAR_RIGHT, x+24, y+2, c1, c2, False)

    tga.print('           Bank Account:                 ', \
            0, 28, define.GREEN, define.BLACK)
    
    tga.print('    FORWARD LASER:                   ', \
            6, 30, define.WHITE, define.BLACK)
    tga.print('       PORT LASER:                   ', \
            6, 31, define.WHITE, define.BLACK)
    tga.print('        AFT LASER:                   ', \
            6, 32, define.WHITE, define.BLACK)
    tga.print('  STARBOARD LASER:                   ', \
            6, 33, define.WHITE, define.BLACK)

    tga.min_cursor_row = 7
    tga.max_cursor_row = len(planet.equipment) + 6
    tga.cursor_row = tga.min_cursor_row 
    
    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[4]'        
    tga.print(s, 26, 35, define.YELLOW, define.BLACK, False)

    return tga
        
def equipment_purchase_screen_move_cursor(tga, direction):

    tga.highlight_row(tga.cursor_row, define.BLACK)
    tga.move_cursor(direction) 
    tga.highlight_row(tga.cursor_row, define.RED)

def equipment_purchase_screen_add_message(tga, message, color=define.RED):

    tga.print_centered('                                              ',\
            26, define.BLACK, define.BLACK)

    tga.print_centered(message, 26, color, define.BLACK)

def equipment_purchase_screen_data(tga, player_ship, planet):

    for i in range(len(planet.equipment)):

        if i == 0:  # fuel, show actual level
            f = round(player_ship.fuel,1)
            if f >= 10:
                b = ' '
            else:
                b = '  '
            tga.print(b + str(f) + ' ', \
                    41, 7+i, define.YELLOW, define.BLACK)
        elif i == 1:  # missiles, show number installed
            n = player_ship.equipment[objects.MISSILE]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.ECM_SYSTEM:
            n = player_ship.equipment[objects.ECM_SYSTEM]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.ENERGY_BOMB:
            n = player_ship.equipment[objects.ENERGY_BOMB]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.PULSE_LASER:
            n = player_ship.equipment[objects.PULSE_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.BEAM_LASER:
            n = player_ship.equipment[objects.BEAM_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.MINING_LASER:
            n = player_ship.equipment[objects.MINING_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.MILITARY_LASER:
            n = player_ship.equipment[objects.MILITARY_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        else:
            if player_ship.equipment[i] > 0:
                tga.print('  YES ', \
                        41, 7+i, define.YELLOW, define.BLACK)
            else:
                tga.print('   NO ', \
                        41, 7+i, define.GRAY, define.BLACK)

    m = round(player_ship.pilot.cash,2)
    tga.print(int_with_commas(m) + \
            ' Cr               ', 26, 28, define.GREEN, define.BLACK)
   
    
    if player_ship.fore_laser != None:
        tga.print('             ', 26, 30, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.fore_laser],\
                26, 30, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 30, define.GRAY, define.BLACK)

    if player_ship.port_laser != None:
        tga.print('             ', 26, 31, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.port_laser],\
                26, 31, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 31, define.GRAY, define.BLACK)
   
    if player_ship.aft_laser != None:
        tga.print('             ', 26, 32, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.aft_laser],\
                26, 32, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 32, define.GRAY, define.BLACK)

    if player_ship.starboard_laser != None:
        tga.print('             ', 26, 33, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.starboard_laser],\
                26, 33, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 33, define.GRAY, define.BLACK)

    tga.highlight_row(tga.cursor_row, define.RED)

def world_data_screen(planet, player_ship):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)

    title = '   NAVIGATION: TARGET PLANET INFO (' + planet.name + ')   '
    tga.print_centered(title.upper(), \
            1, define.WHITE, define.BLACK, False)

    data = player_ship.target_system.get_data()

    data_items = len(data)

    d = player_ship.jump_distance()
    # d = d / player_ship.FUEL_SCALE
    tga.print('Distance: ', 2, 4, define.WHITE, define.BLACK)
    tga.print(str(round(d, 1)) + ' Light Years       ', 12, 4, define.GREEN, define.BLACK)
    tga.print('Economy: ', 2, 6, define.WHITE, define.BLACK)
    tga.print(data[0], 11, 6, define.GREEN, define.BLACK)
    
    tga.print('Government: ', 2, 8, define.WHITE, define.BLACK)
    if player_ship.target_system.num_thargoids > 0:
        m = 'Thargoid Occupied (' + \
                str(planet.num_thargoids - 3) + ')'
        tga.print(m.upper(), 14, 8, define.RED, define.BLACK)
    else:
        tga.print(data[1], 14, 8, define.GREEN, define.BLACK)

    tga.print('Tech Level: ', 2, 10, define.WHITE, define.BLACK)
    tga.print(data[2], 14, 10, define.GREEN, define.BLACK)

    tga.print('Population: ', 2, 12, define.WHITE, define.BLACK)
    tga.print(data[3], 14, 12, define.GREEN, define.BLACK)
    tga.print('Gross Productivity: ', 2, 14, define.WHITE, define.BLACK)
    tga.print(data[4], 22, 14, define.GREEN, define.BLACK)
    tga.print('Average Radius: ', 2, 16, define.WHITE, define.BLACK)
    tga.print(data[5], 18, 16, define.GREEN, define.BLACK)
    tga.print('Description: ', 2, 18, define.WHITE, define.BLACK)
    tga.print(data[6], 15, 18, define.GREEN, define.BLACK)

    if data_items > 6:
        sublist = data[7:]
        index = 19
        for i in sublist:
            tga.print('             ' + i + '             ', 2, \
                    index, define.GREEN, define.BLACK)
            index += 1
    
    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[8]'        
    tga.print(s, 39, 35, define.YELLOW, define.BLACK, False)

    return tga

def main_menu_screen(surface):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)
   
    # title
    tga.print_centered("---- E L I T E   F L A T L A N D ----", \
            1, define.WHITE, define.BLACK, True)
    
    tga.print("(ESC for Help)", \
            35,36, define.YELLOW, define.BLACK, True)

    main_menu_screen_data(tga, surface)

    return tga

def main_menu_clear_screen(tga):
    tga.empty_container()

def main_menu_screen_move_cursor(tga, direction):

    tga.highlight_row(tga.cursor_row, define.BLACK)
    tga.move_cursor(direction) 
    tga.highlight_row(tga.cursor_row, define.RED)

def main_menu_screen_add_message(tga, message):

    tga.print_centered('                                                   ',\
            12, define.BLACK, define.BLACK)
    tga.print_centered('                                                   ',\
            13, define.BLACK, define.BLACK)
    tga.print_centered('                                                   ',\
            14, define.BLACK, define.BLACK)
    
    tga.print_centered(message, 13, define.CYAN, define.BLACK)

def main_menu_screen_add_message_at(tga, message, row, color):

    tga.print_centered('                                                   ',\
            row, define.BLACK, define.BLACK)
    
    tga.print_centered(message, row, color, define.BLACK)

def main_menu_screen_data(tga, surface):

    i = 27
                    
    infoObject = pygame.display.Info()
    w = infoObject.current_w
    h = infoObject.current_h

    # first load TGA with consistently spaced bars (for highlight bar)
    tga.print_centered('                                      ', \
            i, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+2, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+4, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+6, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+8, define.BLACK, define.BLACK, False)
    
    # second, load TGA with menu items 
    tga.print_centered('Create New Commander', \
            i, define.WHITE, define.BLACK, False)
    tga.print_centered('Load Saved Game', \
            i+2, define.WHITE, define.BLACK, False)
    tga.print_centered('Change Resolution (now: ' + str(w) + ' x ' + str(h) + \
            ')', i+4, define.WHITE, define.BLACK, False)
    if surface.controller.fullscreen == False:
        tga.print_centered('Toggle Fullscreen (now: Window Mode)', \
                i+6, define.WHITE, define.BLACK, False)
    else: 
        tga.print_centered('Toggle Fullscreen (now: Fullscreen)', \
                i+6, define.WHITE, define.BLACK, False)
    tga.print_centered('Exit Program', \
            i+8, define.WHITE, define.BLACK, False)
    tga.highlight_row(tga.cursor_row, define.RED)

def pause_menu_screen(surface):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)
   
    pause_menu_screen_data(tga, surface)

    return tga

def pause_menu_screen_move_cursor(tga, direction):

    tga.highlight_row(tga.cursor_row, define.BLACK)
    tga.move_cursor(direction) 
    tga.highlight_row(tga.cursor_row, define.RED)

def pause_menu_screen_add_message(tga, message):

    tga.print_centered('                                                   ',\
            12, define.BLACK, define.BLACK)
    tga.print_centered('                                                   ',\
            13, define.BLACK, define.BLACK)
    tga.print_centered('                                                   ',\
            14, define.BLACK, define.BLACK)
    
    tga.print_centered(message, 13, define.CYAN, define.BLACK)

def pause_menu_screen_clear_message(tga):

    for i in tga.text_group:
        if i.r > 11 and i.r < 15:
            i.kill() 
    
def pause_menu_screen_data(tga, surface):

    i = 27
                    
    infoObject = pygame.display.Info()
    w = infoObject.current_w
    h = infoObject.current_h

    # first load TGA with consistently spaced bars (for highlight bar)
    tga.print_centered('                                      ', \
            i, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+2, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+4, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+6, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+8, define.BLACK, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+10, define.BLACK, define.BLACK, False)

    # second, load TGA with menu items 
    tga.print_centered('Save Game', \
            i, define.WHITE, define.BLACK, False)
    tga.print_centered('Return To Game', \
            i+2, define.WHITE, define.BLACK, False)
    tga.print_centered('Change Resolution (now: ' + str(w) + ' x ' + str(h) + \
            ')', i+4, define.WHITE, define.BLACK, False)
    if surface.controller.fullscreen == False:
        tga.print_centered('Toggle Fullscreen (now: Window Mode)', \
                i+6, define.WHITE, define.BLACK, False)
    else: 
        tga.print_centered('Toggle Fullscreen (now: Fullscreen)', \
                i+6, define.WHITE, define.BLACK, False)
    tga.print_centered('Main Menu (WITHOUT SAVE)', \
            i+8, define.WHITE, define.BLACK, False)
    tga.print_centered('                                      ', \
            i+10, define.WHITE, define.BLACK, False)
    
    tga.highlight_row(tga.cursor_row, define.RED)

def int_with_commas(x):

    if x < 0:

        return '-' + int_with_commas(-x)

    result = ''

    while x >= 1000:

        x, r = divmod(x, 1000)

        result = ",%03d%s" % (r, result)

    return "%d%s" % (x, result)

def end_game_screen(surface):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)
   
    end_game_screen_data(tga, surface)

    return tga

def end_game_screen_move_cursor(tga, direction):

    tga.unhighlight_row(tga.cursor_row, define.BLUE)
    tga.move_cursor(direction) 
    tga.highlight_row(tga.cursor_row, define.BLUE)

def end_game_screen_add_message(tga, message):

    tga.print_centered(message, 15, define.CYAN, define.BLACK, True)

def end_game_screen_data(tga, surface):

    i = 30 

    # first load TGA with consistently spaced bars (for highlight bar)
    tga.print_centered('                                      ', \
            i, define.BLACK, define.BLACK, True)
    tga.print_centered('                                      ', \
            i+2, define.BLACK, define.BLACK, True)
    tga.print_centered('                                      ', \
            i+4, define.BLACK, define.BLACK, True)

    # second, load TGA with menu items 
    tga.print_centered('Save Game', \
            i, define.YELLOW, define.BLUE, True)
    tga.print_centered('Continue Playing', \
            i+2, define.YELLOW, define.BLUE, True)
    tga.print_centered('Main Menu', i+4, define.YELLOW, define.BLUE, True)
    
    tga.highlight_row(tga.cursor_row, define.BLUE)

def help_info(tga=None):

    # columns (x): 1 - 48 inclusive
    # rows (y): 3 - 36 inclusive

    if tga == None:
        tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)

    c = 2 # left-justified
    r = 1 # top-row
    
    tga.add_file_contents_at('files/help.txt', r, c, \
            define.CYAN, define.BLUE, False)

    c1 = define.WHITE
    c2 = define.RED
    
    tga.add_char_by_index(1, 10, 2, c1, c2, False)
    tga.add_char_by_index(3, 12, 2, c1, c2, False)

    tga.add_char('E', 40, 2, c1, c2, False)
    tga.add_char('N', 41, 2, c1, c2, False)
    tga.add_char('T', 42, 2, c1, c2, False)
    tga.add_char('E', 43, 2, c1, c2, False)
    tga.add_char('R', 44, 2, c1, c2, False)

    tga.add_char('1', 13, 4, c1, c2, False)

    tga.add_char('3', 13, 6, c1, c2, False)
    tga.add_char('4', 13, 7, c1, c2, False)
    tga.add_char('5', 13, 8, c1, c2, False)

    tga.add_char('7', 13, 10, c1, c2, False)
    tga.add_char('8', 13, 11, c1, c2, False)
    tga.add_char('9', 13, 12, c1, c2, False)

    tga.add_char_by_index(4, 14, 14, c1, c2, False)
    tga.add_char_by_index(2, 16, 14, c1, c2, False)

    tga.add_char_by_index(1, 44, 14, c1, c2, False)
    tga.add_char_by_index(3, 46, 14, c1, c2, False)

    tga.add_char('W', 11, 16, c1, c2, False)
    tga.add_char('A', 13, 16, c1, c2, False)
    tga.add_char('S', 15, 16, c1, c2, False)
    tga.add_char('D', 17, 16, c1, c2, False)

    tga.add_char('T', 19, 17, c1, c2, False)
    tga.add_char('U', 21, 17, c1, c2, False)
    tga.add_char('M', 23, 17, c1, c2, False)
    
    tga.add_char('E', 32, 18, c1, c2, False)
    
    tga.add_char('T', 16, 19, c1, c2, False)
    tga.add_char('A', 17, 19, c1, c2, False)
    tga.add_char('B', 18, 19, c1, c2, False)
    
    tga.add_char('J', 14, 21, c1, c2, False)
    tga.add_char('I', 46, 21, c1, c2, False)
    
    tga.add_char('X', 19, 23, c1, c2, False)
    tga.add_char('Z', 21, 23, c1, c2, False)
    
    tga.add_char('E', 27, 25, c1, c2, False)
    tga.add_char('S', 28, 25, c1, c2, False)
    tga.add_char('C', 29, 25, c1, c2, False)

    return tga 

def equipment_viewing_screen(planet, player_ship):

    tga = game_engine.TextGridArray(define.TEXT_GRID_W, define.TEXT_GRID_H)

    title = '         SHIP EQUIPMENT & UPGRADES         '

    tga.print_centered(title.upper(), \
            1, define.WHITE, define.BLACK, False)

    tga.print('                                       INSTALLED     ', \
            0, 5, define.WHITE, define.BLACK, True)  
    tga.print('   ITEM                                 ON SHIP      ', \
            0, 5, define.WHITE, define.BLACK, True)

    item_number = 0

    for i in planet.equipment:

        name = i[0]

        tga.print(' ' + name + '               ', \
                2, 7+item_number, define.WHITE, define.BLACK)

        item_number += 1
    
    tga.print('           Bank Account:                 ', \
            0, 28, define.GREEN, define.BLACK)
    
    tga.print('    FORWARD LASER:                   ', \
            6, 30, define.WHITE, define.BLACK)
    tga.print('       PORT LASER:                   ', \
            6, 31, define.WHITE, define.BLACK)
    tga.print('        AFT LASER:                   ', \
            6, 32, define.WHITE, define.BLACK)
    tga.print('  STARBOARD LASER:                   ', \
            6, 33, define.WHITE, define.BLACK)

    tga.min_cursor_row = 7
    tga.max_cursor_row = len(planet.equipment) + 6
    tga.cursor_row = tga.min_cursor_row 
    
    s = ' Current View:  [1]  [3] [4] [5]  [7] [8] [9]'        
    tga.print(s, 1, 35, define.BLUE, define.BLACK, False)
    s = ' Current View:'        
    tga.print(s, 1, 35, define.YELLOW, define.BLACK, False)
    
    s = '[4]'        
    tga.print(s, 26, 35, define.YELLOW, define.BLACK, False)

    return tga
        
def equipment_viewing_screen_move_cursor(tga, direction):

    tga.highlight_row(tga.cursor_row, define.BLACK)
    tga.move_cursor(direction) 
    tga.highlight_row(tga.cursor_row, define.RED)

def equipment_viewing_screen_add_message(tga, message):

    tga.print_centered('                                              ',\
            22, define.BLACK, define.BLACK)

    tga.print_centered(message, 22, define.RED, define.BLACK)

def equipment_viewing_screen_data(tga, player_ship, planet):

    for i in range(len(planet.equipment)):

        if i == 0:  # fuel, show actual level
            f = round(player_ship.fuel,1)
            if f >= 10:
                b = ' '
            else:
                b = '  '
            tga.print(b + str(f) + ' ', \
                    41, 7+i, define.YELLOW, define.BLACK)
        elif i == 1:  # missiles, show number installed
            n = player_ship.equipment[objects.MISSILE]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.ECM_SYSTEM:
            n = player_ship.equipment[objects.ECM_SYSTEM]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.ENERGY_BOMB:
            n = player_ship.equipment[objects.ENERGY_BOMB]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.PULSE_LASER:
            n = player_ship.equipment[objects.PULSE_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.BEAM_LASER:
            n = player_ship.equipment[objects.BEAM_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.MINING_LASER:
            n = player_ship.equipment[objects.MINING_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        elif i == objects.MILITARY_LASER:
            n = player_ship.equipment[objects.MILITARY_LASER]
            if n == 0:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.GRAY, define.BLACK)
            else:
                tga.print('    ' + str(n) + ' ', \
                        41, 7+i, define.YELLOW, define.BLACK)
        else:
            if player_ship.equipment[i] > 0:
                tga.print('  YES ', \
                        41, 7+i, define.YELLOW, define.BLACK)
            else:
                tga.print('   NO ', \
                        41, 7+i, define.GRAY, define.BLACK)

    m = round(player_ship.pilot.cash,2)
    tga.print(int_with_commas(m) + \
            ' Cr               ', 26, 28, define.GREEN, define.BLACK)
    
    if player_ship.fore_laser != None:
        tga.print('             ', 26, 30, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.fore_laser],\
                26, 30, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 30, define.GRAY, define.BLACK)

    if player_ship.port_laser != None:
        tga.print('             ', 26, 31, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.port_laser],\
                26, 31, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 31, define.GRAY, define.BLACK)
   
    if player_ship.aft_laser != None:
        tga.print('             ', 26, 32, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.aft_laser],\
                26, 32, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 32, define.GRAY, define.BLACK)

    if player_ship.starboard_laser != None:
        tga.print('             ', 26, 33, define.BLACK, define.BLACK)
        tga.print(define.LASER_NAME[player_ship.starboard_laser],\
                26, 33, define.YELLOW, define.BLACK)
    else:
        tga.print('Not Installed    ', 26, 33, define.GRAY, define.BLACK)

    tga.highlight_row(tga.cursor_row, define.RED)
