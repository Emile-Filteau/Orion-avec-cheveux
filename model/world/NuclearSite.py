from model import *


class NuclearSite(Target):
    WIDTH = 35
    HEIGHT = 35

    def __init__(self, position, planet_id, sun_id):
        super(NuclearSite, self).__init__(position)
        self.nb_resource = 1
        self.planetId = planet_id
        self.sunId = sun_id

    def over(self, position_start, position_end):
        if self.nb_resource > 0:
            if position_end[0] > self.position[0] - self.WIDTH/2 and position_start[0] < self.position[0] + self.WIDTH/2:
                if position_end[1] > self.position[1] - self.HEIGHT/2 and position_start[1] < self.position[1] + self.HEIGHT/2:
                    return True
        return False

    def select(self, position):
        if position[0] - self.WIDTH/2 < self.position[0] < position[0] + self.WIDTH/2:
            if position[1] - self.HEIGHT/2 < self.position[1] < self.position[1] + self.HEIGHT/2:
                return self
        return None
