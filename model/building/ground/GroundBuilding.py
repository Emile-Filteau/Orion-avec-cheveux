from model import *
from model.building import Building

class GroundBuilding(Building):
    def __init__(self, type, position, owner, sun_id, planet_id):
        super(GroundBuilding, self).__init__(type, position, owner)
        self.sunId = sun_id
        self.planetId = planet_id

    def is_in_range(self, position, range, on_planet=False, planet_id=-1, sun_id=-1):
        if on_planet and self.finished:
            if self.sunId == sun_id and self.planetId == planet_id:
                if position[0] - range < self.position[0] < position[0] + range:
                    if position[1] - range < self.position[1] < position[1] + range:
                        return self
        return None