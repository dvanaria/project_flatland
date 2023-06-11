# Author: Darron Vanaria
# Filesize: 14902 bytes
# LOC: 369

import sys    # for sys.stdout.flush()
import math
import random

import game_engine
import define
import trade_database

class Database():

    def __init__(self):

        self.entry = []

        self.initialize_planet_database()

        self.add_addtional_info_to_database()

    def get_planet_by_index(self, index):

        # retrieve planet from database via index number 0 - 255

        return self.entry[index]

    def get_nearest_planet(self, x, y):

        # uses an algorithm to find closest planet to galactic coordinates x,y
        # (algorithm is a cheap/fast form of the Pythagorean theorem)

        min_dist = 800
        return_entry = None

        for i in self.entry:

            temp = 0
            temp += abs( (x - i.galactic_x) )
            temp += abs( (y - i.galactic_y) )

            if temp < min_dist:

                min_dist = temp
                return_entry = i

        return return_entry

    def initialize_planet_database(self):

        f = open('files/PLANET_DATA.TXT','r')

        radius_min = 8000
        radius_max = 0

        productivity_min = 30000
        productivity_max = 0

        population_min = 8.0 
        population_max = 0.1

        tech_min = 50
        tech_max = 0

        for i in range(256):

            line1 = f.readline()
            line1 = line1.strip()

            line2 = f.readline()
            line2 = line2.strip()

            line3 = f.readline()
            line3 = line3.strip()

            line4 = f.readline()
            line4 = line4.strip()

            master = []

            split2 = line2.split()

            # planet number
            master.append(split2[0].strip("."))

            # planet name
            master.append(split2[1].strip("'"))

            # galactic coordinates
            temp = split2[2].strip("(")  
            temp = temp.strip("),")
            temp = temp.split(",")
            x = temp[0]
            y = temp[1]
            master.append(x)
            master.append(y)

            # planet radius
            if int(split2[8]) < radius_min:
                radius_min = int(split2[8])
            elif int(split2[8]) > radius_max:
                radius_max = int(split2[8])
            master.append(split2[8])

            # government type
            # economy
            split3 = line3.split()
            offset = 0
            if split3[0] != 'Corporate':
                master.append(split3[0].strip(",")) 
                master.append(split3[1] + ' ' + split3[2].strip("."))
            else:
                master.append(split3[0] + ' ' + split3[1].strip(","))
                master.append(split3[2] + ' ' + split3[3].strip("."))
                offset = 1
            
            # population
            master.append(split3[4+offset])
            if population_min > float(split3[4+offset]):
                population_min = float(split3[4+offset])
            elif population_max < float(split3[4+offset]):
                population_max = float(split3[4+offset])
            
            # productivity
            master.append(split3[7+offset])
            if productivity_min > int(split3[7+offset]):
                productivity_min = int(split3[7+offset])
            elif productivity_max < int(split3[7+offset]):
                productivity_max = int(split3[7+offset])
            
            # HC (hub count: systems within reach by one jump)
            master.append(split3[10+offset].strip(","))
            
            # TL (tech level)
            master.append(split3[12+offset].strip(","))
            if tech_min > int(split3[12+offset].strip(",")):
                tech_min = int(split3[12+offset].strip(","))
            elif tech_max < int(split3[12+offset].strip(",")):
                tech_max = int(split3[12+offset].strip(","))

            # lifeform type
            temp = line3.split("TL:")   # need to extract lifeform type
            temp = temp[1].split(",") 
            temp = temp[1].strip()
            temp = temp.strip(".")
            master.append(temp)

            # planet description (goat soup)
            temp = line4.strip("'")
            temp = temp.strip("'")
            temp = temp.strip()
            master.append(temp)   

            p = PlanetData()

            # these are the 13 data fields from the original game

            p.number = int(master[0])
            p.name = master[1] 
            p.galactic_x = int(master[2])
            p.galactic_y = int(master[3])
            p.radius = int(master[4])
            p.government = gov[master[5]]
            p.economy = eco[master[6]]
            p.population = float(master[7])
            p.productivity = int(master[8]) 
            p.hub_count = int(master[9]) 
            p.tech_level = int(master[10]) 
            p.lifeform = master[11] 
            p.goatsoup = master[12] 

            self.entry.append(p)

        f.close()

        print('  256 PLANETARY SYSTEMS LOADED:')
        print()
        print('    Planet Radius Range: ' + str(radius_min) + ' to ' + str(radius_max))
        print('    Productivity Range: ' + str(productivity_min) + ' to ' + str(productivity_max))
        print('    Population Range: ' + str(population_min) + ' to ' + str(population_max))
        print('    Tech Level Range: ' + str(tech_min) + ' to ' + str(tech_max))
        print()

        sys.stdout.flush()

    def add_addtional_info_to_database(self):

        for p in self.entry:

            locs = [ (1,1,5,5), (5,1,1,5), (5,5,1,1), (1,5,5,1) ]
            choice = int(p.radius) % 4

            location = locs[choice]

            p.planet_radius = int(int(p.radius) / 12)    # original is 2820 to 6900 
            i = len(planetary_color_list)
            c = int(p.galactic_x) % i
            p.planet_color = planetary_color_list[c]
            p.planet_x = (location[0] * define.FLIGHT_W) + int(define.FLIGHT_W / 2)
            p.planet_y = (location[1] * define.FLIGHT_H) + int(define.FLIGHT_H / 2)
            p.planet_x += (int(p.productivity) % int(define.FLIGHT_W/2))
            p.planet_y += (int(p.productivity) % int(define.FLIGHT_H/2))

            p.star_radius = ((int(p.radius) % 5) + 1) * 60 # only 5 star sizes
            i = len(star_color_list)
            c = int(p.galactic_y) % i
            p.star_color = star_color_list[c]
            p.star_x = (location[2] * define.FLIGHT_W) + int(define.FLIGHT_W / 2)
            p.star_y = (location[3] * define.FLIGHT_H) + int(define.FLIGHT_H / 2)
            p.star_x += (int(p.productivity) % int(define.FLIGHT_W/2))
            p.star_y += (int(p.productivity) % int(define.FLIGHT_H/2))

            location = int((p.planet_radius * p.star_radius) % 360)
            distance = p.planet_radius + 300
            dx = distance * math.cos(math.radians(location))
            dy = distance * math.sin(math.radians(location))
            dy = -dy
            p.station_x = p.planet_x + dx
            p.station_y = p.planet_y + dy

            p.galactic_chart_x = int(float(p.galactic_x) * \
                    define.GALACTIC_CHART_SCALE_W)
            p.galactic_chart_y = int(float(p.galactic_y) * \
                    define.GALACTIC_CHART_SCALE_H)

            for i in range(3):
                price = equipment_price[i]
                p.equipment.append((equipment_name[i], price))
            if p.tech_level > 1:
                price = equipment_price[3]
                p.equipment.append((equipment_name[3], price))
            if p.tech_level > 2:
                price = equipment_price[4]
                p.equipment.append((equipment_name[4], price))
            if p.tech_level > 3:
                price = equipment_price[5]
                p.equipment.append((equipment_name[5], price))
            if p.tech_level > 4:
                price = equipment_price[6]
                p.equipment.append((equipment_name[6], price))
            if p.tech_level > 5:
                price = equipment_price[7]
                p.equipment.append((equipment_name[7], price))
            if p.tech_level > 6:
                price = equipment_price[8]
                p.equipment.append((equipment_name[8], price))
            if p.tech_level > 7:
                price = equipment_price[9]
                p.equipment.append((equipment_name[9], price))
            if p.tech_level > 8:
                price = equipment_price[10]
                p.equipment.append((equipment_name[10], price))
            if p.tech_level > 9:
                price = equipment_price[11]
                p.equipment.append((equipment_name[11], price))
                price = equipment_price[12]
                p.equipment.append((equipment_name[12], price))
           
            if p.galactic_chart_x > 256:
                if p.galactic_chart_y < 127:
                    r1 = int(p.planet_radius * 0.9751)
                    r2 = int(p.star_radius * 0.7417)
                    if (r1+r2+6)%2 == 0:
                        p.num_thargoids = ((r1 + r2) % 18) + 5

    def adjust_price(self, p):

        price = p + (p * (0.30 * random.random()) * random.choice([-1,1]))

        return price

