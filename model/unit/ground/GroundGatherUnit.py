from model import *
from model.unit.ground import GroundUnit


class GroundGatherUnit(GroundUnit):
    GATHER_TIME = 20

    def __init__(self,  type, position, owner, planet_id, sun_id, is_landed=False):
        super(GroundGatherUnit, self).__init__(type, position, owner, planet_id, sun_id, is_landed)
        self.max_gather = 50
        self.gather_speed = self.GATHER_TIME
        self.container = [0, 0]
        self.returning = False

    def action(self, parent):
        if self.flag.flag_state == Flag.GROUND_GATHER:
            self.gather(parent, parent.game)
        elif self.flag.flag_state == Flag.LOAD:
            self.load(parent, parent.game)
        else:
            super(GroundGatherUnit, self).action(parent)

    def gather(self, player, game):
        resource = self.flag.final_target
        arrived = True
        if isinstance(resource, MineralStack) or isinstance(resource, GazStack):
            if self.position[0] < resource.position[0] or self.position[0] > resource.position[0]:
                if self.position[1] < resource.position[1] or self.position[1] > resource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gather_speed == 0:
                    if isinstance(resource, MineralStack):
                        if self.container[0] < self.max_gather:
                            if resource.nb_minerals >= 5:
                                self.container[0] += 5
                                resource.nb_minerals -= 5
                            else:
                                self.container[0] += resource.nb_minerals
                                resource.nb_minerals = 0
                                self.flag.initial_target = self.flag.final_target
                                self.flag.final_target = player.get_nearest_return_resource_center_on_planet(self.position, self)
                                game.parent.redraw_mini_map()
                            self.gather_speed = self.GATHER_TIME
                        else:
                            self.flag.initial_target = self.flag.final_target
                            self.flag.final_target = player.get_nearest_return_resource_center_on_planet(self.position, self)
                    else:
                        if self.container[1] < self.max_gather:
                            if resource.nb_gaz >= 5:
                                self.container[1] += 5
                                resource.nb_gaz -= 5
                            else:
                                self.container[1] += resource.nb_gaz
                                resource.nb_gaz = 0
                                self.flag.initial_target = self.flag.final_target
                                self.flag.final_target = player.get_nearest_return_resource_center_on_planet(self.position, self)
                                game.parent.redraw_mini_map()
                            self.gather_speed = self.GATHER_TIME
                        else:
                            self.flag.initial_target = self.flag.final_target
                            self.flag.final_target = player.get_nearest_return_resource_center_on_planet(self.position, self)
                else:
                    self.gather_speed -= 1
        else:
            if self.position[0] < resource.position[0] or self.position[0] > resource.position[0]:
                if self.position[1] < resource.position[1] or self.position[1] > resource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                player.ressources[player.MINERAL] += self.container[0]
                player.ressources[player.GAS] += self.container[1]
                self.container[0] = 0
                self.container[1] = 0
                if isinstance(self.flag.initial_target, MineralStack) or isinstance(self.flag.initial_target, GazStack):
                    self.flag.final_target = self.flag.initial_target
                    if isinstance(self.flag.initial_target, MineralStack):
                        if self.flag.final_target.nb_minerals == 0:
                            if game.get_current_planet() == self.planet:
                                player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            else:
                                player.notifications.append(Notification(self.planet.position, Notification.FINISH_GATHER))
                            self.flag.flag_state = Flag.STANDBY
                    else:
                        if self.flag.final_target.nb_gaz == 0:
                            if game.get_current_planet() == self.planet:
                                player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            else:
                                player.notifications.append(Notification(self.planet.position, Notification.FINISH_GATHER))
                            self.flag.flag_state = Flag.STANDBY
                else:
                    self.flag.final_target = self.position
                    self.flag.flag_state = Flag.STANDBY

    def load(self, player, game):
        landing_zone = self.flag.final_target
        planet = game.galaxy.solarSystemList[landing_zone.sun_id].planets[landing_zone.planet_id]
        arrived = True
        if self.position[0] < landing_zone.position[0] or self.position[0] > landing_zone.position[0]:
            if self.position[1] < landing_zone.position[1] or self.position[1] > landing_zone.position[1]:
                arrived = False
                self.move()
        if arrived and landing_zone.LandedShip:
            if len(landing_zone.LandedShip.units) <= landing_zone.LandedShip.capacity:
                player.ressources[player.MINERAL] += self.container[player.MINERAL]
                player.ressources[player.GAS] += self.container[player.GAS]
                self.container[player.MINERAL] = 0
                self.container[player.GAS] = 0
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