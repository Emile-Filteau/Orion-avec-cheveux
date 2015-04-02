from model import *
from model.building import ConstructionBuilding


class Barrack(ConstructionBuilding):
    def __init__(self,  type, position, owner):
        super(Barrack, self).__init__(type, position, owner)
        self.flag.finalTarget = Target(position)
        self.owner = owner

    def add_unit_to_queue(self, unit_type, galaxy=None, forcebuild=False):
        position = [self.position[0], self.position[1], 0]
        unit = None
        if unit_type == Unit.ATTACK_SHIP:
            unit = SpaceAttackUnit(Unit.ATTACK_SHIP, position, self.owner)
        elif unit_type == Unit.SPACE_BUILDING_ATTACK:
            unit = SpaceBuildingAttack(Unit.SPACE_BUILDING_ATTACK, position, self.owner)
        if unit:
            self.unit_being_construct.append(unit)
        if forcebuild:
            unit.build_time = 1