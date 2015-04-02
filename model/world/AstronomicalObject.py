import random
from model import *


class AstronomicalObject(Target):
    NEBULA_WIDTH = 40
    NEBULA_HEIGHT = 41
    MAX_GAS = 1000
    ASTEROID_WIDTH = 30
    ASTEROID_HEIGHT = 31
    MAX_MINERALS = 1000
    NEBULA = 0
    ASTEROID = 1
    
    def __init__(self, type, position, id, solar_system):
        super(AstronomicalObject, self).__init__(position)
        self.solar_system = solar_system
        self.id = id
        self.type = type
        self.discovered = False
        if type == AstronomicalObject.NEBULA:
            self.gazQte = random.randrange(self.MAX_GAS/2, self.MAX_GAS)
            self.mineralQte = 0
        elif type == AstronomicalObject.ASTEROID:
            self.mineralQte = random.randrange(self.MAX_MINERALS/2, self.MAX_MINERALS)
            self.gazQte = 0 

    def over_nebula(self, position_start, position_end):
        if self.gazQte > 0:
            if position_end[0] > self.position[0] - self.NEBULA_WIDTH/2 and position_start[0] < self.position[0] + self.NEBULA_WIDTH/2:
                if position_end[1] > self.position[1] - self.NEBULA_HEIGHT/2 and position_start[1] < self.position[1] + self.NEBULA_HEIGHT/2:
                    return True

    def over_asteroid(self, position_start, position_end):
        if self.mineralQte > 0:
            if position_end[0] > self.position[0] - self.ASTEROID_WIDTH/2 and position_start[0] < self.position[0] + self.ASTEROID_WIDTH/2:
                if position_end[1] > self.position[1] - self.ASTEROID_HEIGHT/2 and position_start[1] < self.position[1] + self.ASTEROID_HEIGHT/2:
                    return True
            
    def select_nebula(self, position):
        if self.position[0]-self.NEBULA_WIDTH/2 <= position[0] <= self.position[0]+self.NEBULA_WIDTH/2:
            if self.position[1]-self.NEBULA_HEIGHT/2 <= position[1] <= self.position[1]+self.NEBULA_HEIGHT/2:
                return self
        return None
    
    def select_asteroid(self, position):
        if self.position[0]-self.ASTEROID_WIDTH/2 < position[0] <= self.position[0]+self.ASTEROID_WIDTH/2:
            if self.position[1]-self.ASTEROID_HEIGHT/2 < position[1] <= self.position[1]+self.ASTEROID_HEIGHT/2:
                return self
        return None