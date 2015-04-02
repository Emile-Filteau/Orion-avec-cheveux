from model import *


class Wall():
    ATTACK_DAMAGE = 3

    def __init__(self, wp1, wp2):
        self.wp1 = wp1
        self.wp2 = wp2
        self.owner = wp1.owner
        p1 = wp1.position
        p2 = wp2.position
        if p1[0] > p2[0]:
            self.maxX = p1[0]
            self.minX = p2[0]
        else:
            self.maxX = p2[0]
            self.minX = p1[0]
        if p1[1] > p2[1]:
            self.maxY = p1[1]
            self.minY = p2[1]
        else:
            self.maxY = p2[1]
            self.minY = p1[1]
        self.slope = Helper.calc_slope(p1, p2)
        self.origin_ordinate = Helper.calc_origin_ordinate(p1[0], p1[1], self.slope)

    def destroy(self, player):
        self.wp1 = None
        self.wp2 = None
        player.walls.remove(self)

    def action(self, player):
        units_to_attack = player.game.units_in_line(self)
        self.attack(units_to_attack, player, player.game.players)

    def attack(self, units, player, players):
        for unit in units:
            is_building = False
            if unit.take_damage(self.ATTACK_DAMAGE, players):
                if isinstance(unit, Unit):
                    index = players[unit.owner].units.index(unit)
                else:
                    index = players[unit.owner].buildings.index(unit)
                    is_building = True
                killed_owner = unit.owner
                player.kill_unit((index, killed_owner, is_building))

    def is_point_on_line(self, point):
        if point[0] > self.maxX or point[0] < self.minX:
            return False
        if point[1] > self.maxY or point[1] < self.minY:
            return False
        temp_origin_ordinate = Helper.calc_origin_ordinate(point[0], point[1], self.slope)
        return self.origin_ordinate == temp_origin_ordinate

    def is_rectangle_on_line(self, center, size):
        if self.slope < 0:
            p1 = [center[0]-size[0]/2, center[1]-size[1]/2]
            p2 = [center[0]+size[0]/2, center[1]+size[1]/2]
        else:
            p1 = [center[0]+size[0]/2, center[1]-size[1]/2]
            p2 = [center[0]-size[0]/2, center[1]+size[1]/2]
        if p1[0] > self.maxX:
            if p2[0] > self.maxX:
                return False
        if p1[0] < self.minX:
            if p2[0] < self.minX:
                return False
        if p1[1] > self.maxY:
            if p2[1] > self.maxY:
                return False
        if p1[1] < self.minY:
            if p2[1] < self.minY:
                return False
        diff1 = self.origin_ordinate - Helper.calc_origin_ordinate(p1[0], p1[1], self.slope)
        diff2 = self.origin_ordinate - Helper.calc_origin_ordinate(p2[0], p2[1], self.slope)
        if diff1 > 0:
            if diff2 <= 0:
                return True
            else:
                return False
        if diff1 < 0:
            if diff2 >= 0:
                return True
            else:
                return False
        else:
            return False
