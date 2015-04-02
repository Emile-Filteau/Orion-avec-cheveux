from model import *
from model.unit import *

class SpaceUnit(Unit):
    def __init__(self,  type, position, owner):
        super(SpaceUnit, self).__init__(type, position, owner)