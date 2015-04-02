from model import *
from model.unit.ground import GroundUnit


class GroundBuilderUnit(GroundUnit):
    def __init__(self,  type, position, owner, planet_id, sun_id, is_landed=False):
        super(GroundBuilderUnit, self).__init__(type, position, owner, planet_id, sun_id, is_landed)

    def action(self, parent):
        if self.flag.flag_state == Flag.BUILD:
            self.build(self.flag.final_target, parent)
        else:
            super(GroundBuilderUnit, self).action(parent)

    def build(self, building, player):
        if Helper.calc_distance(self.position[0], self.position[1], self.flag.final_target.position[0], self.flag.final_target.position[1]) >= self.move_speed:
            self.move()
        else:
            end_pos = [self.flag.final_target.position[0],self.flag.final_target.position[1]]
            self.position = end_pos
            
            if building.buildingTimer < building.buildTime:
                building.buildingTimer += 1
                building.hitpoints += (1/building.buildTime)*building.MAX_HP[building.type]
            else:
                building.finished = True
                if building.hitpoints >= building.MAX_HP[building.type]-1:
                    building.hitpoints = building.MAX_HP[building.type]
                self.flag.flag_state = Flag.STANDBY
                if building.type == Building.FARM:
                    player.MAX_FOOD += 5

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