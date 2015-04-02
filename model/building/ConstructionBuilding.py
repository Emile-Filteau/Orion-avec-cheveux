from model import *
from model.building import Building


class ConstructionBuilding(Building):
    def __init__(self, type, position, owner):
        super(ConstructionBuilding, self).__init__(type, position, owner)
        self.unit_being_construct = []
        self.rallyPoint = [position[0], position[1]+(self.SIZE[type][1]/2)+5, 0]

    def progress_units_construction(self):
        if len(self.unit_being_construct) > 0:
            self.flag.flag_state = Flag.BUILD_UNIT
            self.unit_being_construct[0].constructionProgress += 1
        else:
            self.flag.flag_state = Flag.STANDBY

    def get_unit_being_construct_at(self, unit_id):
        return self.unit_being_construct[unit_id]

    def is_unit_finished(self):
        if len(self.unit_being_construct) > 0:
            return self.unit_being_construct[0].constructionProgress >= self.unit_being_construct[0].buildTime

    def action(self, parent):
        if self.finished:
            if self.flag.flag_state == Flag.CHANGE_RALLY_POINT:
                target = self.flag.final_target
                self.rallyPoint = [target[0], target[1], 0]
                self.flag.flag_state = Flag.BUILD_UNIT

            if self.flag.flag_state != Flag.ATTACK and self.flag.flag_state != Flag.BUILD_UNIT:
                self.flag.flag_state = Flag.STANDBY

            self.progress_units_construction()

            if len(self.unit_being_construct) > 0:
                if self.is_unit_finished():
                    parent.build_unit(self)

