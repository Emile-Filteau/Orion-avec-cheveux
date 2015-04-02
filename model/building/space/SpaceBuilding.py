from model import *
from model.building import Building


class SpaceBuilding(Building):
    def __init__(self, type, position, owner):
        super(SpaceBuilding, self).__init__(type, position, owner)