from model import *


class GazStack(Target):
    WIDTH = 40
    HEIGHT = 42
    MAX_QTY = 3000

    def __init__(self, nb_gaz, position, id, planet_id, sun_id):
        super(GazStack, self).__init__(position)
        self.nb_gaz = nb_gaz
        self.id = id
        self.planet_id = planet_id
        self.sun_id = sun_id
        self.state = 0

    def over(self, position_start, position_end):
        if self.nb_gaz > 0:
            if position_end[0] > self.position[0] - self.WIDTH/2 and position_start[0] < self.position[0] + self.WIDTH/2:
                if position_end[1] > self.position[1] - self.HEIGHT/2 and position_start[1] < self.position[1] + self.HEIGHT/2:
                    return True
        return False

    def select(self, position):
        if self.position[0]-self.WIDTH/2 < position[0] < self.position[0]+self.WIDTH/2:
            if self.position[1]-self.HEIGHT/2 < position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None