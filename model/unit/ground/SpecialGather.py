from model import *
from model.unit.ground import GroundGatherUnit


class SpecialGather(GroundGatherUnit):
    GATHER_TIME = 1200

    def __init__(self,  type, position, owner, planet_id, sun_id, is_landed=False):
        super(SpecialGather, self).__init__(type, position, owner, planet_id, sun_id, is_landed)
        self.maxGather = 1
        self.gather_speed = self.GATHER_TIME
        self.container = 0
        self.returning = False
        self.isGathering = False

    def action(self, parent):
        self.isGathering = False
        if self.flag.flag_state == Flag.GROUND_GATHER:
            self.gather(parent, parent.game)
        elif self.flag.flag_state == Flag.LOAD:
            self.load(parent, parent.game)
        else:
            GroundUnit.action(self, parent)

    def calc_progression(self):
        return self.gather_speed/30

    def get_color_progression(self):
        if self.gather_speed >= 800:
            return 'green'
        elif self.gather_speed >= 400:
            return 'yellow'
        else:
            return 'red'

    def gather(self, player, game):
        resource = self.flag.final_target
        arrived = True
        if isinstance(resource, NuclearSite):
            if self.position[0] < resource.position[0] or self.position[0] > resource.position[0]:
                if self.position[1] < resource.position[1] or self.position[1] > resource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gather_speed == 0:
                    if self.container < self.maxGather:
                        if resource.nbRessource > 0:
                            self.container += 1
                            resource.nbRessource -= 1
                        self.gather_speed = self.GATHER_TIME
                        self.flag.initial_target = self.flag.final_target
                        self.flag.final_target = self.planet.get_landing_spot(player.id)
                else:
                    self.isGathering = True
                    self.gather_speed -= 1
        else:
            if self.position[0] < resource.position[0] or self.position[0] > resource.position[0]:
                if self.position[1] < resource.position[1] or self.position[1] > resource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if isinstance(resource, LandingZone):
                    if resource.landed_ship:
                        resource.landed_ship.nuclear += self.container
                    else:
                        resource.nuclear += self.container
                    self.container = 0
                    self.flag.final_target = self.position
                    if game.get_current_planet() == self.planet:
                        player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                    else:
                        player.notifications.append(Notification(self.planet.position, Notification.FINISH_GATHER))
                    self.flag.flag_state = Flag.STANDBY

    def load(self, player, game):
        landing_zone = self.flag.final_target
        planet = game.galaxy.solarSystemList[landing_zone.sunId].planets[landing_zone.planetId]
        arrived = True
        if self.position[0] < landing_zone.position[0] or self.position[0] > landing_zone.position[0]:
            if self.position[1] < landing_zone.position[1] or self.position[1] > landing_zone.position[1]:
                arrived = False
                self.move()
        if arrived and landing_zone.LandedShip:
            if len(landing_zone.LandedShip.units) <= landing_zone.LandedShip.capacity:
                landing_zone.LandedShip.nuclear += self.container
                self.container = 0
                self.planet = None
                self.position = [-100000, -100000]
                self.planet_id = -1
                self.sun_id = -1
                planet.units.pop(planet.units.index(self))
                landing_zone.LandedShip.units.append(self)
                if self in player.selectedObjects:
                    player.selectedObjects.pop(player.selectedObjects.index(self))
                self.flag.flag_state = Flag.STANDBY
            else:
                self.flag.flag_state = Flag.STANDBY