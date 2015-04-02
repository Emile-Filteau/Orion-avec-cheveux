import random
from model import *


class AI(Player):
    def __init__(self, name, game, id, color_id):
        Player.__init__(self, name, game, id, color_id)
        self.action_frame = 60
        self.current_frame = 0
        self.priority = (1, 4, 3, 2)
        self.max_units = (2, 5, 1, 40)
        self.enemy_discovered = []
        self.minerals_time = True
        self.diplomacies = ['Enemy', 'Enemy', 'Enemy', 'Enemy', 'Enemy', 'Enemy', 'Enemy', 'Enemy']
                
    def action(self):
        Player.action(self)
        if self.current_frame == self.action_frame:
            self.actions()
            self.current_frame = 0
        else:
            self.current_frame += 1

    def actions(self):
        self.do_your_stuff_on_planets()
        self.decision_build_unit()
        self.send_units_to_attack_discovered()
        self.explore(1200)
        self.check_if_saw_enemy()
        self.check_if_building_are_not_finished()
        self.check_if_enemy_in_range()
        self.check_resources()
             
    def find_resource(self):
        self.minerals_time = not self.minerals_time
        for solar_system in self.game.galaxy.solarSystemList:
            if self.minerals_time:
                for nebula in solar_system.nebulas:
                    if self.game.players[self.id].in_view_range(nebula.position) and nebula.gazQte > 0:
                        return nebula
                for asteroid in solar_system.asteroids:
                    if self.game.players[self.id].in_view_range(asteroid.position) and asteroid.mineralQte > 0:
                        return asteroid
            else:
                for asteroid in solar_system.asteroids:
                    if self.game.players[self.id].in_view_range(asteroid.position) and asteroid.mineralQte > 0:
                        return asteroid
                for nebula in solar_system.nebulas:
                    if self.game.players[self.id].in_view_range(nebula.position) and nebula.gazQte > 0:
                        return nebula
        return None

    def send_cargo(self, resource):
        sent_one = False
        for i in self.units:
            if i.isAlive:
                if i.type == Unit.CARGO:
                    if i.flag.flagState != Flag.GATHER:
                        i.change_flag(resource, Flag.GATHER)
                        sent_one = True
        return sent_one
                    
    def explore(self, move_range):
        for unit in self.units:
            if unit.isAlive:
                if unit.type == Unit.SCOUT or (unit.type == Unit.CARGO and unit.flag.flagState != Flag.GATHER) or (unit.type == Unit.ATTACK_SHIP and unit.flag.flagState != Flag.ATTACK):
                    if unit.flag.flagState != Flag.BUILD or unit.flag.flagState != Flag.MOVE:
                        x = random.randint(-1*move_range, move_range)
                        y = random.randint(-1*move_range, move_range)
                        while unit.position[0]+x < (self.game.galaxy.width/2)*-1 or unit.position[0]+x > self.game.galaxy.width/2:
                            x = random.randint(-1*move_range, move_range)
                        while unit.position[1]+y < (self.game.galaxy.height/2)*-1 or unit.position[1]+y > self.game.galaxy.height/2:
                            y = random.randint(-1*move_range, move_range)
                        unit.change_flag(Target([unit.position[0]+x, unit.position[1]+y, 0]), Flag.MOVE)

    def do_your_stuff_on_planets(self):
        if len(self.planets) == 0:
            self.send_transport_to_planet()
        for p in self.planets:
            self.check_resources_planets(p)
            if self.get_ground_builders(p) == 0:
                if len(self.units) > 9:
                    self.units[9].kill()
                self.build(Unit.GROUND_BUILDER_UNIT)
            if self.number_of_stacks(p) > self.get_ground_gathers(p):
                for i in range(self.get_ground_gathers(p), self.number_of_stacks(p)):
                    self.build(Unit.GROUND_GATHER)

    def number_of_stacks(self, planet):
        stacks = 0
        for mineral_stack in planet.minerals:
            if mineral_stack.nb_minerals > 0:
                stacks += 1
        for gaz_stack in planet.gaz:
            if gaz_stack.nb_gaz > 0:
                stacks += 1
        return stacks

    def send_units_to_attack_discovered(self):
        if self.nb_units(Unit.ATTACK_SHIP) > 2:
            if self.nb_units(Unit.ATTACK_SHIP) % 5 == 2:
                self.build(Unit.SPACE_BUILDING_ATTACK)
            if len(self.enemy_discovered) > 0:
                self.send_to_attack_enemy()

    def check_if_building_are_not_finished(self):
        scout = self.get_nearest_scout_from_mother_ship()
        if scout:
            if scout.flag.flagState != Flag.BUILD:
                for building in self.buildings:
                    if not building.finished:
                        scout.change_flag(building, Flag.BUILD)

    def check_if_saw_enemy(self):
        for unit in self.units:
            for player in self.game.players:
                if player != self:
                    for building in player.buildings:
                        if building.isAlive:
                            if isinstance(building, SpaceBuilding) or isinstance(building, MotherShip):
                                if building.type != Building.WAYPOINT:
                                    if building.is_in_range(unit.position, unit.viewRange):
                                        if not self.is_not_already_in_enemies_discovered(building):
                                            self.enemy_discovered.append(building)

    def is_not_already_in_enemies_discovered(self, building):
        for _building in self.enemy_discovered:
            if building == _building:
                return True
        return False

    def check_resources(self):
        resource = self.find_resource()
        if resource:
            if self.send_cargo(resource):
                nearest_build = self.get_nearest_return_resource_center(resource.position)
                if Helper.calc_distance(resource.position[0], resource.position[1], nearest_build.position[0], nearest_build.position[1]) > 300:
                    self.build_building(Building.WAYPOINT, resource)

    def check_resources_planets(self, planet):
        resource = self.find_resource_planet(planet)
        if resource:
            self.send_ground_gather(resource)
            return True
        else:
            if planet.get_landing_spot(self.id).landed_ship:
                landing_zone = planet.get_landing_spot(self.id)
                to_range = len(planet.units)
                if to_range > 10:
                    to_range = 10
                for unit in range(0, to_range):
                    if planet.units[unit].owner == self.id:
                        if planet.units[unit].flag.flagState != Flag.LOAD:
                            planet.units[unit].change_flag(landing_zone, Flag.LOAD)
                units = 0
                for unit in planet.units:
                    if unit.owner == self.id:
                        units += 1
                if units == 0 or len(landing_zone.LandedShip.units) == 10:
                    self.game.take_off(landing_zone.LandedShip, planet, self.id)
                    self.send_transport_to_planet()
            return False

    def get_ground_gathers(self, planet):
        gatherers = 0
        for unit in planet.units:
            if unit.owner == self.id:
                if unit.type == Unit.GROUND_GATHER:
                    gatherers += 1
        for unit in planet.get_landing_spot(self.id).unitBeingConstruct:
            if unit.type == Unit.GROUND_GATHER:
                gatherers += 1
        return gatherers

    def send_ground_gather(self, ressource):
        sent_one = False
        for unit in self.units:
            if unit.isAlive:
                if unit.type == Unit.GROUND_GATHER:
                    if unit.flag.flagState != Flag.GROUND_GATHER:
                        unit.change_flag(ressource, Flag.GROUND_GATHER)
                        sent_one = True
        return sent_one

    def find_resource_planet(self, planet):
        for mineral_stack in planet.minerals:
            if mineral_stack.nb_minerals > 0:
                return mineral_stack
        for gaz in planet.gaz:
            if gaz.nb_gaz > 0:
                return gaz
        return None

    def send_transport_to_planet(self):
        for unit in self.units:
            if unit.isAlive:
                if unit.type == Unit.TRANSPORT:
                    if unit.flag.flagState != Flag.LAND:
                        planet = self.get_nearest_planet(unit.position)
                        unit.change_flag(planet, Flag.LAND)

    def get_nearest_planet(self, position):
        distance = 9999999
        planet = None
        for solar_system in self.game.galaxy.solarSystemList:
            for planet in solar_system.planets:
                if not planet.get_landing_spot(self.id):
                    planet_distance = Helper.calc_distance(position[0], position[1], planet.position[0], planet.position[1])
                    if planet_distance < distance:
                        distance = planet_distance
                        planet = planet
        return planet
            
    def decision_build_unit(self):
        have_built = False
        for i in self.priority:
            if (self.priority.index(i) > 1 and not have_built) or self.priority.index(i) <= 1:
                if self.need_build(i):
                    have_built = True
                    self.build(i)

    def build(self, unit_type):
        if self.can_afford(Unit.BUILD_COST[unit_type][self.MINERAL], Unit.BUILD_COST[unit_type][self.GAS], Unit.BUILD_COST[unit_type][self.FOOD]):
            building = self.get_stand_by_building(unit_type)
            if building:
                self.resources[self.MINERAL] -= Unit.BUILD_COST[unit_type][Unit.MINERAL]
                self.resources[self.GAS] -= Unit.BUILD_COST[unit_type][Unit.GAS]
                self.resources[self.FOOD] += Unit.BUILD_COST[unit_type][Unit.FOOD]
                building.addUnitToQueue(unit_type, self.game.galaxy)
                return 0
        elif self.resources[self.FOOD]+Unit.BUILD_COST[unit_type][self.FOOD] > self.MAX_FOOD:
            if len(self.planets) == 0:
                self.send_transport_to_planet()
            else:
                if not self.have_farm_under_construction(self.planets[0]):
                    self.build_building(Building.FARM, self.planets[0])

    def have_farm_under_construction(self, planet):
        for building in self.buildings:
            if building.is_alive:
                if building.type == Building.FARM:
                    if not building.finished:
                        return True
        return False
    
    def have_building(self, unit_type):
        for building in self.buildings:
            if building.is_alive:
                if building.type == unit_type:
                    return True
        return False
    
    def need_build(self, unit_type):
        if self.nb_units(unit_type) < self.max_units[self.priority.index(unit_type)]:
            if unit_type in (Unit.SCOUT, Unit.CARGO):
                return True
            elif unit_type == Unit.TRANSPORT:
                if self.have_building(Building.UTILITY):
                    return True
                else:
                    self.build_building(Building.UTILITY)
            elif unit_type in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK):
                if self.have_building(Building.BARRACK):
                    return True
                else:
                    self.build_building(Building.BARRACK)
            elif unit_type in (Unit.GROUND_ATTACK, Unit.SPECIAL_GATHER):
                if self.have_building(Building.LANDING_ZONE):
                    return True
                else:
                    self.send_transport_to_planet()
        return False

    def build_building(self, building_type, resource=None):
        if self.can_afford(Building.COST[building_type][self.MINERAL], Building.COST[building_type][self.GAS],0):
            if Building.INSPACE[building_type]:
                scout = self.get_nearest_scout_from_mother_ship()
                if scout:
                    building_position = self.get_position_build(building_type, resource)
                    self.game.build_building(self.id, building_position, Flag.BUILD, [str(self.units.index(scout))], building_type)
            elif len(self.planets) > 0:
                planet = resource
                builder = self.get_nearest_builder_from_landing_zone(planet)
                if builder:
                    sun_id = self.game.galaxy.solarSystemList.index(planet.solarSystem)
                    planet_id = self.game.galaxy.solarSystemList[sun_id].planets.index(planet)
                    building_position = self.get_ground_position_build(building_type, planet)
                    if building_position:
                        self.game.build_building(self.id, building_position, Flag.BUILD, [str(self.units.index(builder))], building_type, sun_id, planet_id)

    def get_ground_builders(self, planet):
        builders = 0
        for unit in planet.units:
            if unit.owner == self.id:
                if unit.is_alive:
                    if unit.type == Unit.GROUND_BUILDER_UNIT:
                        builders += 1
        for unit in planet.get_landing_spot(self.id).unitBeingConstruct:
            if unit.type == Unit.GROUND_BUILDER_UNIT:
                builders += 1
        return builders

    def get_nearest_builder_from_landing_zone(self, planet):
        landing_pos = planet.get_landing_spot(self.id).position
        distance = 9999999
        unit = None
        for unit in self.units:
            if unit.is_alive:
                if unit.type == Unit.GROUND_BUILDER_UNIT:
                    if unit.planet == planet:
                        if unit.flag.flagState != Flag.BUILD:
                            unit_distance = Helper.calc_distance(unit.position[0], unit.position[1], landing_pos[0], landing_pos[1])
                            if unit_distance < distance:
                                distance = unit_distance
                                unit = unit
        return unit

    def get_nearest_scout_from_mother_ship(self):
        distance = 99999999
        scout = None
        for unit in self.units:
            if unit.is_alive:
                if unit.type == Unit.SCOUT:
                    if unit.flag.flagState != Flag.BUILD:
                        unit_distance = Helper.calc_distance(unit.position[0], unit.position[1], self.mother_ships[0].position[0], self.mother_ships[0].position[1])
                        if unit_distance < distance:
                            distance = unit_distance
                            scout = unit
        return scout

    def check_if_enemy_in_range(self):
        for unit in self.units:
            if unit.type in (Unit.ATTACK_SHIP, Unit.SCOUT, Unit.SPACE_BUILDING_ATTACK):
                for player in self.game.players:
                    if player.is_alive:
                        if player.id != self.id and not self.game.players[self.id].is_ally(player.id or isinstance(player, AI)):
                            enemy_unit = player.has_unit_in_range(unit.position, unit.viewRange)
                            if enemy_unit:
                                attack_ship = self.get_first_attack_ship_stand_by(enemy_unit.position)
                                if attack_ship:
                                    if attack_ship.type == Unit.ATTACK_SHIP:
                                        attack_ship.change_flag(enemy_unit, Flag.ATTACK)
                                    else:
                                        attack_ship.change_flag(enemy_unit, Flag.ATTACK_BUILDING)

    def get_first_attack_ship_stand_by(self, enemy_position):
        distance = 985943
        attack = None
        for unit in self.units:
            if unit.is_alive:
                if unit.type in (unit.ATTACK_SHIP, unit.SPACE_BUILDING_ATTACK):
                    if unit.flag.flagState != Flag.ATTACK:
                        unit_distance = Helper.calc_distance(unit.position[0], unit.position[1], enemy_position[0], enemy_position[1])
                        if unit_distance < distance:
                            distance = unit_distance
                            attack = unit
        return attack

    def send_to_attack_enemy(self):
        send_to_attack = []
        for attacks in self.units:
            if attacks.is_alive:
                if attacks.type in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK):
                    send_to_attack.append(attacks)
        if send_to_attack[len(send_to_attack)-1].type != Unit.SPACE_BUILDING_ATTACK:
            send_to_attack.pop(len(send_to_attack)-1)
        if not self.enemy_discovered[0].isAlive:
            self.enemy_discovered.pop(0)
        if len(self.enemy_discovered) > 0:
            for att in send_to_attack:
                if att.type == Unit.ATTACK_SHIP:
                    att.change_flag(self.enemy_discovered[0], Flag.ATTACK)
                else:
                    att.change_flag(self.enemy_discovered[0], Flag.ATTACK_BUILDING)

    def get_position_build(self, build_type, resource=None):
        self.current_planet = None
        if build_type != Building.WAYPOINT and Building.INSPACE[build_type]:
            position = self.mother_ships[0].position
            x = random.randint(int(position[0])-250, int(position[0])+250)
            y = random.randint(int(position[1])-250, int(position[1])+250)
            while not self.game.check_if_can_build([x, y, 0], build_type, 0, self.id):
                x = random.randint(int(position[0])-250, int(position[0])+250)
                y = random.randint(int(position[1])-250, int(position[1])+250)
        else:
            resource_position = resource.position
            x = random.randint(int(resource_position[0])-50, int(resource_position[0])+50)
            y = random.randint(int(resource_position[1])-50, int(resource_position[1])+50)
            while not self.game.check_if_can_build([x, y, 0], build_type, 0, self.id):
                x = random.randint(int(resource_position[0])-50, int(resource_position[0])+50)
                y = random.randint(int(resource_position[1])-50, int(resource_position[1])+50)
        if x < -1*(self.game.galaxy.width/2):
            x = -1*(self.game.galaxy.width/2) + Building.SIZE[build_type][0]
        elif x > (self.game.galaxy.width/2):
            x = -1*(self.game.galaxy.width/2) - Building.SIZE[build_type][0]
        if y < -1*(self.game.galaxy.height/2):
            y = -1*(self.game.galaxy.height/2) + Building.SIZE[build_type][1]
        elif y > (self.game.galaxy.height/2):
            y = (self.game.galaxy.height/2) - Building.SIZE[build_type][1]
        return x, y, 0

    def get_ground_position_build(self, build_type, planet):
        if len(planet.units) > 0:
            self.current_planet = planet
            unit = self.get_nearest_builder_from_landing_zone(planet)
            x = random.randint(int(unit.position[0])-250, int(unit.position[0])+250)
            y = random.randint(int(unit.position[1])-250, int(unit.position[1])+250)
            while not self.game.check_if_can_build([x, y, 0], build_type, self.units.index(unit), self.id):
                x = random.randint(int(unit.position[0])-250, int(unit.position[0])+250)
                y = random.randint(int(unit.position[1])-250, int(unit.position[1])+250)
            if x < 0:
                x = Building.SIZE[build_type][0]
            elif x > planet.WIDTH:
                x = planet.WIDTH - Building.SIZE[build_type][0]
            if y < 0:
                y = Building.SIZE[build_type][1]
            elif y > planet.HEIGHT:
                y = planet.HEIGHT - Building.SIZE[build_type][1]
            return x, y, 0
        return None
            
    def get_stand_by_building(self, unitType):
        if unitType == Unit.CARGO or unitType == Unit.SCOUT:
            for mother_ship in self.mother_ships:
                if mother_ship.is_alive:
                    if mother_ship.finished:
                        return mother_ship
        else:
            for building in self.buildings:
                if building.is_alive:
                    if building.finished:
                        if (building.type == Building.UTILITY and unitType == Unit.TRANSPORT) or (building.type == Building.BARRACK and unitType in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK)) or (building.type == Building.LANDING_ZONE and unitType in (Unit.GROUND_GATHER, Unit.GROUND_BUILDER_UNIT, Unit.GROUND_ATTACK, Unit.SPECIAL_GATHER)):
                            return building
            return None
    
    def nb_units(self, unit_type):
        nb = 0
        for unit in self.units:
            if unit.is_alive:
                if unit.type == unit_type:
                    nb += 1
        for building in self.buildings:
            if building.is_alive:
                if isinstance(building, ConstructionBuilding):
                    for unit in building.unit_being_construct:
                        if unit.is_alive:
                            if unit.type == unit_type:
                                nb += 1
        return nb

    def in_view_range(self, position):
        x = position[0]
        y = position[1]
        for unit in self.units:
            if unit.is_alive and not isinstance(unit, GroundUnit):
                if unit.position[0]-unit.viewRange < x < unit.position[0]+unit.viewRange:
                    if unit.position[1]-unit.viewRange < y < unit.position[1]+unit.viewRange:
                        if unit.type == Unit.TRANSPORT:
                            if not unit.landed:
                                return True
                        else:
                            return True
        for building in self.buildings:
            if building.isAlive and building.finished and not isinstance(building, GroundBuilding) and not isinstance(building, LandingZone):
                if building.position[0]-building.viewRange < x < building.position[0]+building.viewRange:
                    if building.position[1]-building.viewRange < y < building.position[1]+building.viewRange:
                        return True
        if self.mother_ship.position[0]-self.mother_ship.viewRange < x < self.mother_ship.position[0]+self.mother_ship.viewRange:
            if self.mother_ship.position[1]-self.mother_ship.viewRange < y < self.mother_ship.position[1]+self.mother_ship.viewRange:
                return True
        return False