class PlanetData():

    # 13 items

    def __init__(self):

        # original game data fields (13 total)

        self.number = 0
        self.name = None
        self.galactic_x = 0
        self.galactic_y = 0
        self.radius = 0
        self.government = 0 
        self.economy = 0 
        self.population = 0
        self.productivity = 0
        self.hub_count = 0
        self.tech_level = 0
        self.lifeform = None
        self.goatsoup = None

        # added fields for Flatland

        self.planet_radius = 0
        self.planet_color = None
        self.planet_x = 0
        self.planet_y = 0

        self.star_radius = 0
        self.star_color = None
        self.star_x = 0
        self.star_y = 0

        self.station_x = 0
        self.station_y = 0

        # calculate where to draw star on galactic map

        self.galactic_chart_x = 0
        self.galactic_chart_y = 0

        # equipment for sale
        self.equipment = []

        # thargoids, track how many (if any at all, than no other lifeforms)
        self.num_thargoids = 0  
        self.newly_occupied = False
        self.newly_liberated = False

    def print_info(self):

        # for testing purposes

        print()
        print('System Number: ' + str(self.number))
        print('Planet Name: ' + self.name)
        print('Galactic Coordinates: ' + str(self.galactic_x) + ', ' + \
                str(self.galactic_y))
        print('Planet Radius: ' + str(self.radius) + ' km')
        print('Government: ' + str(self.government))
        print('Economy: ' + str(self.economy))
        print('Population: ' + str(round(self.population, 1)) + ' Billion')
        print('Productivity: ' + str(self.productivity) + ' M Cr')
        print('Hub Count: ' + str(self.hub_count))
        print('Tech Level: ' + str(self.tech_level))
        print('Lifeform: ' + self.lifeform)
        print('Description: ' + self.goatsoup)
    
        print()
        print('Planet Radius: ' + str(self.planet_radius))
        print('Planet Color: ' + str(self.planet_color))
        print('Planet x: ' + str(self.planet_x))
        print('Planet y: ' + str(self.planet_y))

        print()
        print('Star Radius: ' + str(self.star_radius))
        print('Star Color: ' + str(self.star_color))
        print('Star x: ' + str(self.star_x))
        print('Star y: ' + str(self.star_y))

        print()
        print('Galactic Chart x: ' + str(self.galactic_chart_x))
        print('Galactic Chart y: ' + str(self.galactic_chart_y))
        sys.stdout.flush()

    def get_data(self):

        temp = []

        temp.append(trade_database.economy_name[self.economy])
        temp.append(trade_database.government_name[self.government])
        temp.append(str(self.tech_level))
        temp.append(str(round(self.population, 1)) + ' Billion')
        temp.append(str(self.productivity) + ' M Cr')
        temp.append(str(self.planet_radius) + ' km')
        
        # format goatsoup so no words get cut off on right margin

        goatsoup_list = self.goatsoup.split()

        line = ''

        for i in goatsoup_list:

            test_length = len(i)

            # is there enough room?

            if len(line) + test_length < 33:

                line += i

                line += ' '

            else:

                temp.append(line)

                line = i + ' '

        temp.append(line)

        return temp

