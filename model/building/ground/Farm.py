from model import *
from model.building.ground import GroundBuilding


class Farm(GroundBuilding):
    def __init__(self, type, position, owner, sun_id, planet_id):
        super(Farm, self).__init__(type, position, owner, sun_id, planet_id)