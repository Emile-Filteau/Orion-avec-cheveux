from model import *
from model.unit.space import SpaceUnit


class TransportShip(SpaceUnit):
    def __init__(self, type, position, owner):
        super(TransportShip, self).__init__(type, position, owner)
        self.landed = False
        self.capacity = 10
        self.units = []
        self.planet_id = -1
        self.sun_id = -1
        self.planet = None
        self.nuclear = 0

    def action(self, parent):
        if self.flag.flag_state == Flag.LAND:
            self.land(parent.game)
        elif self.flag.flag_state == Flag.GATHER:
            self.return_to_mother_ship(parent)
        else:
            super(TransportShip, self).action(parent)

    def is_in_range(self, position, range, on_planet=False, planet_id=-1, solar_system_id=-1):
        if self.landed == on_planet and not on_planet:
            return Unit.is_in_range(self, position, range)
        return None

    def select(self, position):
        if self.isAlive and not self.landed:
            if position[0] - self.SIZE[self.type][0]/2 <= self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if position[1] - self.SIZE[self.type][1]/2 <= self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def box_select(self, start_pos, end_pos):
        if self.isAlive and not self.landed:
            if start_pos[0] - self.SIZE[self.type][0]/2 <= self.position[0] <= end_pos[0] + self.SIZE[self.type][0]/2:
                if start_pos[1] - self.SIZE[self.type][1]/2 <= self.position[1] <= end_pos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None
    
    def return_to_mother_ship(self, player):
        mother_ship = self.flag.final_target
        arrived = True
        if self.position[0] < mother_ship.position[0] or self.position[0] > mother_ship.position[0]:
            if self.position[1] < mother_ship.position[1] or self.position[1] > mother_ship.position[1]:
                arrived = False
                self.move()
        if arrived:
            player.ressources[player.NUCLEAR] += self.nuclear
            self.nuclear = 0

    def land(self, game):
        player_id = self.owner
        galaxy = game.galaxy
        planet = self.flag.final_target
        planet_id = 0
        sun_id = 0
        for i in galaxy.solarSystemList:
            for j in i.planets:
                if planet == j:
                    planet_id = i.planets.index(j)
                    sun_id = galaxy.solarSystemList.index(i)
        self.arrived = True
        if self.position[0] < planet.position[0] or self.position[0] > planet.position[0]:
            if self.position[1] < planet.position[1] or self.position[1] > planet.position[1]:
                self.arrived = False
                self.move()
        if self.arrived:
            player = game.players[player_id]
            already_landed = False
            game.parent.view.isSettingOff()
            for i in planet.landingZones:
                if i.ownerId == player_id:
                    already_landed = True
            if not already_landed:
                if len(planet.landingZones) < 4:
                    for i in planet.landingZones:
                        game.players[i.ownerId].notifications.append(Notification(planet.position, Notification.LAND_PLANET, game.players[game.playerId].name))
                    player.currentPlanet = planet
                    self.planet = planet
                    landing_zone = planet.add_landing_zone(player_id, self, game.players[player_id])
                    self.nuclear += landing_zone.nuclear
                    landing_zone.nuclear = 0
                    landing_zone.hitpoints = 100
                    player.buildings.append(landing_zone)
                    player.selectedObjects = []
                    self.landed = True
                    self.planet_id = planet_id
                    self.sun_id = sun_id
                    self.planet = planet
                    player.planets.append(planet)
                    player.planetCurrent = player.planets.index(planet)
                    if player_id == game.playerId:
                        cam = game.players[player_id].camera
                        cam.place_on_landing(landing_zone)
                    x = 40
                    for i in self.units:
                        position = [landing_zone.position[0] + x, landing_zone.position[1] + 5 * self.units.index(i)]
                        i.land(planet, position)
                        x += 25
                    del self.units[:]
                    if self in game.players[game.playerId].selectedObjects:
                        game.players[game.playerId].selectedObjects.pop(game.players[game.playerId].selectedObjects.index(self))
                    if player_id == game.playerId:
                        game.parent.change_background('PLANET')
                        game.parent.draw_planet_ground(planet)
            else:
                landing_zone = None
                for i in planet.landingZones:
                    if i.ownerId == player_id:
                        landing_zone = i
                if not landing_zone.LandedShip:
                    player.currentPlanet = planet
                    self.planet = planet
                    self.nuclear += landing_zone.nuclear
                    landing_zone.nuclear = 0
                    landing_zone.hitpoints = 100
                    self.landed = True
                    self.planet_id = planet_id
                    self.sun_id = sun_id
                    self.planet = planet
                    if player_id == game.playerId:
                        cam = game.players[player_id].camera
                        cam.place_on_landing(landing_zone)
                    x = 40
                    for i in self.units:
                        position = [landing_zone.position[0] + x, landing_zone.position[1] + 5 * self.units.index(i)]
                        i.land(planet, position)
                        x += 25
                    del self.units[:]
                    if self in game.players[game.playerId].selectedObjects:
                        game.players[game.playerId].selectedObjects.pop(game.players[game.playerId].selectedObjects.index(self))
                    landing_zone.LandedShip = self
                    if player_id == game.playerId:
                        game.parent.change_background('PLANET')
                        game.parent.draw_planet_ground(planet)
            self.flag = Flag(self.position, self.position, Flag.STANDBY)
        
    def take_off(self, planet):
        self.landed = False
        for i in planet.landingZones:
            if i.ownerId == self.owner:
                i.LandedShip = None

    def kill(self):
        self.is_alive = False

    def load(self, unit):
        unit.flag = Flag(unit.position, unit.landingZone, Flag.LOAD)