from model import *
from model.building.space import SpaceBuilding


class Waypoint(SpaceBuilding):
    def __init__(self, type, position, owner):
        super(Waypoint, self).__init__(type, position, owner)
        self.linked_waypoint1 = None
        self.wall1 = None
        self.linked_waypoint2 = None
        self.wall2 = None

    def has_free_wall(self):
        if not self.wall1:
            return True
        if not self.wall2:
            return True
        return False

    def add_wall(self, wall, wp2):
        if not self.wall1 and self.linked_waypoint2 != wp2:
            self.linked_waypoint1 = wp2
            self.wall1 = wall
            return True
        elif not self.wall2 and self.linked_waypoint1 != wp2:
            self.linked_waypoint2 = wp2
            self.wall2 = wall
            return True
        else:
            return False

    def destroy_wall(self, wall):
        if self.wall1 == wall:
            self.linked_waypoint1 = None
            self.wall1 = None
        elif self.wall2 == wall:
            self.linked_waypoint2 = None
            self.wall2 = None
            
    def kill(self, player=None):
        if not player:
            if not self.wall1:
                self.wall1.destroy(player)
                self.linked_waypoint1.destroy_wall(self.wall1)
                self.destroy_wall(self.wall1)
            if not self.wall2:
                self.wall2.destroy(player)
                self.linked_waypoint2.destroy_wall(self.wall2)
                self.destroy_wall(self.wall2)
        self.is_alive = False