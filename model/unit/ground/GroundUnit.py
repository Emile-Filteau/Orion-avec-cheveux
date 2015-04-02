from model import *
from model.unit import Unit


class GroundUnit(Unit):
    def __init__(self, type, position, owner, planet_id, sun_id, is_landed=False):
        super(GroundUnit, self).__init__(type, position, owner)
        self.sun_id = sun_id
        self.planet_id = planet_id
        self.planet = None
        self.is_landed = is_landed

    def is_in_range(self, position, range, on_planet=False, planet_id=-1, solar_system_id=-1):
        if self.is_landed and on_planet:
            if self.sun_id == solar_system_id and self.planet_id == planet_id:
                if position[0]-range < self.position[0] < position[0]+range:
                    if position[1]-range < self.position[1] < position[1]+range:
                        return self
        return None

    def land(self, planet, position):
        self.is_landed = True
        self.position = position
        self.planet = planet
        self.planet_id = planet.id
        self.sun_id = planet.solarSystem.sunId
        planet.units.append(self)

    def take_off(self):
        self.is_landed = False
        self.planet_id = -1
        self.sun_id = -1
        self.planet = None

    def action(self, parent):
        if self.flag.flag_state == Flag.LOAD:
            self.load(parent.game)
        else:
            Unit.action(self, parent)

    def load(self, game):
        landing_zone = self.flag.final_target
        planet = game.galaxy.solarSystemList[landing_zone.sunId].planets[landing_zone.planetId]
        arrived = True
        if self.position[0] < landing_zone.position[0] or self.position[0] > landing_zone.position[0]:
            if self.position[1] < landing_zone.position[1] or self.position[1] > landing_zone.position[1]:
                arrived = False
                self.move()
        if arrived and landing_zone.LandedShip:
            if len(landing_zone.LandedShip.units) <= landing_zone.LandedShip.capacity:
                self.planet = None
                self.position = [-100000, -100000]
                self.planet_id = -1
                self.sun_id = -1
                planet.units.pop(planet.units.index(self))
                landing_zone.LandedShip.units.append(self)
                if self in game.players[self.owner].selectedObjects:
                    game.players[self.owner].selectedObjects.pop(game.players[self.owner].selectedObjects.index(self))
                self.flag.flag_state = Flag.STANDBY
            else:
                self.flag.flag_state = Flag.STANDBY