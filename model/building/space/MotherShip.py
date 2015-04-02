from model import *
from model.building import ConstructionBuilding

class MotherShip(ConstructionBuilding):
    MAX_ARMOR = 2000
    MAX_SHIELD = 0
    ATTACK_RANGE = 185
    ATTACK_SPEED = 25
    ATTACK_DAMAGE = 15     
    
    def __init__(self,  type, position, owner):
        super(MotherShip, self).__init__(type, position, owner)
        self.flag.final_target = Target(position)
        self.owner = owner
        self.range = self.ATTACK_RANGE
        self.attack_speed = self.ATTACK_SPEED
        self.attack_damage = self.ATTACK_DAMAGE
        self.attack_count = self.attack_speed
        self.armor = 0
        self.killCount = 0
        self.wormhole = None

    def action(self, parent):
        parent.game.check_if_enemy_in_range(self)
        if self.flag.flag_state == Flag.ATTACK:
            if isinstance(self.flag.final_target, TransportShip):
                if self.flag.final_target.landed:
                    parent.game.setAStandByFlag(self)
            killed_index = self.attack(parent.game.players)
            if killed_index[0] > -1:
                parent.kill_unit(killed_index)
        if not self.wormhole:
            if self.wormhole.duration == 0:
                self.wormhole = None
        ConstructionBuilding.action(self, parent)

    def add_unit_to_queue(self, unit_type, galaxy=None, forcebuild=False):
        position = [self.position[0], self.position[1], 0]
        unit = None
        if unit_type == Unit.SCOUT:
            unit = Unit(Unit.SCOUT, position, self.owner)
        elif unit_type == Unit.CARGO:
            unit = GatherShip(Unit.CARGO, position, self.owner)
        if forcebuild and unit:
            unit.build_time = 1
            if unit_type == Unit.CARGO:
                unit.GATHERTIME = 0
        self.unit_being_construct.append(unit)

    def apply_bonuses(self, bonuses):
        if self.finished:
            self.attack_damage = self.ATTACK_DAMAGE+bonuses[Player.ATTACK_DAMAGE_MOTHER_SHIP]
            self.shield = bonuses[Player.BUILDING_MOTHER_SHIELD_BONUS]
            self.MAX_SHIELD = bonuses[Player.BUILDING_MOTHER_SHIELD_BONUS]

    def attack(self, players, unit_to_attack=None):
        if not unit_to_attack:
            unit_to_attack = self.flag.final_target
        if not isinstance(unit_to_attack, GroundUnit):
            index = -1
            killed_owner = -1
            is_building = False
            distance = Helper.calc_distance(self.position[0], self.position[1], unit_to_attack.position[0], unit_to_attack.position[1])
            try:
                if distance > self.range:
                    self.attack_count = self.attack_speed
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
                        self.attack_count = self.attack_speed
                return index, killed_owner, is_building
            except ValueError:
                self.flag = Flag(Target(self.position), Target(self.position), Flag.BUILD_UNIT)
                return -1, -1

    def take_damage(self, amount, players):
        self.shield_regen_count = self.REGEN_WAIT_TIME
        self.shield_regen_after_attack = self.REGEN_WAIT_TIME_AFTER_ATTACK
        if self.shield > 0:
            if self.shield < amount:
                self.shield = 0
            else:
                self.shield -= amount
        elif self.armor > 0:
            if self.armor < amount:
                self.armor = 0
            else:
                self.armor -= amount
        else:
            if self.hitpoints <= amount:
                self.hitpoints = 0
                return True
            else:
                self.hitpoints -= amount
        return False
