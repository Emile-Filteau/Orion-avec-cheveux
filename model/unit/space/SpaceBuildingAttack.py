from model import *
from model.unit.space import SpaceUnit


class SpaceBuildingAttack(SpaceUnit):
    def __init__(self, type, position, owner):
        super(SpaceBuildingAttack, self).__init__(type, position, owner)
        self.range = self.ATTACK_RANGE[type]
        self.attack_speed = self.ATTACK_SPEED[type]
        self.attack_damage = self.ATTACK_DAMAGE[type]
        self.attack_count = self.attack_speed
        self.kill_count = 0

    def action(self, parent):
        if self.flag.flag_state == Flag.ATTACK_BUILDING:
            self.attack(parent.game.players)
        elif self.flag.flag_state == Flag.PATROL:
            self.patrol()
        else:
            super(SpaceBuildingAttack, self).action(parent)

    def change_flag(self, final_target, state):
        self.attack_count = self.attack_speed
        Unit.change_flag(self, final_target, state)
        
    def attack(self, players):
        pos = self.flag.final_target.position
        distance = Helper.calc_distance(self.position[0], self.position[1], pos[0], pos[1])
        if distance > self.range:
            self.attack_count = 5
            self.move()
        else:
            self.attack_count -= 1
            if self.attack_count == 0:
                players[self.owner].bullets.append(Bullet([self.position[0], self.position[1], 0], self.owner, players[self.owner].units.index(self)))
                players[self.owner].bullets[len(players[self.owner].bullets)-1].change_flag(Target([pos[0], pos[1], 0]), Flag.ATTACK)
                self.attack_count = self.attack_speed

    def apply_bonuses(self, bonuses):
        super(SpaceBuildingAttack, self).apply_bonuses(bonuses)
        self.attack_speed = self.ATTACK_SPEED[self.type]+bonuses[Player.ATTACK_SPEED_BONUS]
        self.attack_damage = self.ATTACK_DAMAGE[self.type]+bonuses[Player.ATTACK_DAMAGE_BONUS]
        self.range = self.ATTACK_RANGE[self.type]+bonuses[Player.ATTACK_RANGE_BONUS]

    def get_killed_count(self):
        return self.kill_count