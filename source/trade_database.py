# Author: Darron Vanaria
# Filesize: 11537 bytes
# LOC: 294

import random
import sys

# Summary of Economics in Flatland:
#
#     1. items to buy at Rich Industrial (index 0) systems:
#
#          luxuries, computers, machinery
#
#     2. items to buy at Poor Agricultural (index 7) systems:
#
#          food, textiles, liquor, furs, precious metals and gems
#
#     3. items on the black market:
#
#          buy firearms at Rich Industrial systems
#
#          buy narcotics and slaves at Poor Agricultural systems
#
#     Note: only Government Types 'Anarchy' and 'Fuedal'
#           will allow buying/selling illegal items 
#           without police intervention

class Database():

    def __init__(self, planet_database):

        self.entry = []

        self.planet_database = planet_database

        for i in range(256):

            p = planet_database.get_planet_by_index(i)

            temp = MarketData(p)

            self.entry.append(temp)

    def get_market_by_index(self, index):

        # retrieve planet from database via index number 0 - 255

        return self.entry[index]

    def update_price(self, index, price_list):

        self.entry[index].prices = []

        for i in commodity_name:

            self.entry[index].prices.append(price_list[i])

    def update_stock(self, index, stock_list):

        self.entry[index].stock = []

        for i in commodity_name:

            self.entry[index].stock.append(stock_list[i])

    def rebuild_market(self, index):

        p = self.planet_database.get_planet_by_index(index)

        for i in commodity_name:
            
            temp = self.entry[index].prices[i] 

            flux = temp * PRICE_FLUX
            flux = flux * random.choice([-1,1])
            t = temp + flux

            # make sure no prices are negative
            if t < 0:
                t = -t
            if t == 0:
                t = 1.0

            vf = "{0:0.1f}".format(t)

            self.entry[index].prices[i] = float(vf)

        for i in commodity_name:

            temp = self.entry[index].stock[i]

            temp += random.choice([-5,-4,-3,3,4,5])

            if temp < 0:
                temp = 0

            self.entry[index].stock[i] = temp


