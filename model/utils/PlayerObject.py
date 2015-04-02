from model import *
from model.utils import Target


class PlayerObject(Target):
    def __init__(self, type, position, owner):
        super(PlayerObject, self).__init__(position)
        self.type = type
        self.flag = Flag(Target([0, 0, 0]), Target([0, 0, 0]), Flag.STANDBY)
        self.owner = owner
        self.is_alive = True
        self.constructionProgress = 0

    def get_flag(self):
        return self.flag

    def change_flag(self, final_target, state):
        if self.is_alive:
            self.flag.initial_target = Target([self.position[0], self.position[1], 0])
            self.flag.final_target = final_target
            self.flag.flag_state = state

    def take_damage(self, amount, players):
        self.hitpoints -= amount
        if self.hitpoints <= 0:
            return True
        else:
            return False

    def is_in_range(self, position, range, on_planet=False, planet_Id=-1, solar_system_Id=-1):
        if not on_planet:
            if position[0]-range < self.position[0] < position[0]+range:
                if position[1]-range < self.position[1] < position[1]+range:
                    return self
        return None
    
    def kill(self):
        self.is_alive = False