# build lists for choosing random planet/star define.
planetary_color_list = []
planetary_color_list.append(define.BLUE)
planetary_color_list.append(define.GREEN)
planetary_color_list.append(define.NAVY)
planetary_color_list.append(define.FOREST_GREEN)
planetary_color_list.append(define.BLUE_GREEN)
planetary_color_list.append(define.TEAL)
planetary_color_list.append(define.PALE_GREEN)
planetary_color_list.append(define.PURPLE)
planetary_color_list.append(define.INDIGO)
planetary_color_list.append(define.OLIVE)
planetary_color_list.append(define.GRAY)
planetary_color_list.append(define.SAND_BLUE)
planetary_color_list.append(define.KERMIT_GREEN)
planetary_color_list.append(define.POND_SCUM)
planetary_color_list.append(define.AQUA)

star_color_list = []
star_color_list.append(define.YELLOW)
star_color_list.append(define.RED)
star_color_list.append(define.ORANGE)
star_color_list.append(define.PINK)
star_color_list.append(define.WHITE)
star_color_list.append(define.BARBIE)
star_color_list.append(define.KHAKI)

gov = { \
    'Anarchy':0, \
    'Feudal':1, \
    'Multi-Government':2, \
    'Dictatorship':3, \
    'Communist':4, \
    'Confederacy':5, \
    'Democracy':6, \
    'Corporate State':7 }

eco = { \
    'Rich Ind':0, \
    'Average Ind':1, \
    'Poor Ind':2, \
    'Mainly Ind':3, \
    'Mainly Agri':4, \
    'Rich Agri':5, \
    'Average Agri':6, \
    'Poor Agri':7 }

equipment_name = { \
        0: 'Fuel                     ', \
        1: 'Missile                  ', \
        2: 'Large Cargo Bay          ', \
        3: 'ECM System               ', \
        4: 'Pulse Laser              ', \
        5: 'Beam Laser               ', \
        6: 'Fuel Scoop               ', \
        7: 'Escape Capsule           ', \
        8: 'Energy Bomb              ', \
        9: 'Extra Energy Unit        ', \
        10:'Docking Computer         ', \
        11:'Mining Laser             ', \
        12:'Military Laser           ' }

equipment_price = { \
        0:37.00 , \
        1:31.00 , \
        2:402.00 , \
        3:60.00 , \
        4:400.00 , \
        5:1000.00 , \
        6:525.00, \
        7:1000.00, \
        8:90.00, \
        9:1500.00, \
        10:1500.00, \
        11:825.00, \
        12:6523.00 }
