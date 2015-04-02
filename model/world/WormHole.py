from model import *


class WormHole(Target):
    WIDTH = 125
    HEIGHT = 125
    NUKE_COST = 2
    DEFAULT_DURATION = 600

    def __init__(self, position, destination, player_id):
        super(WormHole, self).__init__(position)
        self.duration = self.DEFAULT_DURATION
        self.destination = destination
        self.player_id = player_id

    def action(self):
        self.duration -= 1

    def select(self, position):
        if self.position[0]-self.WIDTH/2 < position[0] < self.position[0]+self.WIDTH/2:
            if self.position[1]-self.HEIGHT/2 < position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None
    
    def over(self, position_start, position_end):
        if position_end[0] > self.position[0] - self.WIDTH/2 and position_start[0] < self.position[0] + self.WIDTH/2:
            if position_end[1] > self.position[1] - self.HEIGHT/2 and position_start[1] < self.position[1] + self.HEIGHT/2:
                return True
        return False