from model import *
from model.building import ConstructionBuilding


class LandingZone(ConstructionBuilding):
    WIDTH = 75
    HEIGHT = 75

    def __init__(self, position, owner_id, landing_ship, id, planet_id, sun_id):
        super(LandingZone, self).__init__(Building.LANDING_ZONE, position, owner_id)
        self.owner_id = owner_id
        self.landed_ship = landing_ship
        self.id = id
        self.planet_id = planet_id
        self.sun_id = sun_id
        self.finished = True
        self.planet = landing_ship.planet
        self.nuclear = 0

    def over(self, position_start, position_end):
        if position_end[0] > self.position[0] - self.WIDTH/2 and position_start[0] < self.position[0] + self.WIDTH/2:
            if position_end[1] > self.position[1] - self.HEIGHT/2 and position_start[1] < self.position[1] + self.HEIGHT/2:
                return True
        return False

    def select(self, position):
        if self.position[0]-self.WIDTH/2 < position[0] < self.position[0]+self.WIDTH/2:
            if self.position[1]-self.HEIGHT/2 < position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None

    def is_in_range(self, position, range, on_planet=False, planet_id=-1, sun_id=-1):
        if on_planet:
            if self.sun_id == sun_id and self.planet_id == planet_id:
                if position[0]-range < self.position[0] < position[0]+range:
                    if position[1]-range < self.position[1] < position[1]+range:
                        return self
        return None

    def take_damage(self, amount, players):
        if not self.landed_ship:
            if self.landed_ship.take_damage(amount, players):
                killed_owner = self.owner_id
                index = players[self.owner_id].units.index(self.landed_ship)
                self.landed_ship = None
                players[self.owner_id].kill_unit((index, killed_owner, False))
        else:
            self.hitpoints -= amount
            if self.hitpoints <= 0:
                return True
        return False

    def add_unit_to_queue(self, unit_type, galaxy=None, forcebuild=False):
        position = [self.position[0], self.position[1], 0]
        unit = None
        if unit_type == Unit.GROUND_GATHER:
            unit = GroundGatherUnit(Unit.GROUND_GATHER, position, self.owner, self.planet_id, self.sun_id, True)
            unit.planet = galaxy.solarSystemList[self.sun_id].planets[self.planet_id]
        elif unit_type == Unit.GROUND_ATTACK:
            unit = GroundAttackUnit(Unit.GROUND_ATTACK, position, self.owner, self.planet_id, self.sun_id, True)
            unit.planet = galaxy.solarSystemList[self.sun_id].planets[self.planet_id]
        elif unit_type == Unit.GROUND_BUILDER_UNIT:
            unit = GroundBuilderUnit(Unit.GROUND_BUILDER_UNIT, position, self.owner, self.planet_id, self.sun_id, True)
            unit.planet = galaxy.solarSystemList[self.sun_id].planets[self.planet_id]
        elif unit_type == Unit.SPECIAL_GATHER:
            unit = SpecialGather(Unit.SPECIAL_GATHER, position, self.owner, self.planet_id, self.sun_id, True)
            unit.planet = galaxy.solarSystemList[self.sun_id].planets[self.planet_id]
        if forcebuild:
            unit.build_time = 1
            if unit_type in (Unit.SPECIAL_GATHER, Unit.GROUND_GATHER):
                unit.GATHER_TIME = 0
        self.unit_being_construct.append(unit)