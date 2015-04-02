from model import *
from model.building.ground import GroundBuilding


class Lab(GroundBuilding):
    def __init__(self, type, position, owner, sun_id, planet_id):
        super(Lab, self).__init__(type, position, owner, sun_id, planet_id)
        self.techs_to_research = []

    def action(self, parent):
        if self.finished:
            if len(self.techs_to_research) > 0:
                self.progress_techs(parent)

    def progress_techs(self, player):
        self.techs_to_research[0][0].researchTime += 1
        if self.techs_to_research[0][0].researchTime >= self.techs_to_research[0][0].timeNeeded:
            player.BONUS[self.techs_to_research[0][1]] = self.techs_to_research[0][0].add
            self.techs_to_research[0][0].is_available = False
            if not self.techs_to_research[0][0].child:
                self.techs_to_research[0][0].child.is_available = True
            player.notifications.append(Notification([-10000, -10000, -10000], Notification.FINISH_TECH, self.techs_to_research[0][0].name))
            self.techs_to_research.pop(0)
            player.change_bonuses()