from model import *
from model.unit.ground import GroundUnit


class GroundAttackUnit(GroundUnit):
    def __init__(self,  type, position, owner, planet_id, sun_id, is_landed=False):
        super(GroundAttackUnit, self).__init__(type, position, owner, planet_id, sun_id, is_landed)
        self.range = self.ATTACK_RANGE[type]
        self.attack_speed = self.ATTACK_SPEED[type]
        self.attack_damage = self.ATTACK_DAMAGE[type]
        self.attack_count = self.attack_speed
        self.killCount = 0

    def action(self, parent):
        if self.is_landed:
            if self.flag.flag_state == Flag.ATTACK:
                killed_index = self.attack(parent.game.players)
                if killed_index[0] > -1:
                    parent.kill_unit(killed_index)
            elif self.flag.flag_state == Flag.PATROL:
                self.patrol()
                parent.game.check_if_enemy_in_range(self, True, self.planet_id, self.sun_id)
            elif self.flag.flag_state == Flag.STANDBY:
                parent.game.check_if_enemy_in_range(self, True, self.planet_id, self.sun_id)
            else:
                super(GroundAttackUnit, self).action(parent)

    def attack(self, players, unit_to_attack=None):
        if not unit_to_attack:
            unit_to_attack = self.flag.final_target
        index = -1
        killed_owner = -1
        is_building = False
        distance = Helper.calc_distance(self.position[0], self.position[1], unit_to_attack.position[0], unit_to_attack.position[1])
        try:
            if distance > self.range:
                self.attack_count = self.attack_speed
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
                        self.killCount += 1
                        if self.killCount % 2 == 1:
                            self.attack_damage += 1
                    self.attack_count = self.attack_speed
            return index, killed_owner, is_building
        except ValueError:
            self.flag = Flag(Target(self.position), Target(self.position), Flag.STANDBY)
            return -1, -1

    def apply_bonuses(self, bonuses):
        super(GroundAttackUnit, self).apply_bonuses(bonuses)
        self.attack_speed = self.ATTACK_SPEED[self.type]+bonuses[Player.ATTACK_SPEED_BONUS]
        self.attack_damage = self.ATTACK_DAMAGE[self.type]+bonuses[Player.ATTACK_DAMAGE_BONUS]
        self.range = self.ATTACK_RANGE[self.type]+bonuses[Player.ATTACK_RANGE_BONUS]

    def get_killed_count(self):
        return self.killCount