class MarketData():

    def __init__(self, planet):

        # constructor takes a PlanetData object

        self.planet = planet
        self.prices = self.generate_market_prices(planet)
        self.stock = self.generate_market_stock(planet, self.prices)
        self.chief_import = self.find_chief_import(self.prices, planet)
        self.chief_export = self.find_chief_export(self.prices, planet)

        for i in self.prices:
            if i == self.chief_import:
                self.prices[i] = self.prices[i] * 1.25
            if i == self.chief_export:
                self.prices[i] = self.prices[i] * 0.75 

    def generate_market_prices(self, p):

        # returns a list of 17 commodity prices for this particular world.
        # p is a PlanetData structure

        # this should be called every time the player re-enters a system, due
        # to slight price fluctuations each trip.

        economy_type = p.economy
        government_type = p.government

        # this uses the global 'market' (list of lists) to generate a specific
        # set of prices for a specific system

        temp = list( market[economy_type] )

        for i in commodity_name:

            flux = temp[i] * PRICE_FLUX
            flux = flux * random.choice([-1,1])
            t = temp[i] + flux

            # make sure no prices are negative
            if t < 0:
                t = -t
            if t == 0:
                t = 1.0

            vf = "{0:0.1f}".format(t)

            temp[i] = float(vf) 

        # black market items
        for i in (3,6,10):
            temp[i] = 20 # base price
            temp[i] += (11.3 * government_type)
            flux = temp[i] * PRICE_FLUX
            flux = flux * random.choice([-1,1])
            t = temp[i] + flux
            
            # make sure no prices are negative
            if t < 0:
                t = -t
            if t == 0:
                t = 1.0

            vf = "{0:0.1f}".format(t)

            temp[i] = float(vf) 
        
        # hack: make profits a bit larger for legal items
        diffs = self.price_diff(temp, economy_type)
        for i in commodity_name:
            if i not in (3,6,10):
                t = temp[i] 
                if diffs[i] > 0:
                    t = temp[i] + (20 * random.random())
                elif diffs[i] < 0:
                    t = temp[i] - (20 * random.random())
            
                # make sure no prices are negative
                if t < 0:
                    t = -t
                if t == 0:
                    t = 1.0

                vf = "{0:0.1f}".format(t)

                temp[i] = float(vf) 

        return temp

    def generate_market_stock(self, p, market_prices):

        # p is a PlanetData structure

        economy_type = p.economy
        government_type = p.government

        temp = []

        diffs = self.price_diff( market_prices, economy_type )

        for i in commodity_name:

            s = STOCK_BASELINE + diffs[i] 
            if s <= 0:
                s = 0

            # no stock of illegal goods in 'civilized' worlds 
            if i in (3,6,10) and government_type > 1:
                s = 0

            temp.append( int(s) )

        return temp

    def find_chief_import(self, m, p):

        # p is a PlanetData structure

        economy_type = p.economy

        diff_list = self.price_diff(m, economy_type)

        difference = 0 
        index = 0 

        for i in commodity_name:

            if diff_list[i] < difference:

                if i in (3,6,10):
                    
                    if p.government < 2:
                    
                        difference = diff_list[i]
                        index = i

                else:

                    difference = diff_list[i]
                    index = i
        
        return commodity_name[index]

    def find_chief_export(self, m, p):

        # p is a PlanetData structure

        economy_type = p.economy

        diff_list = self.price_diff(m, economy_type)

        chief = 0
        chief_index = 0 

        for i in commodity_name:

            if diff_list[i] > chief:

                if i in (3,6,10):
                    
                    if p.government < 2:
                    
                        chief = diff_list[i]
                        chief_index = i

                else:

                    chief = diff_list[i]
                    chief_index = i

        return commodity_name[chief_index]

    def price_diff(self, m, economy_type):

        rlist = []

        for i in commodity_name:

            t =  average_prices[i] - m[i]
            vf = "{0:0.1f}".format(t)
            rlist.append( float(vf) )

        return rlist

    def string_list(self):

        m = self.prices
        s = self.stock
        p = self.planet

        # p is a PlanetData structure

        economy_type = p.economy

        d = self.price_diff( m, economy_type )

        string_list = []
    
        t0 = ''
        string_list.append(t0)
        t0 = '     NAVIGATION: TARGET MARKET INFO (' + p.name.upper() + ')    '
        string_list.append(t0)
        t0 = ''
        string_list.append(t0)
        t0 = ''
        string_list.append(t0)
        
        t1 = '                    UNIT    IN    MARKET '
        t2 = '   PRODUCT    UNIT  PRICE  STOCK  AVERAGE'
        t3 = ''

        string_list.append(t1)
        string_list.append(t2)
        string_list.append(t3)

        temp = ''

        for i in commodity_name:

            t = ''
            if i in (3,6,10):
                t += ' * '
            else:
                t += '   '
            t += commodity_name[i]
            temp += t.ljust(16)

            temp += unit_name[i]

            temp += str(m[i]).rjust(6)

            temp += str(s[i]).rjust(6)

            z = m[i] + d[i]
            vf = str(round(z, 1))
            temp += vf.rjust(9)

            if self.chief_import in commodity_name[i]:
                temp += ' IMPORT' 
            elif self.chief_export in commodity_name[i]:
                temp += ' EXPORT'
            else:
                temp += '       '

            string_list.append(temp)
            temp = ''

        temp = ''
        string_list.append(temp)
            
        if self.planet.num_thargoids > 0:

            temp = '   * Thargoid occupied system (illegal     '
            string_list.append(temp)
            temp = '     trading laws do not apply here)       '
            string_list.append(temp)

        elif self.planet.government > 1:

            temp = '   * Trading in illegal items punishable   '
            string_list.append(temp)
            temp = '     by law in this system! (' + \
                    government_name[ self.planet.government ] +')'
            string_list.append(temp)

        else:

            temp = '   * Illegal trading laws not enforced     ' 
            string_list.append(temp)
            temp = '     in this system (' + \
                    government_name[ self.planet.government ] +')'
            string_list.append(temp)

        return string_list

economy_name = { \
        0:'Rich Industrial', \
        1:'Average Industrial', \
        2:'Poor Industrial', \
        3:'Mainly Industrial', \
        4:'Mainly Agricultural', \
        5:'Rich Agricultural', \
        6:'Average Agricultural', \
        7:'Poor Agricultural' }

commodity_name = { \
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

government_name = { \
        0:'Anarchy', \
        1:'Feudal', \
        2:'Multi-Government', \
        3:'Dictatorship', \
        4:'Communist', \
        5:'Confederacy', \
        6:'Democracy', \
        7:'Corporate State' }

unit_name = ('t ', 't ', 't ', 't ', 't ', 't ', 't ', 't ', 't ', 't ', 't ', \
        't ', 't ', 'kg', 'kg', 'g ', 't ')

starting_prices = (35, 28, 6.7, 50, 52, 79.2, 50, 62.5, 48.3, 37.5, 50, 79.8, \
        13.5, 70, 42, 80, 71)

build_values = (-2.8, -3, 1.8, 0.0, -2.9, 3.1, 0.0, 3, 2.8, -2.1, 0.0, \
        -2.8, 2.3, -3, -2.8, -2.9, -2.4)

average_prices = (25.2, 17.5, 13, 50, 41.85, 90.05, 50, 73, 58.1, 30.15, \
        50, 70, 21.55, 59.5, 32.2, 69.85, 62.6)

PRICE_FLUX = 0.05 # how much any individual market price will differ from avg

STOCK_BASELINE = 15 # how much is in stock, if price = average

# Build Markets ############################################################

market = []  # holds 8 lists, each a full set of market prices
             # these are used as a baseline for the 8 different economies

for e in economy_name:

    temp = []

    for i in commodity_name:

        v = starting_prices[i] + (build_values[i] * e)

        vf = "{0:0.1f}".format(v)

        temp.append( float(vf) )

    market.append(temp)

############################################################################
