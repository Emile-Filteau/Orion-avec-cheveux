from model import *
from model.unit.space import SpaceUnit


class NyanCat(SpaceUnit):

    def __init__(self,  type, position, owner):
        super(NyanCat, self).__init__(type, position, owner)
        self.range = self.ATTACK_RANGE[type]
        self.attack_speed = self.ATTACK_SPEED[type]
        self.attack_damage = self.ATTACK_DAMAGE[type]
        self.attack_count = self.attack_speed
        self.kill_count = 0

    def action(self, parent):
        if self.flag.flag_state == Flag.ATTACK:
            if isinstance(self.flag.final_target, TransportShip):
                if self.flag.final_target.landed:
                    self.flag = Flag(self, self, Flag.STANDBY)
            if self.flag.flag_state == Flag.ATTACK:
                killed_index = self.attack(parent.game.players)
                if killed_index[0] > -1:
                    parent.kill_unit(killed_index)
        elif self.flag.flag_state == Flag.PATROL:
            self.patrol()
        else:
            super(NyanCat, self).action(parent)

    def change_flag(self, final_target, state):
        self.attack_count = self.attack_speed
        Unit.change_flag(self, final_target, state)
        
    def attack(self, players, unit_to_attack=None):
        if not unit_to_attack:
            unit_to_attack = self.flag.final_target
        index = -1
        killed_owner = -1
        is_building = False
        distance = Helper.calc_distance(self.position[0], self.position[1], unit_to_attack.position[0], unit_to_attack.position[1])
        try:
            if distance > self.range :
                self.attack_count=self.attack_speed
                self.move()
            else:
                self.attack_count -= 1
                if self.attack_count == 0:
                    if unit_to_attack.take_damage(self.attack_damage, players):
                        if not isinstance(unit_to_attack, Building):
                            index = players[unit_to_attack.owner].units.index(unit_to_attack)
                        else:
                            index = players[unit_to_attack.owner].buildings.index(unit_to_attack)
                            is_building = True
                        killed_owner = unit_to_attack.owner
                        self.kill_count += 1
                        if self.kill_count % 2 == 1:
                            self.attack_damage += 1
                    self.attack_count = self.attack_speed
            return index, killed_owner, is_building
        except ValueError:
            self.flag = Flag(Target(self.position), Target(self.position), Flag.STANDBY)
            return -1, -1

    def get_killed_count(self):
        return self.kill_count