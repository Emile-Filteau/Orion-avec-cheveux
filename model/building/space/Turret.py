from model import *
from model.building.space import SpaceBuilding

class Turret(SpaceBuilding):
    ATTACK_SPEED = 12
    ATTACK_DAMAGE = 6
    ATTACK_RANGE = 175

    def __init__(self, type, position, owner):
        super(Turret, self).__init__(type, position, owner)
        self.range = self.ATTACK_RANGE
        self.attack_speed = self.ATTACK_SPEED
        self.attack_damage = self.ATTACK_DAMAGE
        self.attack_count = self.attack_speed
        self.killCount = 0

    def action(self, parent):
        if self.finished:
            if self.flag.flag_state == Flag.ATTACK:
                killed_indexes = self.attack(parent.game.players)
                if killed_indexes[0] > -1:
                    parent.kill_unit(killed_indexes)
            else:
                parent.game.check_if_enemy_in_range(self)

    def attack(self, players, unit_to_attack=None):
        if not unit_to_attack:
            unit_to_attack = self.flag.final_target
        index = -1
        killed_owner = -1
        is_building = False
        distance = Helper.calc_distance(self.position[0], self.position[1], unit_to_attack.position[0], unit_to_attack.position[1])
        try:
            if distance <= self.range:
                self.attack_count -= self.attack_count
                if self.attack_count == 0:
                    if unit_to_attack.take_damage(self.attack_damage, players):
                        if not isinstance(unit_to_attack, Building):
                            index = players[unit_to_attack.owner].units.index(unit_to_attack)
                        else:
                            index = players[unit_to_attack.owner].buildings.index(unit_to_attack)
                            is_building = True
                        killed_owner = unit_to_attack.owner
                        for i in players[self.owner].units:
                            if i.isAlive:
                                if i.flag.final_target == unit_to_attack:
                                    i.flag = Flag(Target(i.position), Target(i.position), Flag.STANDBY)
                                    i.attack_count = i.AttackSpeed
                        self.killCount += 1
                    self.attack_count = self.attack_speed
            else:
                self.flag = Flag(Target(self.position), Target(self.position), Flag.STANDBY)
            return index, killed_owner, is_building
        except ValueError:
            self.flag = Flag(Target(self.position), Target(self.position), Flag.STANDBY)
            return -1, -1, is_building

    def change_flag(self, final_target, state):
        if self.isAlive:
            self.flag.initial_target = Target([self.position[0], self.position[1], 0])
            self.flag.final_target = final_target
            self.flag.flag_state = state

    def apply_bonuses(self, bonuses):
        if self.finished:
            self.attack_speed = self.ATTACK_SPEED+bonuses[Player.ATTACK_SPEED_BONUS]
            self.attack_damage = self.ATTACK_DAMAGE+bonuses[Player.ATTACK_DAMAGE_BUILDING_BONUS]
            self.range = self.ATTACK_RANGE+bonuses[Player.ATTACK_RANGE_BONUS]
            Building.apply_bonuses(self, bonuses)
