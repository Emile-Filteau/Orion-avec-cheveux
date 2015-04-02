from model import *
import math
import random


class Galaxy(object):
    SIZE_MULTIPLIER = 1000
    MIN_SPAWN_POINT_SPACING = 800
    BORDER_SPACING = 25
    SUN_BORDER_SPACING = BORDER_SPACING + 175
    MAX_SOLAR_SYSTEM = 9

    def __init__(self, nb_player, seed):
        if nb_player > 2:
            temp = int(math.pow(2, math.sqrt(nb_player)) * 1500)
            if temp % 2 > 0:
                temp += 1
            self.width = temp
            self.height = temp
            self.depth = temp
        else:
            self.width = 3000
            self.height = 3000
            self.depth = 3000
        self.seed = random.seed(seed)
        self.spawn_points = []
        self.solar_system_list = []
        self.wormholes = []
        for i in range(1, nb_player * self.MAX_SOLAR_SYSTEM):
            temp_x = ""
            temp_y = ""
            place_found = False
            while not place_found:
                temp_x = random.randrange(self.width/2 * -1, self.width/2)
                temp_y = random.randrange(self.height/2 * -1, self.height/2)
                place_found = True

                if temp_x < -1*(self.width/2)+self.SUN_BORDER_SPACING or temp_x > self.width/2-self.SUN_BORDER_SPACING:
                    place_found = False
                if temp_y < -1*(self.height/2)+self.SUN_BORDER_SPACING or temp_y > self.height/2-self.SUN_BORDER_SPACING:
                    place_found = False
                for j in self.solar_system_list:
                    if j.sunPosition[0]-j.WIDTH < temp_x < j.sunPosition[0]+j.WIDTH:
                        if j.sunPosition[1]-j.HEIGHT < temp_y < j.sunPosition[1]+j.HEIGHT:
                            place_found = False
                            break
            self.solar_system_list.append(SolarSystem([temp_x, temp_y, 0], i-1))

    def get_spawn_point(self):
        found = False
        x = None
        y = None
        while not found:
            x = (random.random()*self.width)-self.width/2
            y = (random.random()*self.height)-self.height/2
            found = True
            if x < (self.width/2*-1)+Building.SIZE[Building.MOTHERSHIP][0] or x > self.width/2-Building.SIZE[Building.MOTHERSHIP][0]:
                found = False
            if y < (self.height/2*-1)+Building.SIZE[Building.MOTHERSHIP][1] or y > self.height/2-Building.SIZE[Building.MOTHERSHIP][1]:
                found = False
            if found:
                for i in self.solar_system_list:
                    if i.sunPosition[0] - i.WIDTH/2 < x < i.sunPosition[0] + i.WIDTH/2:
                        if i.sunPosition[1] - i.HEIGHT/2 < y < i.sunPosition[1]+i.HEIGHT/2:
                            found = False
                            break
            if found:
                for i in self.spawn_points:
                    if i[0] - Galaxy.MIN_SPAWN_POINT_SPACING < x < i[0] + Galaxy.MIN_SPAWN_POINT_SPACING:
                        if i[1] - Galaxy.MIN_SPAWN_POINT_SPACING < y < i[1] + Galaxy.MIN_SPAWN_POINT_SPACING:
                            found = False
                            break
        self.spawn_points.append((x, y, 0))
        return [x, y, 0]
    
    def select(self, position, want_worm_hole=True):
        clicked_obj = None
        if want_worm_hole:
            for i in self.wormholes:
                if i.duration > 0:
                    wormhole = i.select(position)
                    if wormhole and not clicked_obj:
                        clicked_obj = wormhole
        if not clicked_obj:
            for i in self.solar_system_list:
                space_obj = i.select(position)
                if space_obj and not clicked_obj:
                    clicked_obj = space_obj
        return clicked_obj