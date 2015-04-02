# -*- coding: UTF-8 -*-
from model.utils import *


class Notification(Target):
    ATTACKED_UNIT = 0
    ATTACKED_BUILDING = 1
    ALLIANCE_ALLY = 2
    ALLIANCE_DEMAND_ALLY = 3
    ALLIANCE_ENEMY = 4
    MESSAGE_ALLIES = 5
    MESSAGE_ALL = 6
    LAND_PLANET = 7
    FINISHED_BUILD = 8
    FINISH_GATHER = 9
    FINISH_TECH = 10
    NOT_ENOUGH_RESOURCES = 11
    PING = 12
    NOT_ENOUGH_POPULATION = 13
    NAME = ("Un de vos vaisseaux se fait attaquer par ", "Un de vos bâtiments se fait attaquer par ", "Vous êtes maintenant allié avec ", "Vous avez reçu une demande d'alliance de ", "Vous êtes maintenant l'ennemi de ", "", "", "Votre planète est maintenant aussi habitée par ", "Une nouvelle unité a été créée: ", "Une de vos unités a fini de collecter", "Une nouvelle technologie vient d'être terminée : ", "Vous manquez de resources.", "Vous êtes demandé à cet endroit par : ", "La population maximale a été atteinte.")
    COLOR = ("RED", "RED", "GREEN", "YELLOW", "RED", "GREEN", "CYAN", "GRAY", "WHITE", "WHITE", "WHITE", "WHITE", "YELLOW", "WHITE")

    def __init__(self, position, notification_type, action_player_name=None):
        super(Notification, self).__init__(position)
        self.notification_type = notification_type
        self.refresh_seen = 0
        self.color = self.COLOR[notification_type]
        self.name = self.NAME[notification_type]
        self.actionPlayerName = ''
        if action_player_name:
            self.actionPlayerName = action_player_name
            self.name += action_player_name