from model import *
from model.unit.space import SpaceUnit


class GatherShip(SpaceUnit):
    GATHER_TIME = 20

    def __init__(self,  type, position, owner):
        super(GatherShip, self).__init__(type, position, owner)
        self.max_gather = 50
        self.gather_speed = 20
        self.container = [0, 0]
        self.returning = False

    def action(self, parent):
        if self.flag.flag_state == Flag.GATHER:
            self.gather(parent, parent.game)
        else:
            super(GatherShip, self).action(parent)

    def gather(self, player, game):
        resource = self.flag.final_target
        arrived = True
        if isinstance(self.flag.final_target, AstronomicalObject):
            if self.position[0] < resource.position[0] or self.position[0] > resource.position[0]:
                if self.position[1] < resource.position[1] or self.position[1] > resource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gather_speed == 0:
                    if resource.type == SolarSystem.ASTEROID:
                        if self.container[0] < self.max_gather:
                            if resource.mineralQte >= 5:
                                self.container[0] += 5
                                resource.mineralQte -= 5
                            else:
                                self.container[0] += resource.mineralQte
                                resource.mineralQte = 0
                                self.flag.initial_target = self.flag.final_target
                                self.flag.final_target = player.get_nearest_return_resource_center(self.position)
                                game.parent.redraw_mini_map()
                            self.gather_speed = self.GATHER_TIME
                        else:
                            self.flag.initial_target = self.flag.final_target
                            self.flag.final_target = player.get_nearest_return_resource_center(self.position)
                    else:
                        if self.container[1] < self.max_gather:
                            if resource.gazQte >= 5:
                                self.container[1] += 5
                                resource.gazQte -= 5
                            else:
                                self.container[1] += resource.gazQte
                                resource.gazQte = 0
                                self.flag.initial_target = self.flag.final_target
                                self.flag.final_target = player.get_nearest_return_resource_center(self.position)
                                game.parent.redraw_mini_map()
                            self.gather_speed = self.GATHER_TIME
                        else:
                            self.flag.initial_target = self.flag.final_target
                            self.flag.final_target = player.get_nearest_return_resource_center(self.position)
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
                if isinstance(self.flag.initial_target, AstronomicalObject):
                    self.flag.final_target = self.flag.initial_target
                    if self.flag.final_target.type == AstronomicalObject.ASTEROID:
                        if self.flag.final_target.mineralQte == 0:
                            player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            self.flag.flag_state = Flag.STANDBY
                    else:
                        if self.flag.final_target.gazQte == 0:
                            player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            self.flag.flag_state = Flag.STANDBY
                else:
                    self.flag.final_target = self.position
                    self.flag.flag_state = Flag.STANDBY