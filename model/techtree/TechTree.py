# -*- coding: UTF-8 -*-
from xml.etree.ElementTree import *
from model import *


class TechTree(object):
    UNITS = 0
    BUILDINGS = 1
    MOTHER_SHIP = 2
    
    def __init__(self):
        self.unit_techs = []
        self.building_techs = []
        self.mother_ship_techs = []
        tree = ElementTree(file="TechTree.xml")
        units = tree.find("Units")
        for u in units.findall("Tech"):
            self.unit_techs.append(Tech(self, u))

        buildings = tree.find("Buildings")
        for b in buildings.findall("Tech"):
            self.building_techs.append(Tech(self, b))

        mother_ships = tree.find("Mothership")
        for m in mother_ships.findall("Tech"):
            self.mother_ship_techs.append(Tech(self, m))

    def buy_upgrade(self, name, branch, tech=None):
        if not tech:
            for i in self.get_branch(branch):
                if self.get_names(branch)[self.get_branch(branch).index(i)] == name:
                    tech = i
                    break
        if not tech.isAvailable:
            if tech.child:
                return self.buy_upgrade(tech.name, branch, tech.child)
            else:
                return None
        else:
            tech.isAvailable = False
            return tech

    def get_upgrade(self, name, branch, tech=None):
        if not tech:
            for i in self.get_branch(branch):
                if self.get_names(branch)[self.get_branch(branch).index(i)] == name:
                    tech = i
                    break
        if not tech.isAvailable:
            if not tech.child:
                return self.get_upgrade(name, branch, tech.child)
            else:
                return None
        else:
            return tech

    def get_names(self, branch):
        names = []
        for i in self.get_branch(branch):
            tech = self.get_upgrade(i.name, branch, i)
            if tech:
                names.append(tech.name)
        return names

    def get_techs(self, branch):
        techs = []
        for i in self.get_branch(branch):
            tech = self.get_upgrade(i.name, branch, i)
            if tech:
                techs.append(tech)
        return techs

    def get_branch(self, branch):
        if branch == self.UNITS:
            return self.unit_techs
        elif branch == self.BUILDINGS:
            return self.building_techs
        elif branch == self.MOTHER_SHIP:
            return self.mother_ship_techs
