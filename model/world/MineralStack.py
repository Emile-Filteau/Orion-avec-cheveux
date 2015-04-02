from model import *


class MineralStack(Target):
    WIDTH = 48
    HEIGHT = 64
    MAX_QTY = 3000

    def __init__(self, nb_minerals, position, id, planet_id, sun_id):
        super(MineralStack, self).__init__(position)
        self.nb_minerals = nb_minerals
        self.id = id
        self.planet_id = planet_id
        self.sun_id = sun_id

    def over(self, position_start, position_end):
        if self.nb_minerals > 0:
            if position_end[0] > self.position[0]-self.WIDTH/2 and position_start[0] < self.position[0]+self.WIDTH/2:
                if position_end[1] > self.position[1]-self.HEIGHT/2 and position_start[1] < self.position[1]+self.HEIGHT/2:
                    return True
        return False
        
    def select(self, position):
        if self.position[0]-self.WIDTH/2 < position[0] < self.position[0]+self.WIDTH/2:
            if self.position[1]-self.HEIGHT/2 < position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None