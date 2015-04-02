from model import *
import math


class Player(object):
    MINERAL = 0
    GAS = 1
    FOOD = 2
    NUCLEAR = 3
    ATTACK_DAMAGE_BONUS = 0
    ATTACK_SPEED_BONUS = 1
    MOVE_SPEED_BONUS = 2
    ATTACK_RANGE_BONUS = 3
    VIEW_RANGE_BONUS = 4
    BUILDING_SHIELD_BONUS = 5
    BUILDING_MOTHER_SHIELD_BONUS = 6
    ATTACK_DAMAGE_MOTHER_SHIP = 7
    ATTACK_DAMAGE_BUILDING_BONUS = 8
    ABILITY_WORM_HOLE = 9
    ABILITY_WALLS = 10
    BONUS = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    MAX_FOOD = 10
    FORCE_BUILD_ACTIVATED = False
    SQUARE_FORMATION = 0
    TRIANGLE_FORMATION = 1
    
    def __init__(self, name, game, id, color_id):
        self.id = id
        self.name = name
        self.game = game
        self.color_id = color_id
        self.techTree = TechTree()
        self.selected_objects = []
        self.list_memory = [[], [], [], [], [], [], [], [], []]
        self.units = []
        self.buildings = []
        self.notifications = []
        self.planets = []
        self.bullets = []
        self.diplomacies = []
        for i in range(8):
            self.diplomacies.append('Enemy')
        self.diplomacies[self.id] = 'Ally'
        self.start_pos = [0, 0, 0]
        self.mother_ship = None
        self.mother_ships = []
        self.walls = []
        self.current_mother_ship = 0
        self.buildings_found = []
        self.formation = self.SQUARE_FORMATION
        self.current_planet = None
        self.resources = [350, 350, 2, 0]
        self.is_alive = True
        self.camera = None
        self.actionHealUnit = None

    def action(self):
        for unit in self.units:
            if unit.isAlive:
                unit.action(self)
        for building in self.buildings:
            if building.isAlive:
                building.action(self)
        for wall in self.walls:
            wall.action(self)
        for bullet in self.bullets:
            bullet.action(self)

    def add_base_units(self, start_pos):
        self.buildings.append(MotherShip(Building.MOTHERSHIP, start_pos, self.id))
        self.mother_ship = self.buildings[0]
        self.mother_ships.append(self.mother_ship)
        self.mother_ship.finished = True
        self.mother_ship.buildingTimer = Building.TIME[Building.MOTHERSHIP]
        self.mother_ship.hitpoints = self.mother_ship.maxHP
        self.mother_ship.armor = self.mother_ship.MAX_ARMOR
        self.units.append(Unit(Unit.SCOUT, [start_pos[0] + 20, start_pos[1] + 20, 0], self.id))
        self.units.append(GatherShip(Unit.CARGO, [start_pos[0] + 40, start_pos[1]+40], self.id))

    def add_camera(self, galaxy, width, height):
        pos = self.mother_ship.position
        default = [pos[0], pos[1]]
        self.camera = Camera(default, galaxy, self, width, height)
    
    def get_selected_heal_unit_index(self):
        if self.selected_objects[0].type == Unit.HEALING_UNIT:
            return self.units.index(self.selected_objects[0])
        return None

    def select_unit_to_heal(self, position):
        for unit in self.units:
            if not isinstance(unit, GroundUnit):
                if unit.select(position):
                    return unit
        for building in self.buildings:
            if not isinstance(building, GroundBuilding):
                if building.select(position):
                    return building
        return None
    
    def get_selected_building_index(self):
        return self.buildings.index(self.selected_objects[0])

    def link_waypoints(self, waypoint_id_1, waypoint_id_2, cost):
        way1 = self.buildings[waypoint_id_1]
        way2 = self.buildings[waypoint_id_2]
        if way1.has_free_wall and way2.has_free_wall:
            self.resources[self.GAS] -= cost
            wall = Wall(way1, way2)
            if way1.add_wall(wall, way2):
                if way2.add_wall(wall, way1):
                    self.walls.append(wall)
                else:
                    way1.destroy_wall(wall)
            
    def select_units_by_type(self, unit_type):
        units = []
        for selected_object in self.selected_objects:
            if selected_object.type == unit_type:
                units.append(selected_object)
        self.selected_objects = units

    def move_camera(self):
        self.camera.move()

    def change_diplomacy(self, player_to_change, new_status):
        self.diplomacies[player_to_change] = new_status

    def select_unit(self, position):
        for unit in self.units:
            if not isinstance(unit, GroundUnit):
                if unit.select(position):
                    self.selected_objects = [unit]
                    return
        for building in self.buildings:
            if not isinstance(building, GroundBuilding) and not isinstance(building, LandingZone):
                if building.select(position):
                    self.selected_objects = [building]
                    return

    def multi_select_units(self, position):
        for unit in self.units:
            if unit.select(position) and unit not in self.selected_objects:
                self.selected_objects.append(unit)

    def select_object(self, player_obj, multi):
        if player_obj:
            if isinstance(player_obj, Unit):
                if player_obj.owner == self.id:
                    if not multi:
                        self.selected_objects = [player_obj]
                    else:
                        self.selected_objects.append(player_obj)
            elif isinstance(player_obj, LandingZone):
                if player_obj.owner == self.id:
                    self.selected_objects = [player_obj]
            else:
                if not multi:
                    self.selected_objects = [player_obj]
                else:
                    self.selected_objects.append(player_obj)
    
    def select_object_from_menu(self, unit_id):
        self.selected_objects = [self.selected_objects[unit_id]]
    
    def box_select(self, select_start, select_end):
        first = True
        if not self.current_planet:
            for unit in self.units:
                if not isinstance(unit, GroundUnit):
                    unit = unit.box_select(select_start, select_end)
                    if first:
                        self.selected_objects = []
                        first = False
                    self.select_object(unit, True)
        else:
            for unit in self.current_planet.units:
                unit = unit.box_select(select_start, select_end)
                if first:
                    self.selected_objects = []
                    first = False
                self.select_object(unit, True)
    
    def select_all(self, position):
        if not self.current_planet:
            self.select_unit(position)
            first_unit = self.selected_objects[0]
            if len(self.selected_objects) > 0:
                for unit in self.units:
                    if self.camera.in_game_area(unit.position):
                        unit = unit.select(position)
                        if unit.type == first_unit.type:
                            self.select_object(unit, True)
                            
    def get_first_unit(self):
        if len(self.selected_objects) > 0:
            if isinstance(self.selected_objects[0], Unit) or isinstance(self.selected_objects[0], ConstructionBuilding):
                return self.selected_objects[0]
        return None

    def get_ship_to_unload(self):
        if self.current_planet:
            zone = self.current_planet.get_landing_spot(self.id)
            if zone and zone in self.selected_objects:
                if zone.LandedShip:
                    return zone
        return None
        
    def right_click(self, pos, player_id):
        if self.is_alive:
            if not self.is_ally(player_id) or player_id == self.id:
                for unit in self.units:
                    if unit.select(pos):
                        return unit
                mother_ship = self.mother_ship.select(pos)
                if mother_ship:
                    return mother_ship
                for building in self.buildings:
                    if building.select(pos):
                        return building                
        return None

    def select_planet(self, planet):
        if len(self.selected_objects) > 0:
            if self.selected_objects[0] == planet:
                self.look_planet(planet)
            else:
                self.selected_objects = [planet]
        else:
            self.selected_objects = [planet]
            
    def look_planet(self, planet):
        if planet.already_landed(self.id):
            self.current_planet = planet
            self.camera.place_on_landing(planet.get_landing_spot(self.id))
        
    def in_view_range(self, position):
        x = position[0]
        y = position[1]
        for i in range(len(self.game.players)):
            if self.is_ally(i):
                for unit in self.game.players[i].units:
                    if unit.isAlive and not isinstance(unit, GroundUnit):
                        if unit.position[0]-unit.viewRange < x < unit.position[0]+unit.viewRange:
                            if unit.position[1]-unit.viewRange < y < unit.position[1]+unit.viewRange:
                                if unit.type == Unit.TRANSPORT:
                                    if not unit.landed:
                                        return True
                                else:
                                    return True
                for building in self.game.players[i].buildings:
                    if building.isAlive and building.finished and not isinstance(building, GroundBuilding) and not isinstance(building, LandingZone):
                        if building.position[0]-building.viewRange < x < building.position[0]+building.viewRange:
                            if building.position[1]-building.viewRange < y < building.position[1]+building.viewRange:
                                return True
        if self.mother_ship.position[0]-self.mother_ship.viewRange < x < self.mother_ship.position[0]+self.mother_ship.viewRange:
            if self.mother_ship.position[1]-self.mother_ship.viewRange < y < self.mother_ship.position[1]+self.mother_ship.viewRange:
                return True
        return False
    
    def is_ally(self, player_id):
        if self.diplomacies[player_id] == "Ally":
            return self.game.is_allied(player_id, self.id)
        return False

    def get_nearest_return_resource_center(self, position):
        nearest_distance = Helper.calc_distance(position[0], position[1],
                                                self.mother_ships[0].position[0], self.mother_ships[0].position[1])
        nearest_building = self.mother_ships[0]
        for building in self.buildings:
            if building.type == Building.WAYPOINT or building.type == Building.MOTHERSHIP:
                if building.finished:
                    distance = Helper.calc_distance(position[0], position[1],
                                                    building.position[0], building.position[1])
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_building = building
        return nearest_building

    def get_nearest_return_resource_center_on_planet(self, position, unit):
        sun_id = unit.sunId
        planet_id = unit.planetId
        if unit.planet.get_landing_spot(unit.owner):
            landing_spot_position = unit.planet.get_landing_spot(unit.owner).position
            nearest_distance = Helper.calc_distance(position[0], position[1],
                                                    landing_spot_position[0], landing_spot_position[1])
            nearest_building = unit.planet.get_landing_spot(unit.owner)
        else:
            nearest_distance = 894382740932748
            nearest_building = unit.flag.finalTarget.position
        for building in self.buildings:
            if building.type == Building.FARM:
                if building.finished:
                    if building.sun_id == sun_id:
                        if building.planet_id == planet_id:
                            distance = Helper.calc_distance(position[0], position[1],
                                                            building.position[0], building.position[1])
                            if distance < nearest_distance:
                                nearest_distance = distance
                                nearest_building = building
        return nearest_building

    def check_if_is_attacking(self, killed_indexes):
        if killed_indexes[2]:
            unit_to_attack = self.game.players[killed_indexes[1]].buildings[killed_indexes[0]]
        else:
            unit_to_attack = self.game.players[killed_indexes[1]].units[killed_indexes[0]]
        for unit in self.units:
            if unit.isAlive:
                if unit.flag.final_target == unit_to_attack and unit.flag.flag_state == Flag.ATTACK:
                    unit.flag = Flag(Target(unit.position), Target(unit.position), Flag.STANDBY)
                    unit.attack_count = unit.attack_speed
        for building in self.buildings:
            if building.isAlive:
                if building.flag.final_target == unit_to_attack:
                    building.flag = Flag(Target(unit.position), Target(unit.position), Flag.STANDBY)
                    building.attack_count = building.attack_speed

    def check_if_can_add_notif(self, type):
        for notification in self.notifications:
            if notification.type == type:
                return False
        return True

    def kill_unit(self, killed_indexes):
        if killed_indexes[1] == self.id:
            if not killed_indexes[2]:
                if self.units[killed_indexes[0]] in self.selected_objects:
                    self.selected_objects.remove(self.units[killed_indexes[0]])
                self.units[killed_indexes[0]].kill()
                self.resources[self.FOOD] -= Unit.BUILD_COST[self.units[killed_indexes[0]].type][self.FOOD]
            else:
                if self.buildings[killed_indexes[0]] in self.selected_objects:
                    self.selected_objects.remove(self.buildings[killed_indexes[0]])
                if self.buildings[killed_indexes[0]].type == Building.WAYPOINT:
                    self.buildings[killed_indexes[0]].kill(self)
                else:
                    self.buildings[killed_indexes[0]].kill()
                    if self.buildings[killed_indexes[0]].type == Building.FARM:
                        self.MAX_FOOD -= 5
                    elif self.buildings[killed_indexes[0]].type == Building.LANDING_ZONE:
                        self.game.remove_landing_zone_from_planet(self.buildings[killed_indexes[0]])
            self.game.kill_unit(killed_indexes, False)
        else:
            self.game.kill_unit(killed_indexes, True)

    def has_unit_in_range(self, position, range, on_planet=False, planet_id=-1, solar_system_id=-1):
        for unit in self.units:
            if unit.isAlive:
                if unit.is_in_range(position, range, on_planet, planet_id, solar_system_id):
                    return unit
        for building in self.buildings:
            if building.isAlive:
                if building.is_in_range(position, range, on_planet, planet_id, solar_system_id):
                    return building
        return None

    def build_unit(self, construction_unit):
        unit = construction_unit.unitBeingConstruct.pop(0)
        unit.apply_bonuses(self.BONUS)
        unit.change_flag(Target(construction_unit.rallyPoint), Flag.MOVE)
        self.units.append(unit)
        
        if self.game.playerId == unit.owner:
            if not self.camera.in_game_area(construction_unit.position):
                if isinstance(construction_unit, MotherShip) or isinstance(construction_unit, Barrack) or isinstance(construction_unit, Utility):
                    self.notifications.append(Notification(construction_unit.position, Notification.FINISHED_BUILD, Unit.NAME[unit.type]))
                else:
                    self.notifications.append(Notification(construction_unit.planet.position, Notification.FINISHED_BUILD, Unit.NAME[unit.type]))
        
        if isinstance(unit, GroundUnit):
            self.game.galaxy.solarSystemList[unit.sunId].planets[unit.planetId].units.append(unit)

    def kill(self):
        self.is_alive = False
        for unit in self.units:
            unit.kill()
        for building in self.buildings:
            building.kill()

    def change_bonuses(self):
        for unit in self.units:
            unit.apply_bonuses(self.BONUS)
        for building in self.buildings:
            building.apply_bonuses(self.BONUS)
            
    def adjust_resources(self, resource_type, amount):
        self.resources[resource_type] += amount

    def cancel_unit(self, unit_id, construction_building):
        if construction_building < len(self.buildings):
            if unit_id < len(self.buildings[construction_building].unitBeingConstruct):
                unit = self.buildings[construction_building].get_unit_being_construct_at(unit_id)
                self.adjust_resources(self.MINERAL, unit.buildCost[0])
                self.adjust_resources(self.GAS, unit.buildCost[1])
                self.resources[self.FOOD] -= unit.buildCost[2]
                self.buildings[construction_building].unitBeingConstruct.pop(unit_id)

    def cancel_tech(self, tech_id, construction_building):
        if construction_building < len(self.buildings):
            if tech_id < len(self.buildings[construction_building].techsToResearch):
                tech = self.buildings[construction_building].techsToResearch[tech_id][0]
                self.adjust_resources(self.MINERAL, tech.costMine)
                self.adjust_resources(self.GAS, tech.costGaz)
                tech.isAvailable = True
                if tech.child:
                    tech.child.isAvailable = False
                self.buildings[construction_building].techsToResearch.pop(tech_id)

    def can_afford(self, minerals, gas, food, nuke=0):
        return self.resources[self.MINERAL] >= minerals and self.resources[self.GAS] >= gas and self.resources[self.FOOD]+food <= self.MAX_FOOD and self.resources[self.NUCLEAR] >= nuke

    def create_unit(self, unit_type, construction_building):
        if self.resources[self.MINERAL] >= Unit.BUILD_COST[unit_type][Unit.MINERAL] and self.resources[self.GAS] >= Unit.BUILD_COST[unit_type][Unit.GAS]:
            self.buildings[construction_building].add_unit_to_queue(unit_type, self.game.galaxy, self.FORCE_BUILD_ACTIVATED)
            self.resources[self.MINERAL] -= Unit.BUILD_COST[unit_type][Unit.MINERAL]
            self.resources[self.GAS] -= Unit.BUILD_COST[unit_type][Unit.GAS]
            self.resources[self.FOOD] += Unit.BUILD_COST[unit_type][Unit.FOOD]
            self.buildings[construction_building].flag.flag_state = Flag.BUILD_UNIT

    def make_ground_units_move(self, units, position, action):
        for unit in units:
            if unit != '':  # TODO: WTF
                self.units[int(unit)].change_flag(Target(position), action)

    def make_units_attack(self, units, target_player, target_unit, type):
        for unit in units:
            if unit != '':
                if int(unit) < len(self.units):
                    if type == "u":
                        self.units[int(unit)].change_flag(target_player.units[target_unit], Flag.ATTACK)
                    else:
                        self.units[int(unit)].change_flag(target_player.buildings[target_unit], Flag.ATTACK)

    def make_unit_land(self, unit_id, planet):
        self.units[unit_id].change_flag(planet, Flag.LAND)

    def make_unit_load(self, units, landing_zone):
        for unit in units:
            if unit != '':
                if int(unit) < len(self.units):
                    self.units[int(unit)].change_flag(landing_zone, Flag.LOAD)
    
    def make_units_gather(self, units, astroObject):
        for unit in units:
            if unit != '':
                if int(unit) < len(self.units):
                    self.units[int(unit)].change_flag(astroObject, Flag.GATHER)
                
    def make_ground_units_gather(self, units, resource):
        for unit in units:
            if unit != '':
                if int(unit) < len(self.units):
                    self.units[int(unit)].change_flag(resource, Flag.GROUND_GATHER)

    def make_unit_go_to_worm_hole(self, units, wormhole):
        for unit in units:
            if unit != '':
                if int(unit) < len(self.units):
                    self.units[int(unit)].change_flag(wormhole, Flag.WORMHOLE)

    def select_memory(self, selected):
        self.selected_objects = []
        for player_object in self.list_memory[selected]:
            if player_object.is_alive:
                if isinstance(player_object, GroundUnit) or isinstance(player_object, GroundBuilding) or isinstance(player_object, LandingZone):
                    self.current_planet = self.game.galaxy.solarSystemList[player_object.sun_id].planets[player_object.planet_id]
                    self.selected_objects.append(player_object)
                elif isinstance(player_object, SpaceUnit) or player_object.type == Unit.SCOUT or isinstance(player_object, SpaceBuilding) or isinstance(player_object, MotherShip) or player_object.type == Building.UTILITY or player_object.type == Building.BARRACK:
                    if self.current_planet:
                        self.current_planet = None
                        self.game.parent.view.change_background('GALAXY')
                        self.game.parent.view.redraw_mini_map()
                    self.selected_objects.append(player_object)
            else:
                self.list_memory[selected].pop(self.list_memory[selected].index(player_object))
        if len(self.selected_objects) > 0:
            if not self.current_planet:
                self.camera.position = self.camera.ensure_position_is_in_world([self.selected_objects[0].position[0], self.selected_objects[0].position[1]])
            else:
                self.camera.position = self.camera.ensure_position_is_on_planet([self.selected_objects[0].position[0], self.selected_objects[0].position[1]])

    def new_memory(self, selected):
        self.list_memory[selected] = []
        for i in self.selected_objects:
            if isinstance(i, PlayerObject):
                self.list_memory[selected].append(i)

    def calculate_final_buildings_score(self):
        score = 0
        for building in self.buildings:
            if building.finished:
                score += building.SCORE_VALUE[building.type]
        return score

    def calculate_final_units_score(self):
        score = 0
        for unit in self.units:
            score += unit.SCORE_VALUE[unit.type]
        return score

    def calculate_final_diplomacy_score(self):
        score = 0
        for diplomacy in self.diplomacies:
            if diplomacy == 'Ally':
                score += 100
        return score

    def calculate_final_resources_score(self):
        score = self.resources[self.MINERAL] + self.resources[self.GAS]
        score += self.resources[self.FOOD]*3
        score += self.resources[self.NUCLEAR]*50
        return score

    def calculate_final_killed_score(self):
        score = 0
        for unit in self.units:
            score += unit.killCount
        return score*50
    
    def make_formation(self, units, galaxy, target=None, action=Flag.MOVE):
        if len(units) > 2:
            if not target:
                if int(units[0]) < len(self.units):
                    target = self.units[int(units[0])].flag.finalTarget.position
            line_taken = []
            line = 0
            target_origin = [0, 0]
            target_origin[0] = target[0]
            target_origin[1] = target[1]
            if int(units[0]) < len(self.units):
                unit = self.units[int(units[0])]
                widths = [unit.SIZE[unit.type][0]]
                heights = [unit.SIZE[unit.type][1]]
                for i in range(0, len(units)-1):
                    if int(units[i]) < len(self.units):
                        unit = self.units[int(units[i])]
                        widths.append(unit.SIZE[unit.type][0])
                        heights.append(unit.SIZE[unit.type][1])
                width = max(widths)
                height = max(heights)
                if self.formation == self.SQUARE_FORMATION:
                    that_line = []
                    line_taken = []
                    number_of_lines = math.sqrt(len(units)-1)
                    if str(number_of_lines).split('.')[1] != '0':
                        number_of_lines += 1
                    math.trunc(float(number_of_lines))
                    number_of_lines = int(number_of_lines)
                    for l in range(0, number_of_lines):
                        that_line = []
                        for k in range(0, number_of_lines):
                            that_line.append(False)
                        line_taken.append(that_line)
                    for i in range(0, len(units)-1):
                        good_place = False
                        line = 0
                        while good_place:
                            for p in range(0, len(line_taken[line])):
                                if not line_taken[line][p]:
                                    line_taken[line][p] = True
                                    target[0] = target_origin[0]+(p*width*1.2)
                                    if target[0] < -1*(galaxy.width/2)+width:
                                        target[0] = -1*(galaxy.width/2)+width
                                    elif target[0] > (galaxy.width/2)-width:
                                        target[0] = (galaxy.width/2)-width
                                    target[1] = target_origin[1]-(line*height*1.2)
                                    if target[1] < -1*(galaxy.height/2)+height:
                                        target[1] = -1*(galaxy.height/2)+height
                                    good_place = True
                                    break
                            if not good_place:
                                line += 1
                        if int(units[i]) < len(self.units):
                            self.units[int(units[i])].change_flag(Target([target[0], target[1], 0]), int(action))
                elif self.formation == self.TRIANGLE_FORMATION:
                    that_line = []
                    x_line_before = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    that_line.append([False])
                    line_taken.append(that_line[False])
                    x_line_before[0] = target[0]
                    for i in range(0, len(units)-1):
                        good_place = False
                        line = 0
                        while not good_place:
                            for p in range(0,len(line_taken[line])):
                                if not line_taken[line][p]:
                                    line_taken[line][p] = True
                                    if line != 0:
                                        if p == len(line_taken[line-1]):
                                            target[0]=target_origin[0]+(p*width)
                                            if target[0] > (galaxy.width/2)-width:
                                                target[0] -= (target[0]-(galaxy.width/2)+width)
                                            x_line_before[p] = target[0]
                                        else:
                                            target[0] = x_line_before[p]-width
                                            if target[0] < -1*(galaxy.width/2)+(width/2):
                                                target[0] = x_line_before[p]
                                            elif target[0] > (galaxy.width/2)-(width/2):
                                                target[0] -= (target[0]-(galaxy.width/2)+width)
                                            x_line_before[p] = target[0]
                                    target[1] = target_origin[1]-(line*height)
                                    if target[1] < -1*(galaxy.height/2)+(height/2):
                                        target[1] = target_origin[1]
                                    good_place = True
                                    break
                            if not good_place:
                                line += 1
                                if (len(line_taken)-1) < line:
                                    number_of_spaces = 1+line
                                    that_line = []
                                    for a in range(0, number_of_spaces):
                                        that_line.append(False)
                                    line_taken.append(that_line)
                        if int(units[i]) < len(self.units):
                            self.units[int(units[i])].change_flag(Target([target[0], target[1], 0]), int(action))
        else:
            if int(units[0]) < len(self.units):
                self.units[int(units[0])].change_flag(Target([target[0], target[1], 0]), int(action))