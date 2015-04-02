from model import *
from model.unit.space import SpaceUnit


class HealingUnit(SpaceUnit):

        def __init__(self, type, position, owner):
            super(HealingUnit, self).__init__(type, position, owner)
            self.units_to_heal = []
            self.HEALING_RANGE = 50
            self.HEALING_SPEED = 40
            self.HEALING_POWER = 1
            self.ctr = 0

        def action(self, parent):
            if self.flag.flag_state == Flag.HEAL:
                target = self.flag.final_target
                if (Helper.calc_distance(self.position[0], self.position[1], target.position[0], target.position[1])) >= self.HEALING_RANGE:
                    self.move()
                else:
                    self.ctr += 1
                    if self.ctr == self.HEALING_SPEED and self.flag.final_target.hitpoints < self.flag.final_target.max_hp:
                        self.flag.final_target.hitpoints += self.HEALING_POWER
                        self.ctr = 0
                    elif self.flag.final_target.hitpoints >= self.flag.final_target.max_hp:
                        self.flag.final_target.hitpoints = self.flag.final_target.max_hp
                        self.flag.flag_state = Flag.STANDBY
                
            else:
                super(HealingUnit, self).action(parent)