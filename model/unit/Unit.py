# -*- coding: UTF-8 -*-
from model import *


class Unit(PlayerObject):
    DEFAULT = 0
    SCOUT = 1
    ATTACK_SHIP = 2
    TRANSPORT = 3
    CARGO = 4
    GROUND_UNIT = 5
    GROUND_GATHER = 6
    SPECIAL_GATHER = 7
    GROUND_ATTACK = 8
    GROUND_BUILDER_UNIT = 9
    HEALING_UNIT = 10
    SPACE_BUILDING_ATTACK = 11
    NYAN_CAT = 12
    NAME = ('Unité', 'Scout', 'Vaisseau d\'attaque', 'Vaisseau de Transport', 'Cargo', 'Unité terrestre', 'Unité de collecte', 'Unité spéciale', 'Unité d\'attaque', 'Unité de construction', 'Drone de Réparation', 'Unité d\'attaque lourde', 'Nyan cat')
    MINERAL = 0
    GAS = 1
    FOOD = 2
    SIZE = ((0, 0), (18, 15), (28, 32), (32, 29), (20, 30), (24, 24), (20, 38), (32, 32), (36, 33), (23, 37), (30, 37), (60, 33), (35, 25))
    MAX_HP = (50, 50, 100,125, 75, 100, 100, 100, 100,100, 100, 100, 175)
    MOVE_SPEED = (1.0,  4.0, 2.0, 3.0, 3.0, 5.0, 5.0, 3.0, 3.5, 4.0, 3.0, 1.5, 7.0)
    ATTACK_SPEED = (0, 0, 10, 0, 0, 0, 0, 0, 15, 0, 0, 125, 6)
    ATTACK_DAMAGE = (0, 0, 5, 0, 0, 0, 0, 0, 12, 0, 0, 50, 50)
    ATTACK_RANGE = (0, 0, 150, 0, 0, 0, 0, 0, 150, 0, 0, 300, 450)
    BUILD_TIME = (300, 200, 400, 300, 250, 200, 200, 200, 200, 200, 200, 500, 0)
    BUILD_COST = ((50, 50, 1), (100, 50, 1), (300, 300, 1), (300, 300, 1), (75, 0, 1), (150, 100, 1), (50, 75, 1), (75, 125, 1), (100, 80, 1), (65, 90, 1), (75, 50, 1), (400, 400, 1), (0, 0, 0))
    VIEW_RANGE = (150,  250, 200, 175, 175,200, 200, 200, 200, 200, 200, 300, 450)
    SCORE_VALUE = (10, 10, 20, 30, 15, 10, 15, 25, 20, 15, 20, 25, 50)
    
    def __init__(self, type, position, owner):
        super(Unit, self).__init__(type, position, owner)
        self.view_range = self.VIEW_RANGE[type]
        self.hitpoints = self.MAX_HP[type]
        self.max_hp = self.hitpoints
        self.build_time = self.BUILD_TIME[type]
        self.build_cost = self.BUILD_COST[type]
        self.name = self.NAME[type]
        self.move_speed = self.MOVE_SPEED[type]
        self.before = None

    def action(self, parent):
        if self.flag.flag_state == Flag.MOVE or self.flag.flag_state == Flag.GROUND_MOVE:
            self.move()
        elif self.flag.flag_state == Flag.ATTACK:
            if isinstance(self.flag.final_target, TransportShip):
                if self.flag.final_target.landed:
                    self.flag = Flag(self, self, Flag.STANDBY)
            if self.flag.flag_state == Flag.ATTACK:
                killed_index = self.attack(parent.game.players)
                if killed_index[0] > -1:
                    parent.kill_unit(killed_index)
        elif self.flag.flag_state == Flag.PATROL:
            self.patrol()
        elif self.flag.flag_state == Flag.BUILD:
            self.build(self.flag.final_target, parent)
        elif self.flag.flag_state == Flag.WORMHOLE:
            self.go_to_worm_hole(parent)

    def move(self):
        if Helper.calc_distance(self.position[0], self.position[1], self.flag.final_target.position[0], self.flag.final_target.position[1]) <= self.move_speed:
            end_pos = [self.flag.final_target.position[0], self.flag.final_target.position[1]]
            self.position = end_pos
            if self.flag.flag_state == Flag.MOVE or self.flag.flag_state == Flag.GROUND_MOVE:
                self.flag.flag_state = Flag.STANDBY
            elif self.flag.flag_state == Flag.MOVE + Flag.ATTACK:
                self.flag.flag_state = Flag.ATTACK
        else:
            angle = Helper.calc_angle(self.position[0], self.position[1], self.flag.final_target.position[0], self.flag.final_target.position[1])
            temp = Helper.get_angled_point(angle, self.move_speed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]

    def patrol(self):
        arrived = True
        if self.position[0] < self.flag.final_target.position[0] or self.position[0] > self.flag.final_target.position[0]:
                if self.position[1] < self.flag.final_target.position[1] or self.position[1] > self.flag.final_target.position[1]:
                    self.move()
                    arrived = False
        if arrived:
            self.before = self.flag.initial_target
            self.flag.initial_target = self.flag.final_target
            self.flag.final_target = self.before
            self.move()
        return None

    def go_to_worm_hole(self, player):
        wormhole = self.flag.final_target
        arrived = True
        if self.position[0] < self.flag.final_target.position[0] or self.position[0] > self.flag.final_target.position[0]:
            if self.position[1] < self.flag.final_target.position[1] or self.position[1] > self.flag.final_target.position[1]:
                self.move()
                arrived = False
        if arrived:
            temp = [wormhole.destination[0], wormhole.destination[1]]
            self.position = temp
            self.flag.flag_state = Flag.STANDBY

    def select(self, position):
        if self.isAlive:
            if position[0] - self.SIZE[self.type][0]/2 <= self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if position[1] - self.SIZE[self.type][1]/2 <= self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def box_select(self, start_pos, end_pos):
        if self.isAlive:
            if start_pos[0] - self.SIZE[self.type][0]/2 < self.position[0] < end_pos[0] + self.SIZE[self.type][0]/2:
                if start_pos[1] - self.SIZE[self.type][1]/2 < self.position[1] < end_pos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def build(self, building, player):
        if Helper.calc_distance(self.position[0], self.position[1], self.flag.final_target.position[0], self.flag.final_target.position[1]) >= self.move_speed:
            self.move()
        else:
            end_pos = [self.flag.final_target.position[0], self.flag.final_target.position[1]]
            self.position = end_pos
            
            if building.building_timer < building.build_time:
                building.building_timer += 1
                building.hitpoints += (1/building.build_time)*building.MAX_HP[building.type]
            else:
                building.finished = True
                if building.hitpoints >= building.MAX_HP[building.type]-1:
                    building.hitpoints = building.MAX_HP[building.type]
                self.flag.flag_state = Flag.STANDBY
                if isinstance(building, Mothership):
                    building.armor = Mothership.MAX_ARMOR
                building.apply_bonuses(player.BONUS)

    def erase_unit(self):
        self.flag.flag_state = 0
        self.position = [-1500,-1500,0]

    def apply_bonuses(self, bonuses):
        self.move_speed = self.MOVE_SPEED[self.type]+bonuses[Player.MOVE_SPEED_BONUS]
        self.view_range = self.VIEW_RANGE[self.type]+bonuses[Player.VIEW_RANGE_BONUS]

    def get_flag(self):
        return self.flag

    def get_killed_count(self):
        return 0
