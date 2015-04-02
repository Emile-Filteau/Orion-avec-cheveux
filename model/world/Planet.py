from model import *
from model.world import SolarSystem
import random


class Planet(Target):
    IMAGE_WIDTH = 38
    IMAGE_HEIGHT = 37
    WIDTH = 1600
    HEIGHT = 1200
    PADDING = 25
    MAX_DIST_FROM_SUN = SolarSystem.WIDTH/4
    MINERAL = 0
    GAZ = 1
    LANDING_ZONE = 2
    NUCLEAR = 3

    def __init__(self, planet_position, n_mineral_stack, n_gaz_stack, id, solar_system):
        super(Planet, self).__init__(planet_position)
        self.discovered = False
        self.minerals = []
        self.mineral_qty = 0
        self.gaz_qty = 0
        self.gaz = []
        self.nuclear_site = None
        self.n_mineral_stack = n_mineral_stack + 1
        self.n_gaz_stack = n_gaz_stack + 1
        self.landing_zones = []
        self.units = []
        self.buildings = []
        self.id = id
        self.solar_system = solar_system
        for i in range(0, self.n_mineral_stack):
            n_minerals = random.randrange(MineralStack.MAX_QTY/2, MineralStack.MAX_QTY)
            position_found = False
            position = None
            while not position_found:
                position_found = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-MineralStack.WIDTH/2:
                    position_found = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-MineralStack.HEIGHT/2:
                    position_found = False
                for mineral in self.minerals:
                    if mineral.position[0]-mineral.WIDTH < position[0] < mineral.position[0]+mineral.WIDTH:
                        if mineral.position[1]-mineral.HEIGHT < position[1] < mineral.position[1]+mineral.HEIGHT:
                            position_found = False
                            break
            self.minerals.append(MineralStack(n_minerals, position, i, id, solar_system.sunId))
        for i in range(0, self.n_gaz_stack):
            n_gaz = int(random.randrange(GazStack.MAX_QTY/2, GazStack.MAX_QTY))
            position_found = False
            position = None
            while not position_found:
                position_found = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-GazStack.WIDTH/2:
                    position_found = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-GazStack.HEIGHT/2:
                    position_found = False
                for mineral in self.minerals:
                    if position[0] > mineral.position[0]-mineral.WIDTH < position[0] < mineral.position[0]+mineral.WIDTH:
                        if position[1] > mineral.position[1]-mineral.HEIGHT < position[1] < mineral.position[1]+mineral.HEIGHT:
                            position_found = False
                            break
                for gaz in self.gaz:
                    if gaz.position[0]-gaz.WIDTH < position[0] < gaz.position[0]+gaz.WIDTH:
                        if gaz.position[1]-gaz.HEIGHT < position[1] < gaz.position[1]+gaz.HEIGHT:
                            position_found = False
                            break
            self.gaz.append(GazStack(n_gaz, position, i, id, solar_system.sunId))
        nuclear = random.random()*6
        if nuclear > 4:
            position_found = False
            position = None
            while not position_found:
                position_found = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-GazStack.WIDTH/2:
                    position_found = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-GazStack.HEIGHT/2:
                    position_found = False
                for mineral in self.minerals:
                    if mineral.position[0]-mineral.WIDTH < position[0] < mineral.position[0]+mineral.WIDTH:
                        if mineral.position[1]-mineral.HEIGHT < position[1] < mineral.position[1]+mineral.HEIGHT:
                            position_found = False
                            break
                for gaz in self.gaz:
                    if gaz.position[0]-gaz.WIDTH < position[0] < gaz.position[0]+gaz.WIDTH:
                        if gaz.position[1]-gaz.HEIGHT < position[1] < gaz.position[1]+gaz.HEIGHT:
                            position_found = False
                            break
            self.nuclear_site = NuclearSite(position, self.id, self.solar_system.sunId)

    def get_num_minerals(self):
        minerals = 0
        for i in self.minerals:
            minerals += i.nbMinerals
        return minerals

    def get_num_gaz(self):
        gaz = 0
        for i in self.gaz:
            gaz += i.nbGaz
        return gaz

    def add_landing_zone(self, player_id, landing_ship, player):
        place_found = False
        position = None
        while not place_found:
            place_found = True
            position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
            if position[0] < LandingZone.WIDTH/2 or position[0] > self.WIDTH-LandingZone.WIDTH/2:
                place_found = False
            if position[1] < LandingZone.HEIGHT/2 or position[1] > self.HEIGHT-LandingZone.HEIGHT/2:
                place_found = False
            for landing_zone in self.landing_zones:
                if landing_zone.position[0]-landing_zone.WIDTH-100 < position[0] < landing_zone.position[0]+landing_zone.WIDTH+100:
                    if landing_zone.position[1]-landing_zone.HEIGHT-100 < position[1] < landing_zone.position[1]+landing_zone.HEIGHT+100:
                        place_found = False
                        break
            for mineral in self.minerals:
                if mineral.position[0]-mineral.WIDTH-10 < position[0] < mineral.position[0]+mineral.WIDTH+10:
                    if mineral.position[1]-mineral.HEIGHT-10 < position[1] < mineral.position[1]+mineral.HEIGHT+10:
                        place_found = False
                        break
            for gaz in self.gaz:
                if gaz.position[0]-gaz.WIDTH-10 < position[0] < gaz.position[0]+gaz.WIDTH+10:
                    if gaz.position[1]-gaz.HEIGHT-10 < position[1] < gaz.position[1]+gaz.HEIGHT+10:
                        place_found = False
                        break
        id = len(self.landing_zones)
        new_spot = LandingZone(position, player_id, landing_ship, id, self.id, self.solar_system.sunId)
        new_spot.MAX_SHIELD = player.BONUS[player.BUILDING_SHIELD_BONUS]
        new_spot.shield = new_spot.MAX_SHIELD
        self.landing_zones.append(new_spot)
        return new_spot

    def already_landed(self, player_id):
        for landing_zone in self.landing_zones:
            if landing_zone.owner_id == player_id:
                return True
        return False

    def get_landing_spot(self, player_id):
        for landing_zone in self.landing_zones:
            if landing_zone.owner_id == player_id:
                return landing_zone
        return None

    def select(self, position):
        if self.position[0]-self.IMAGE_WIDTH/2 < position[0] < self.position[0]+self.IMAGE_WIDTH/2:
            if self.position[1]-self.IMAGE_HEIGHT/2 < position[1] < self.position[1]+self.IMAGE_HEIGHT/2:
                return self
        return None
    
    def over(self, position_start, position_end):
        if self.position[0] - self.IMAGE_WIDTH/2 < position_start[0] < self.position[0] + self.IMAGE_WIDTH/2:
            if self.position[1] - self.IMAGE_HEIGHT/2 < position_start[1] < self.position[1] + self.IMAGE_HEIGHT/2:
                return True
        return False

    def ground_over(self, position_start, position_end):
        for mineral in self.minerals:
            if mineral.over(position_start, position_end):
                return True
        for gaz in self.gaz:
            if gaz.over(position_start, position_end):
                return True
        for landing_zone in self.landing_zones:
            if landing_zone.over(position_start, position_end):
                return True
        if self.nuclear_site:
            if self.nuclear_site.over(position_start, position_end):
                return True
        return False

    def ground_select(self, position):
        for landing_zone in self.landing_zones:
            if landing_zone.select(position):
                return landing_zone
        for mineral in self.minerals:
            if mineral.select(position):
                return mineral
        for gaz in self.gaz:
            if gaz.select(position):
                return gaz
        if self.nuclear_site:
            if self.nuclear_site.select(position):
                return self.nuclear_site
        for unit in self.units:
            if unit.select(position):
                return unit
        for building in self.buildings:
            if building.select(position):
                return building
        return None

    def has_zone_in_range(self, position, range):
        for landing_zone in self.landing_zones:
            if landing_zone.is_in_range(position, range):
                return landing_zone
        return None