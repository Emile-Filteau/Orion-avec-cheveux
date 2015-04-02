# -*- coding: UTF-8 -*-
from model import *


class Building(PlayerObject):
    WAYPOINT = 0
    UTILITY = 1
    BARRACK = 2
    FARM = 3
    TURRET = 4
    MOTHERSHIP = 5
    LANDING_ZONE = 6
    LAB = 7
    NAME = ("Point ralliement", "Utilités", "Barraque", "Ferme", "Tourette", "Vaisseau mere", "Zone d'aterrissage","Laboratoire de recherche")
    SIZE = ((30, 30), (75, 70), (75, 80), (75, 59), (32, 32), (125, 125), (32, 32), (94, 94))
    INSPACE = (True, True, True, False, True, True, False, False)
    COST = ((50, 50), (250, 250), (300, 300), (75, 75), (250, 200), (2000, 2000), (0, 0), (300, 300))
    TIME = (125, 250, 250, 125, 125, 1250, 0, 250)
    MAX_HP = (150, 250, 250, 200, 200, 1500, 100, 200)
    VIEW_RANGE = (200, 200, 200, 100, 250, 400, 200, 100)
    SCORE_VALUE = (15, 10, 10, 10, 20, 50, 15, 30)
    MAX_SHIELD = 0
    REGEN_WAIT_TIME = 30
    REGEN_WAIT_TIME_AFTER_ATTACK = 60
    
    def __init__(self, type, position, owner):
        PlayerObject.__init__(self, type, position, owner)
        self.building_timer = 0
        self.view_range = self.VIEW_RANGE[type]
        self.hitpoints = 0
        self.max_hp = self.MAX_HP[type]
        self.build_time = self.TIME[type]
        self.build_cost = self.COST[type]
        self.name = self.NAME[type]
        self.finished = False
        self.shield = 0
        self.shield_regen_count = self.REGEN_WAIT_TIME
        self.shield_regen_after_attack = 0

    def action(self, parent):
        if self.finished:
            self.regen_shield()

    def regen_shield(self):
        if self.shield_regen_after_attack > 0:
            self.shield_regen_after_attack -= 1
        elif self.shield_regen_count > 0:
            self.shield_regen_count -= 1
        else:
            if self.shield > self.MAX_SHIELD-5:
                self.shield = self.MAX_SHIELD
            else:
                self.shield += 5
                self.shield_regen_count = self.REGEN_WAIT_TIME
                    
    def take_damage(self, amount, players):
        self.shield_regen_count = self.REGEN_WAIT_TIME
        self.shield_regen_after_attack = self.REGEN_WAIT_TIME_AFTER_ATTACK
        if self.shield > 0:
            if self.shield < amount:
                self.shield = 0
            else:
                self.shield -= amount
        else:
            if self.hitpoints <= amount:
                self.hitpoints = 0
                return True
            else:
                self.hitpoints -= amount
        return False

    def select(self, position):
        if self.isAlive:
            if position[0] - self.SIZE[self.type][0]/2 <= self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if position[1] - self.SIZE[self.type][1]/2 <= self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def select_icon(self, start_pos, end_pos):
        if self.isAlive:
            if start_pos[0] - self.SIZE[self.type][0]/2 < self.position[0] < end_pos[0] + self.SIZE[self.type][0]/2:
                if start_pos[1] - self.SIZE[self.type][1]/2 < self.position[1] < end_pos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def apply_bonuses(self, bonuses):
        if self.finished:
            self.shield = bonuses[Player.BUILDING_SHIELD_BONUS]
            self.MAX_SHIELD = bonuses[Player.BUILDING_SHIELD_BONUS]