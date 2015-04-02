from model import *
from model.utils import PlayerObject

class Bullet(PlayerObject):
    def __init__(self, position, owner, unit_id):
        super(Bullet, self).__init__(666, position, owner)
        self.range = 100
        self.moveSpeed = 7.0
        self.AttackDamage = 50.0
        self.unit_id = unit_id
        self.arrived = False
        self.to_show = 10

    def action(self, player):
        distance = Helper.calc_distance(self.position[0], self.position[1], self.flag.final_target.position[0], self.flag.final_target.position[1])
        if not self.arrived:
            if distance > 1:
                self.move()
            else:
                is_building = False
                players = player.game.players
                units_to_attack = player.game.has_unit_in_range(self)
                for unit in units_to_attack:
                    damage_to_take = self.AttackDamage-(Helper.calc_distance(self.position[0], self.position[1], unit.position[0], unit.position[1])/2)
                    if damage_to_take < 0:
                        damage_to_take = 0
                    if unit.take_damage(damage_to_take, players):
                        if isinstance(unit, Unit):
                            index = players[unit.owner].units.index(unit)
                        else:
                            index = players[unit.owner].buildings.index(unit)
                            is_building = True
                        killed_owner = unit.owner
                        player.units[self.unit_id].killCount += 1
                        if player.units[self.unit_id].killCount % 4 == 1:
                            self.AttackDamage += 1
                        player.kill_unit((index, killed_owner, is_building))
                self.arrived = True

    def move(self):
        if Helper.calc_distance(self.position[0], self.position[1], self.flag.final_target.position[0], self.flag.final_target.position[1]) <= self.moveSpeed:
            end_pos = [self.flag.final_target.position[0], self.flag.final_target.position[1]]
            self.position = end_pos
        else:
            angle = Helper.calc_angle(self.position[0], self.position[1], self.flag.final_target.position[0], self.flag.final_target.position[1])
            temp = Helper.get_angled_point(angle, self.moveSpeed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]