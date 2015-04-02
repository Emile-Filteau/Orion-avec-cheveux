from model import *

class Tech(object):
    def __init__(self, parent, element):
        self.parent = parent
        self.name = element.find("Name").text
        self.effect = element.find("Effect").text
        self.add = int(element.find("Add").text)
        self.cost_mine = int(element.find("CostMine").text)
        self.cost_gaz = int(element.find("CostGaz").text)
        self.research_time = 0
        self.time_needed = int(element.find("BuildTime").text)
        self.is_available = True
        if element.find("CostNuclear"):
            self.costNuclear = int(element.find("CostNuclear").text)
        else:
            self.costNuclear = 0
        if element.find("Upgrade"):
            self.child = TechUpgrade(self, element.find("Upgrade"))
        else:
            self.child = None