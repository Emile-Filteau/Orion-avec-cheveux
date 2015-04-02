from model import *
import math

from view.View import *


class Game():
    def __init__(self, controller):
        self.parent = controller
        self.players = []
        self.player_id = 0
        self.messages = []
        self.changes = []
        self.id_trade_with = self.player_id
        self.trade_page = -1
        self.is_master_of_trade = False
        self.multi_select = False
        self.galaxy = None

    def start(self, players, seed, width, height):
        self.galaxy = Galaxy(len(players), seed)
        self.players = players
        for player in self.players:
            start_pos = self.galaxy.get_spawn_point()
            player.add_base_units(start_pos)
        self.get_my_player().add_camera(self.galaxy, width, height)

    def action(self):
        self.get_my_player().camera.move()
        self.parent.view.gameArea.delete('enemyRange')
        for wormhole in self.galaxy.wormholes:
            if wormhole.duration > 0:
                wormhole.action()
        for player in self.players:
            if player.is_alive:
                player.action()
        return self.get_my_player().is_alive

    def get_my_player(self):
        return self.players[self.player_id]
    
    def heal_unit_for_real(self, action_player_id, target, heal_unit_index):
        if target[1] == 0:
            self.players[action_player_id].units[heal_unit_index].change_flag(self.players[action_player_id].units[int(target[0])], Flag.HEAL)
        else:
            self.players[action_player_id].units[heal_unit_index].change_flag(self.players[action_player_id].buildings[int(target[0])], Flag.HEAL)

    def select_unit_to_heal(self, pos):
        to_heal = self.get_my_player().select_unit_to_heal(pos)
        if to_heal:
            if isinstance(to_heal, Unit):
                type_to_heal = 0
            elif isinstance(to_heal, Building):
                type_to_heal = 1
            else:
                type_to_heal = 2
            if type_to_heal != 2:
                self.set_action_heal_unit(to_heal, type_to_heal)
    
    def set_action_heal_unit(self, to_heal, type_to_heal):
        if type_to_heal == 0:
            to_heal_index = self.get_my_player().units.index(to_heal)
        elif type_to_heal == 1:
            to_heal_index = self.get_my_player().buildings.index(to_heal)
        healer_unit_index = self.get_my_player().get_selected_heal_unit_index()
        if healer_unit_index:
            self.parent.push_change(healer_unit_index, Flag(finalTarget=Target([to_heal_index, type_to_heal, 0]), flagState=Flag.HEAL))

    def make_notification(self, action_player_id, target, unit_index):
        player = self.players[target[0]]
        action_player_name = self.players[action_player_id].name
        add_it = True
        notification = None
        if not target[1] in (Notification.MESSAGE_ALL, Notification.MESSAGE_ALLIES, Notification.PING):
            if target[1] == Notification.ATTACKED_UNIT:
                for i in player.notifications:
                        if i.position == player.units[target[2]].position and i.actionPlayerName == action_player_name:
                            add_it = False
                if add_it:
                    if not isinstance(player.units[target[2]], GroundUnit):
                        notification = Notification(player.units[target[2]].position, target[1], action_player_name)
                    else:
                        for planet in player.planets:
                            for unit in planet.units:
                                if unit == player.units[target[2]]:
                                    notification = Notification(planet.position, target[1], action_player_name)
                                    break
            elif target[1] == Notification.ATTACKED_BUILDING:
                for i in player.notifications:
                    if i.position == player.buildings[target[2]].position and i.actionPlayerName == action_player_name:
                        add_it = False
                if add_it:
                    if Building.INSPACE[player.buildings[target[2]].type]:
                        notification = Notification(player.buildings[target[2]].position, target[1], action_player_name)
                    else:
                        notification = Notification(player.buildings[target[2]].planet.position, target[1], action_player_name)
            if notification:
                player.notifications.append(notification)
        else:
            mess = ""
            for i in unit_index:
                mess += i
            mess = action_player_name + " : " + mess
            if target[1] == Notification.MESSAGE_ALL:
                notification = Notification([-10000, -10000, -10000], target[1], mess)
                if self.player_id != player.id:
                    self.get_my_player().notifications.append(notification)
            elif target[1] == Notification.MESSAGE_ALLIES:
                notification = Notification([-10000, -10000, -10000], target[1], mess)
                if player.is_ally(self.player_id):
                    if self.player_id != player.id:
                        self.get_my_player().notifications.append(notification)
            elif target[1] == Notification.PING:
                notification = Notification([target[2], target[3], 0], target[1], action_player_name)
                if player.is_ally(self.player_id):
                    if self.player_id != player.id:
                        if self.get_my_player().check_if_can_add_notif(Notification.PING):
                            self.get_my_player().notifications.append(notification)

    def set_building_flag(self, x, y, type, sun_id=0, planet_id=0):
        units = ''
        for selected_object in self.get_my_player().selectedObjects:
            if selected_object.type in (selected_object.SCOUT, selected_object.GROUND_BUILDER_UNIT):
                units += str(self.get_my_player().units.index(selected_object)) + ","
        if self.get_my_player().ressources[0] >= Building.COST[type][0] and self.get_my_player().ressources[1] >= Building.COST[type][1]:
            if Building.INSPACE[type]:
                self.parent.push_change(units, Flag((type, 0), Target([x, y, 0]), Flag.BUILD))
            else:
                self.parent.push_change(units, Flag((type, sun_id, planet_id), Target([x, y, 0]), Flag.BUILD))

    def build_building(self, player_id, target, flag, unit_index, type, sun_id=None, planet_id=None):
        wp = None
        if self.check_if_can_build((target[0], target[1],0), type, int(unit_index[0]), player_id, sunId=sun_id, planetId=planet_id):
            player = self.players[player_id]
            if player.ressources[0] >= Building.COST[type][0] and player.ressources[1] >= Building.COST[type][1]:
                player.ressources[0] -= Building.COST[type][0]
                player.ressources[1] -= Building.COST[type][1]
                if type == Building.WAYPOINT:
                    wp = Waypoint(Building.WAYPOINT, [target[0], target[1], 0], player_id)
                elif type == Building.UTILITY:
                    wp = Utility(Building.UTILITY, [target[0], target[1], 0], player_id)
                elif type == Building.BARRACK:
                    wp = Barrack(Building.BARRACK, [target[0], target[1], 0], player_id)
                elif type == Building.TURRET:
                    wp = Turret(Building.TURRET, [target[0], target[1], 0], player_id)
                elif type == Building.FARM:
                    wp = Farm(Building.FARM, [target[0], target[1], 0], player_id, sun_id, planet_id)
                    wp.planet = self.galaxy.solarSystemList[sun_id].planets[planet_id]
                    self.galaxy.solarSystemList[sun_id].planets[planet_id].buildings.append(wp)
                elif type == Building.LAB:
                    wp = Lab(Building.LAB, [target[0], target[1], 0], player_id, sun_id, planet_id)
                    wp.planet = self.galaxy.solarSystemList[sun_id].planets[planet_id]
                    self.galaxy.solarSystemList[sun_id].planets[planet_id].buildings.append(wp)
                elif type == Building.MOTHERSHIP:
                    wp = MotherShip(Building.MOTHERSHIP, [target[0], target[1], 0], player_id)
                    self.players[player_id].motherships.append(wp)
            if wp:
                if self.players[player_id].FORCE_BUILD_ACTIVATED:
                    wp.build_time = 1
                self.players[player_id].buildings.append(wp)
                for i in unit_index:
                    if i != '':
                        self.players[player_id].units[int(i)].change_flag(wp, flag)

    def resume_building_flag(self, building):
        units = ''
        selected_object = None
        for selected_object in self.get_my_player().selectedObjects:
            if selected_object.type in (selected_object.SCOUT, selected_object.GROUND_BUILDER_UNIT):
                units += str(self.get_my_player().units.index(selected_object)) + ","
        if not building.finished:
            self.parent.push_change(units, Flag(selected_object, building, Flag.FINISH_BUILD))

    def resume_building(self, player_id, building, unit_index):
        for i in unit_index:
            if i != '':
                if int(i) < len(self.players[player_id].units):
                    self.players[player_id].units[int(i)].change_flag(self.players[player_id].buildings[building], Flag.BUILD)

    def set_moving_flag(self, x, y):
        units = ''
        send = False
        if y > self.galaxy.height/2:
            y = self.galaxy.height/2-15
        selected_object = None
        for selected_object in self.get_my_player().selectedObjects:
            if isinstance(selected_object, Unit):
                units += str(self.get_my_player().units.index(selected_object)) + ","
                send = True
        if send:
            self.parent.push_change(units, Flag(selected_object, Target([x, y, 0]), Flag.MOVE))
            
    def set_ground_moving_flag(self, x, y):
        units = ''
        for i in self.get_my_player().selectedObjects:
            if isinstance(i, Unit):
                units += str(self.get_my_player().units.index(i))+ ","
        self.parent.push_change(units, Flag(Target([0, 0, 0]), Target([x, y, 0]), Flag.GROUND_MOVE))

    def set_default_moving_flag(self, x, y, unit):
        units = ''
        units += str(self.get_my_player().units.index(unit)) + ","
        self.parent.push_change(units, Flag(unit, Target([x, y, 0]), Flag.MOVE))

    def set_standby_flag(self):
        units = ""
        for i in self.get_my_player().selectedObjects:
            if isinstance(i, Unit):
                units += str(self.get_my_player().units.index(i)) + ","
        if units != "":
            self.parent.push_change(units, Flag(Target([0, 0, 0]), Target([0, 0, 0]), Flag.STANDBY))

    def set_patrol_flag(self, pos):
        units = ''
        send = False
        i = None
        for i in self.get_my_player().selectedObjects:
            if isinstance(i, Unit):
                units += str(self.get_my_player().units.index(i)) + ","
                send = True
        if send:
            self.parent.push_change(units, Flag(i, Target([pos[0], pos[1], 0]), Flag.PATROL))

    def set_attack_flag(self, attacked_unit):
        attacking = True
        if attacking:
            units = ""
            for i in self.get_my_player().selectedObjects:
                if isinstance(i, SpaceAttackUnit) or isinstance(i, NyanCat):
                    if isinstance(attacked_unit, Unit):
                        if attacked_unit.type == Unit.TRANSPORT:
                            if not attacked_unit.landed:
                                units += str(self.get_my_player().units.index(i)) + ","
                        else:
                            units += str(self.get_my_player().units.index(i)) + ","
                    else:
                        units += str(self.get_my_player().units.index(i)) + ","
                elif isinstance(i, GroundAttackUnit):
                    units += str(self.get_my_player().units.index(i)) + ","
            if units != "":
                self.parent.push_change(units, Flag(i, attacked_unit, Flag.ATTACK))
                if isinstance(attacked_unit, Unit):
                    self.parent.push_change(None, Flag(None, [attacked_unit.owner, Notification.ATTACKED_UNIT, self.players[attacked_unit.owner].units.index(attacked_unit)], Flag.NOTIFICATION))
                else:
                    self.parent.push_change(None, Flag(None, [attacked_unit.owner, Notification.ATTACKED_BUILDING, self.players[attacked_unit.owner].buildings.index(attacked_unit)], Flag.NOTIFICATION))

    def set_attack_building_flag(self, pos):
        units = ''
        for i in self.get_my_player().selectedObjects:
            if i.type == Unit.SPACE_BUILDING_ATTACK:
                units += str(self.get_my_player().units.index(i)) + ","
        self.parent.push_change(units, Flag(None, pos, Flag.ATTACK_BUILDING))

    def make_space_building_attack(self, player_id, target, unit_id):
        for i in unit_id:
            if i != '':
                if int(i) < len(self.players[player_id].units):
                    self.players[player_id].units[int(i)].change_flag(Target(target), Flag.ATTACK_BUILDING)

    def set_an_attack_flag(self, attacked_unit, unit):
        units = ""
        if attacked_unit.type == Unit.TRANSPORT:
            if not attacked_unit.landed:
                unit.attack_count = unit.attack_speed
                units += str(self.players[unit.owner].units.index(unit)) + ","
        else:
            unit.attack_count = unit.attack_speed
            units += str(self.players[unit.owner].units.index(unit)) + ","
        if units != "":
            self.parent.push_change(units, Flag(unit.owner, attacked_unit, Flag.ATTACK))

    def set_worm_hole_flag(self, wormhole):
        units = ""
        for i in self.get_my_player().selectedObjects:
            if isinstance(i, Unit):
                units += str(self.get_my_player().units.index(i)) + ","
        self.parent.push_change(units, Flag(self.player_id, wormhole, Flag.WORMHOLE))

    def make_unit_go_to_wormhole(self, units, player_id, worm_hole_id):
        wormhole = self.galaxy.wormholes[worm_hole_id]
        self.players[player_id].make_unit_go_to_worm_hole(units, wormhole)

    def make_units_attack(self, player_id, units, target_player, target_unit, type):
        self.players[player_id].make_units_attack(units, self.players[target_player], target_unit, type)

    def kill_unit(self, killed_indexes, has_to_kill = True):
        if has_to_kill:
            self.players[killed_indexes[1]].kill_unit(killed_indexes)
            if killed_indexes[2]:
                if isinstance(self.players[killed_indexes[1]].buildings[killed_indexes[0]], LandingZone):
                    self.players[killed_indexes[1]].planets.remove(self.players[killed_indexes[1]].buildings[killed_indexes[0]].planet)
                elif isinstance(self.players[killed_indexes[1]].buildings[killed_indexes[0]], MotherShip):
                    mother_ship = self.players[killed_indexes[1]].buildings[killed_indexes[0]]
                    if self.players[killed_indexes[1]].motherships.index(mother_ship) == 0:
                        if len(self.players[killed_indexes[1]].motherships) >= 2:
                            self.players[killed_indexes[1]].mother_ship = self.players[killed_indexes[1]].buildings[killed_indexes[0]+1]
                    self.players[killed_indexes[1]].motherships.remove(self.players[killed_indexes[1]].buildings[killed_indexes[0]])
                    die = True
                    for i in self.players[killed_indexes[1]].motherships:
                        if i.is_alive:
                            die = False
                            break
                    if die:
                        self.kill_player(killed_indexes[1])
            else:
                if isinstance(self.players[killed_indexes[1]].units[killed_indexes[0]], TransportShip):
                    for un in self.players[killed_indexes[1]].units[killed_indexes[0]].units:
                        self.kill_unit((self.players[killed_indexes[1]].units.index(un), killed_indexes[1], killed_indexes[2]))
        for play in self.players:
            play.check_if_is_attacking(killed_indexes)

    def remove_landing_zone_from_planet(self, landing_zone):
        planet = self.galaxy.solarSystemList[landing_zone.sunId].planets[landing_zone.planetId]
        if landing_zone in planet.landing_zones:
            planet.landing_zones.remove(landing_zone)

    def add_building_enemy(self, building_found, is_finished):
        for building in self.get_my_player().buildingsFound:
            if building[0] == building_found:
                building[1] = is_finished
                return None
        self.get_my_player().buildingsFound.append([building_found, is_finished])

    def set_buy_tech(self, tech_type, index):
        self.parent.push_change(tech_type, Flag(0, Target([int(index), self.get_my_player().get_selected_building_index(), 0]), Flag.BUY_TECH))

    def buy_tech(self, player_id, tech_type, index, lab_index):
        player = self.players[player_id]
        tech_tree = player.techTree
        if tech_type == "Button_Buy_Unit_Tech":
            tech = tech_tree.get_techs(tech_tree.UNITS)[index]
        elif tech_type == "Button_Buy_Building_Tech":
            tech = tech_tree.get_techs(tech_tree.BUILDINGS)[index]
        elif tech_type == "Button_Buy_MotherShip_Tech":
            tech = tech_tree.get_techs(tech_tree.MOTHERSHIP)[index]
        if player.ressources[0] >= tech.costMine and player.ressources[1] >= tech.costGaz and player.ressources[3] >= tech.costNuclear:
            if tech_type == "Button_Buy_Unit_Tech":
                tech = tech_tree.buy_upgrade(tech_tree.get_techs(tech_tree.UNITS)[index].name,tech_tree.UNITS, tech)
            elif tech_type == "Button_Buy_Building_Tech":
                tech = tech_tree.buy_upgrade(tech_tree.get_techs(tech_tree.BUILDINGS)[index].name,tech_tree.BUILDINGS, tech)
            elif tech_type == "Button_Buy_MotherShip_Tech":
                tech = tech_tree.buy_upgrade(tech_tree.get_techs(tech_tree.MOTHERSHIP)[index].name,tech_tree.MOTHERSHIP, tech)
            player.ressources[0] -= tech.costMine
            player.ressources[1] -= tech.costGaz
            player.ressources[3] -= tech.costNuclear
            if lab_index < len(player.buildings) and isinstance(player.buildings[lab_index], Lab):
                if player.FORCE_BUILD_ACTIVATED:
                    tech.timeNeeded = 1
                if tech.effect == 'D':
                    player.buildings[lab_index].techsToResearch.append((tech, player.ATTACK_DAMAGE_BONUS))
                elif tech.effect == 'DB':
                    player.buildings[lab_index].techsToResearch.append((tech, player.ATTACK_DAMAGE_BUILDING_BONUS))
                elif tech.effect == 'S':
                    player.buildings[lab_index].techsToResearch.append((tech, player.MOVE_SPEED_BONUS))
                elif tech.effect == 'AS':
                    player.buildings[lab_index].techsToResearch.append((tech, player.ATTACK_SPEED_BONUS))
                elif tech.effect == 'AR':
                    player.buildings[lab_index].techsToResearch.append((tech, player.ATTACK_RANGE_BONUS))
                elif tech.effect == 'TN':
                    player.buildings[lab_index].techsToResearch.append((tech, player.ABILITY_WORM_HOLE))
                elif tech.effect == 'M':
                    player.buildings[lab_index].techsToResearch.append((tech, player.ABILITY_WALLS))
                elif tech.effect == 'VR':
                    player.buildings[lab_index].techsToResearch.append((tech, player.VIEW_RANGE_BONUS))
                elif tech.effect == 'BB':
                    player.buildings[lab_index].techsToResearch.append((tech, player.BUILDING_SHIELD_BONUS))
                elif tech.effect == 'BM':
                    player.buildings[lab_index].techsToResearch.append((tech, player.BUILDING_MOTHERSHIELD_BONUS))
                elif tech.effect == 'DM':
                    player.buildings[lab_index].techsToResearch.append((tech, player.ATTACK_DAMAGE_MOTHERSHIP))
        else:
            player.notifications.append(Notification([-10000, -10000, -10000], Notification.NOT_ENOUGH_RESSOURCES))
        
    def set_gather_flag(self, ship, resource):
        units = str(self.get_my_player().units.index(ship)) + ","
        self.parent.push_change(units, Flag(Target([0, 0, 0]), resource, Flag.GATHER))

    def set_all_gather_flag(self, resource):
        units = ""
        for i in self.get_my_player().selectedObjects:
            if i.type == Unit.CARGO:
                units += str(self.get_my_player().units.index(i)) + ","
        self.parent.push_change(units, Flag(Target([0, 0, 0]), resource, Flag.GATHER))

    def make_units_gather(self, player_id, units_id, solar_system_id, astro_object_d, astro_object_type):
        if astro_object_type == AstronomicalObject.NEBULA:
            astro_object = self.galaxy.solarSystemList[solar_system_id].nebulas[astro_object_d]
        elif astro_object_type == AstronomicalObject.ASTEROID:
            astro_object = self.galaxy.solarSystemList[solar_system_id].asteroids[astro_object_d]
        elif astro_object_type == Building.WAYPOINT:
            astro_object = self.players[player_id].buildings[astro_object_d]
        else:
            astro_object = self.players[player_id].motherShip
        self.players[player_id].make_units_gather(units_id, astro_object)

    def set_ground_gather_flag(self, ship, resource):
        units = str(self.get_my_player().units.index(ship)) + ","
        self.parent.push_change(units, Flag(Target([0,0,0]), resource, Flag.GROUND_GATHER))

    def set_all_ground_gather_flag(self, resource):
        units = ""
        for i in self.get_my_player().selectedObjects:
            if i.type == Unit.GROUND_GATHER:
                units += str(self.get_my_player().units.index(i)) + ","
        self.parent.push_change(units, Flag(Target([0,0,0]), resource, Flag.GROUND_GATHER))
        
    def make_ground_unit_move(self, player_id, units_id, pos_x, pos_y, pos_z, action):
        self.players[int(player_id)].make_ground_units_move(units_id, [pos_x, pos_y, pos_z], int(action))

    def make_ground_units_gather(self, player_id, units_id, resource_id, planet_id, sun_id, resource_type):
        if resource_type == "mine":
            resource = self.galaxy.solarSystemList[sun_id].planets[planet_id].minerals[resource_id]
        elif resource_type == "gaz":
            resource = self.galaxy.solarSystemList[sun_id].planets[planet_id].gaz[resource_id]
        elif resource_type == "nuclear":
            resource = self.galaxy.solarSystemList[sun_id].planets[planet_id].nuclearSite
        elif resource_type == "landing":
            resource = self.galaxy.solarSystemList[sun_id].planets[planet_id].landingZones[resource_id]
        else:  # resource_type == "farm"
            resource = self.players[player_id].buildings[sun_id]
        if isinstance(resource, LandingZone):
            if not resource.landed_ship:
                self.players[player_id].make_ground_units_gather(units_id, resource)
        else:
            self.players[player_id].make_ground_units_gather(units_id, resource)

    def set_trade_flag(self, items, player_id_2, quantity):
        for i in items:
            self.parent.push_change(player_id_2, Flag(i, quantity[items.index(i)], Flag.TRADE))

    def ask_trade(self, name, index, mode):
        id_other_player = -1
        for player in self.players:
            if player.is_alive:
                if player.name == self.parent.view.menuModes.variableTrade.get():
                    id_other_player = player.id
                    break
        if id_other_player != -1:
            self.parent.push_change(id_other_player, Flag(1, "askTrade", Flag.TRADE))
            self.trade_page = 1
            self.id_trade_with = id_other_player
            self.parent.view.ongletTradeWaiting()

    def stop_trade(self):
        self.parent.push_change(self.id_trade_with, Flag(5, "stopTrade", Flag.TRADE))

    def start_trade(self, answer, id1):
        if answer:
            self.parent.push_change(id1, Flag(2, "startTrade", Flag.TRADE))
        else:
            self.parent.push_change(id1, Flag(3, "deniedTrade", Flag.TRADE))
            self.parent.view.ongletTradeChoicePlayer()

    def confirm_trade_question(self, id2):
        try:
            if int(self.parent.view.menuModes.spinMinerals1.get()) <= self.get_my_player().ressources[0] and int(self.parent.view.menuModes.spinGaz1.get()) <= self.get_my_player().ressources[1]:
                if int(self.parent.view.menuModes.spinMinerals2.get()) <= self.players[self.id_trade_with].ressources[0] and int(self.parent.view.menuModes.spinGaz2.get()) <= self.players[self.id_trade_with].ressources[1]:
                    self.parent.push_change(id2, Flag(4, self.parent.view.menuModes.spinMinerals1.get()+','+self.parent.view.menuModes.spinMinerals2.get()+','+self.parent.view.menuModes.spinGaz1.get()+','+self.parent.view.menuModes.spinGaz2.get(), Flag.TRADE))
                    self.trade_page = 1
                    self.parent.view.ongletTradeWaiting()
        except KeyError:
            print('du texte dans les spins de trade')
            
    def confirm_trade(self, answer, id1, min1, min2, gaz1, gaz2):
        if answer:
            self.parent.push_change(self.id_trade_with, Flag("m", min1, Flag.TRADE))
            self.parent.push_change(self.player_id, Flag("m", min2+','+str(self.id_trade_with), Flag.TRADE))
            self.parent.push_change(self.id_trade_with, Flag("g", gaz1, Flag.TRADE))
            self.parent.push_change(self.player_id, Flag("g", gaz2+','+str(self.id_trade_with), Flag.TRADE))
        else:
            self.parent.push_change(id1, Flag(3, "deniedTrade", Flag.TRADE))
            self.trade_page = -1
            self.parent.view.ongletTradeChoicePlayer()

    def trade_actions(self, action_player_id, target, unit_index):
        if target[0] == '1':
            if int(unit_index[0]) == self.player_id:
                self.trade_page = 3
                self.id_trade_with=action_player_id
                self.parent.view.ongletTradeYesNoQuestion(action_player_id)
        elif target[0] == '2':
            if int(unit_index[0]) == self.player_id or action_player_id == self.player_id:
                if int(unit_index[0]) == self.player_id:
                    self.is_master_of_trade=True
                    self.parent.view.ongletTrade(self.player_id, self.id_trade_with)
                else:
                    self.is_master_of_trade=False
                    self.parent.view.ongletTrade(self.id_trade_with, self.player_id)
                self.trade_page = 2
        elif target[0] == '3':
            if int(unit_index[0]) == self.player_id:
                self.is_master_of_trade = False
                self.trade_page = -1
                self.id_trade_with = self.player_id
                self.parent.view.ongletTradeNoAnswer()
        elif target[0] == '4':
            if int(unit_index[0]) == self.player_id:
                self.trade_page = 4
                self.to_trade = (target[1], target[2], target[3], target[4])
                self.parent.view.ongletTradeAskConfirm(action_player_id, self.to_trade[0], self.to_trade[1], self.to_trade[2], self.to_trade[3])
        elif target[0] == '5':
            if int(unit_index[0]) == self.player_id or action_player_id == self.player_id:
                self.is_master_of_trade = False
                self.trade_page = -1
                self.id_trade_with = self.player_id
                self.parent.view.ongletTradeCancel()
        elif target[0] == 'm' or target[0] == 'g':
            if target[0] == 'm':
                resource_type = Player.MINERAL
            elif target[0] == 'g':
                resource_type = Player.GAS
            if int(unit_index[0]) != action_player_id:
                self.trade(action_player_id, int(unit_index[0]), resource_type, int(target[1]))
            else:
                self.trade(int(target[2]), action_player_id, resource_type, int(target[1]))
            self.is_master_of_trade=False
            self.trade_page = -1
            self.id_trade_with = self.player_id
            self.parent.view.ongletTradeYesAnswer()

    def set_landing_flag(self, unit, planet):
        solar_system_id = 0
        planet_index = 0
        for solar_system in self.galaxy.solarSystemList:
            for _planet in solar_system.planets:
                if _planet == planet:
                    solar_system_id = self.galaxy.solarSystemList.index(solar_system)
                    planet_index = self.galaxy.solarSystemList[solar_system_id].planets.index(_planet)
        self.parent.push_change(str(self.get_my_player().units.index(unit)), (solar_system_id, planet_index, Flag.LAND))

    def make_unit_land(self, player_id, unit_id, solar_system_id, planet_id):
        planet = self.galaxy.solarSystemList[solar_system_id].planets[planet_id]
        self.players[player_id].make_unit_land(unit_id, planet)

    def set_rally_point_position(self, pos):
        self.parent.push_change(self.get_my_player().get_selected_building_index(), Flag(finalTarget=pos, flagState=Flag.CHANGE_RALLY_POINT))

    def set_change_formation_flag(self, formation):
        units = ""
        for i in self.get_my_player().selectedObjects:
            units += str(self.get_my_player().units.index(i)) + ","
        self.parent.push_change(units, Flag(i, formation, Flag.CHANGE_FORMATION))
        
    def set_take_off_flag(self, ship, planet):
        planet_id = 0
        sun_id = 0
        ship_id = self.get_my_player().units.index(ship)
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    planet_id = i.planets.index(j)
                    sun_id = self.galaxy.solarSystemList.index(i)
        self.parent.push_change(ship_id, (planet_id, sun_id, 'TAKEOFF'))

    def set_load_flag(self, unit, landing_zone):
        units = ""
        for i in unit:
            if isinstance(i, GroundUnit):
                units += str(self.get_my_player().units.index(i)) + ","
        self.parent.push_change(units, Flag(unit, landing_zone, Flag.LOAD))

    def load_unit(self, units, planet_id, sun_id, player_id):
        planet = self.galaxy.solarSystemList[sun_id].planets[planet_id]
        landing_zone = planet.get_landing_spot(player_id)
        if landing_zone:
            self.players[player_id].make_unit_load(units, landing_zone)

    def unload(self):
        zone = self.get_my_player().get_ship_to_unload()
        if zone:
            self.parent.push_change(zone, 'UNLOAD')

    def make_zone_unload(self, zone_id, player_id, planet_id, sun_id):
        landing_zone = self.galaxy.solarSystemList[sun_id].planets[planet_id].landingZones[zone_id]
        planet = self.galaxy.solarSystemList[sun_id].planets[planet_id]
        units = landing_zone.LandedShip.units
        for i in units:
            position = [landing_zone.position[0] + 40, landing_zone.position[1] + 5 * self.players[player_id].units.index(i)]
            i.land(planet, position)
        del landing_zone.LandedShip.units[:]

    #Pour ajouter une unit
    def add_unit(self, unitType):
        mineralCost = Unit.BUILD_COST[unitType][0]
        gazCost = Unit.BUILD_COST[unitType][1]
        foodCost = Unit.BUILD_COST[unitType][2]
        if self.get_my_player().can_afford(mineralCost, gazCost, foodCost):
            self.parent.push_change(self.get_my_player().get_selected_building_index(),Flag(finalTarget=unitType, flagState=Flag.CREATE))
        elif self.get_my_player().ressources[Player.FOOD]+foodCost > self.get_my_player().MAX_FOOD:
            if self.get_my_player().check_if_can_add_notif(Notification.NOT_ENOUGH_POPULATION):
                self.get_my_player().notifications.append(Notification([-10000,-10000,-10000], Notification.NOT_ENOUGH_POPULATION))
        else:
            if self.get_my_player().check_if_can_add_notif(Notification.NOT_ENOUGH_RESSOURCES):
                self.get_my_player().notifications.append(Notification([-10000,-10000,-10000], Notification.NOT_ENOUGH_RESSOURCES))

    def create_unit(self, player, construction_unit, unit_type):
        mineral_cost = Unit.BUILD_COST[unit_type][0]
        gaz_cost = Unit.BUILD_COST[unit_type][1]
        food_cost = Unit.BUILD_COST[unit_type][2]
        if self.players[player].can_afford(mineral_cost, gaz_cost, food_cost):
            if construction_unit <= (len(self.players[player].buildings)-1) and construction_unit:
                if isinstance(self.players[player].buildings[construction_unit], ConstructionBuilding):
                    self.players[player].create_unit(unit_type, construction_unit)
                    
    def send_cancel_unit(self, unit):
        self.parent.push_change(self.get_my_player().get_selected_building_index(), Flag(finalTarget=unit, flagState=Flag.CANCEL_UNIT))

    def cancel_unit(self, player, unit, construction_building):
        if construction_building <= (len(self.players[player].buildings)-1) and construction_building:
            self.players[player].cancel_unit(unit, construction_building)

    def send_cancel_tech(self, tech):
        self.parent.push_change(self.get_my_player().get_selected_building_index(), Flag(finalTarget=tech, flagState=Flag.CANCEL_TECH))

    def cancel_tech(self, player, tech, construction_building):
        if construction_building <= (len(self.players[player].buildings)-1) and construction_building:
            self.players[player].cancel_tech(tech, construction_building)

    def erase_unit(self):
        if len(self.get_my_player().selectedObjects) > 0:
            if isinstance(self.get_my_player().selectedObjects[len(self.get_my_player().selectedObjects)-1], Unit):
                self.parent.push_change(self.get_my_player().units.index(self.get_my_player().selectedObjects[len(self.get_my_player().selectedObjects)-1]), Flag(None, None, Flag.DESTROY))

    def erase_units(self, player_id=None):
        if not player_id:
            player_id = self.player_id
        #self.parent.pushChange(player_id, Flag(None,player_id,FlagState.DESTROY_ALL))

    def check_if_game_finished(self):
        my_player = self.get_my_player()
        for player in self.players:
            if player.is_alive and player.id != my_player.id:
                if not my_player.is_ally(player.id):
                    return False
        return True

    def calculate_who_won(self):
        scores = []
        for pl in self.players:
            to_insert = []
            to_insert.append(pl.colorId)
            to_insert.append(pl.name)
            to_insert.append(pl.calculate_final_buildings_score())
            to_insert.append(pl.calculate_final_units_score())
            to_insert.append(pl.calculate_final_resources_score())
            to_insert.append(pl.calculate_final_killed_score())
            to_insert.append(pl.calculate_final_diplomacy_score())
            to_insert.append(to_insert[2]+to_insert[3]+to_insert[4]+to_insert[5]+to_insert[6])
            index_to_insert = 0
            for score in scores:
                if to_insert[7] > score[7]:
                    break
                index_to_insert += 1
            scores.insert(index_to_insert, to_insert)
        return scores

    def kill_player(self, player_id):
        self.players[player_id].kill()
        if player_id == self.player_id:
            self.parent.remove_player()
            self.get_my_player().selectedObjects = []
            self.parent.go_to_win_frame(self.calculate_who_won())
        elif self.check_if_game_finished():
            self.parent.go_to_win_frame(self.calculate_who_won())
    
    def trade(self, player1, player2, resource_type, amount):
        self.players[player1].adjust_resources(resource_type, amount)
        self.players[player2].adjust_resources(resource_type, amount*-1)

    def adjust_resources(self, player, resource_type, amount):
        self.players[player].adjust_resources(resource_type, amount)

    def cheat_player(self, player_id , type):
        if type == "forcegaz":
            self.players[player_id].ressources[Player.GAS] += 5000
        elif type == "forcemine":
            self.players[player_id].ressources[Player.MINERAL] += 5000
        elif type == "forcenuke":
            self.players[player_id].ressources[Player.NUCLEAR] += 25
        elif type == "forcepop":
            self.players[player_id].MAX_FOOD += 30
        elif type == "forcebuild":
            self.players[player_id].FORCE_BUILD_ACTIVATED = True
            player = self.players[player_id]
            for unit in player.units:
                if isinstance(unit, GatherShip) or isinstance(unit, GroundGatherUnit) or isinstance(unit, SpecialGather):
                    unit.GATHERTIME = 0
            for building in player.buildings:
                if isinstance(building, ConstructionBuilding) and building.finished:
                    for a in building.unit_being_construct:
                        a.build_time = 1
                elif not building.finished:
                    building.hitpoints = building.MAX_HP[building.type]
                    building.build_time = 1
                elif isinstance(building, Lab) and building.finished:
                    for t in building.techsToResearch:
                        t[0].time_needed = 1
        elif type == "doabarrelroll":
            unit = NyanCat(Unit.NYAN_CAT, [0,0,0], player_id)
            self.players[player_id].units.append(unit)
        elif type == "allyourbasesbelongtous":
            self.players[player_id].mother_ships[0].view_range = 1000000000
    
    def demand_alliance(self, player_id, other_player_id, new_status):
        self.players[player_id].change_diplomacy(other_player_id, new_status)
        if other_player_id == self.player_id:
            if new_status == "Ally":
                if self.players[other_player_id].is_ally(player_id):
                    self.get_my_player().notifications.append(Notification((-10000, -10000, -10000), Notification.ALLIANCE_ALLY, self.players[player_id].name))
                else:
                    self.get_my_player().notifications.append(Notification((-10000, -10000, -10000), Notification.ALLIANCE_DEMAND_ALLY, self.players[player_id].name))
            else:
                self.get_my_player().notifications.append(Notification((-10000, -10000, -10000), Notification.ALLIANCE_ENNEMY, self.players[player_id].name))
        elif player_id == self.player_id:
            if new_status == "Ally" and self.players[other_player_id].is_ally(player_id):
                    self.get_my_player().notifications.append(Notification((-10000, -10000, -10000), Notification.ALLIANCE_ALLY, self.players[other_player_id].name))
        if self.check_if_game_finished():
            self.parent.go_to_win_frame(self.calculate_who_won())

    def get_player_id(self, player):
        for i in self.players:
            if i.name == player:
                return i.id
        return -1
    
    def is_allied(self, player_1_id, player_2_id):
        if self.players[player_1_id].diplomacies[player_2_id] == "Ally":
            return True
        else:
            return False

    def get_allies(self):
        allies = []
        for p in self.players:
            if p != self.get_my_player():
                if p.is_ally(self.player_id):
                    allies.append(p.name)
        return allies

    def get_first_unit_selected(self):
        return self.get_my_player().selectedObjects[0]

    def select_waypoint_wall(self, pos):
        if not self.get_my_player().current_planet:
            for building in self.get_my_player().buildings:
                if isinstance(building, Waypoint) and building != self.get_first_unit_selected():
                    if building.select(pos):
                        return building
        return None

    def calc_cost_wall(self, waypoint1, waypoint2):
        distance = Helper.calc_distance(waypoint1.position[0], waypoint1.position[1], waypoint2.position[0], waypoint2.position[1])
        cost = (distance*3)-((distance*3) % 25)+25
        return cost
    
    def set_linked_waypoint(self, pos):
        selected_way_point = self.get_first_unit_selected()
        other_waypoint = self.select_waypoint_wall(pos)
        if other_waypoint:
            if selected_way_point.has_free_wall and other_waypoint.hasFreeWall:
                cost = int(self.calc_cost_wall(selected_way_point, other_waypoint))
                if self.get_my_player().can_afford(0, cost, 0):
                    way1 = self.get_my_player().buildings.index(selected_way_point)
                    way2 = self.get_my_player().buildings.index(other_waypoint)
                    self.parent.push_change("0,", Flag(None, [way1, way2, cost], Flag.LINK_WAYPOINTS))
                else:
                    self.get_my_player().notifications.append(Notification([-10000, -10000, -10000], Notification.NOT_ENOUGH_RESSOURCES))

    def link_waypoints(self, player_id, way_id1, way_id2, cost):
        player = self.players[player_id]
        if player.can_afford(0, cost, 0):
            player.link_waypoints(way_id1, way_id2, cost)

    def units_in_line(self, wall):
        units = []
        for player in self.players:
            if player.id != wall.owner:
                for unit in player.units:
                    if unit.isAlive:
                        if wall.is_rectangle_on_line(unit.position, unit.SIZE[unit.type]):
                            units.append(unit)
                for building in player.buildings:
                    if building.isAlive:
                        if wall.is_rectangle_on_line(building.position, building.SIZE[building.type]):
                            units.append(building)
        return units

    def select_unit_enemy(self, pos_selected):
        if not self.get_my_player().current_planet:
            if len(self.get_my_player().selectedObjects) > 0:
                    for player in self.players:
                        if player.is_alive:
                            if player.id != self.player_id and not self.get_my_player().is_ally(player.id):
                                for unit in player.units:
                                    if unit.select(pos_selected):
                                        self.set_attack_flag(unit)

    def check_if_enemy_in_range(self, unit, on_planet=False, planet_id=-1, solar_system_id=-1):
        for pl in self.players:
            if pl.isAlive:
                if pl.id != unit.owner and self.players[unit.owner].is_ally(pl.id) == False:
                    enemyUnit = pl.has_unit_in_range(unit.position, unit.range, on_planet, planet_id, solar_system_id)
                    if enemyUnit != None:
                        self.attack_enemy_in_range(unit, enemyUnit)
                        break
        if on_planet:
            planet = self.galaxy.solarSystemList[solar_system_id].planets[planet_id]
            enemyZone = planet.has_zone_in_range(unit.position, unit.range)
            if enemyZone != None and enemyZone.ownerId != unit.owner and not self.players[unit.owner].is_ally(enemyZone.ownerId):
                self.attack_enemy_in_range(unit, enemyZone)
                                        
    def attack_enemy_in_range(self, unit, unitToAttack):
        unit.change_flag(unitToAttack, Flag.ATTACK)

    def has_unit_in_range(self, bullet):
        unitsToAttack = []
        for pl in self.players:
            if pl.isAlive and pl.id != bullet.owner:
                for un in pl.units:
                    if un.isAlive and (isinstance(un, SpaceUnit) or un.type == Unit.SCOUT):
                        unitInRange = un.is_in_range(bullet.position, bullet.range)
                        if unitInRange != None:
                            unitsToAttack.append(unitInRange)
                for bd in pl.buildings:
                    if bd.isAlive and (isinstance(bd, SpaceBuilding) or isinstance(bd, MotherShip) or isinstance(bd, Barrack) or isinstance(bd, Utility)):
                        buildingInRange = bd.is_in_range(bullet.position, bullet.range)
                        if buildingInRange != None:
                            unitsToAttack.append(buildingInRange)
        return unitsToAttack
    
    def check_if_can_build(self, position, type, index=None, playerId = None, planetId = None, sunId = None):
        if index != None:
            if index < len(self.players[playerId].units):
                unit = self.players[playerId].units[index]
            else:
                return False
        else:
            if len(self.get_my_player().selectedObjects) > 0:
                unit = self.get_my_player().selectedObjects[0]
            else:
                return False
        start = (position[0]-(Building.SIZE[type][0]/2),position[1]-(Building.SIZE[type][1]/2),0)
        end = (position[0]+(Building.SIZE[type][0]/2),position[1]+(Building.SIZE[type][1]/2),0)
        
        for p in self.players:
            for b in p.buildings:
                if planetId != None:
                    if (isinstance(b, GroundBuilding) or isinstance(b, LandingZone)) and isinstance(unit, GroundUnit):
                        if unit.planet == b.planet:
                            if b.select_icon(start, end) != None:
                                return False
                else:
                    if b.select_icon(start, end) != None:
                        return False
        if planetId == None:
            for i in self.galaxy.solarSystemList:
                if i.over(start, end):
                    return False
        else:
            planet = self.galaxy.solarSystemList[sunId].planets[planetId]
            if planet.ground_over(start, end):
                return False
        return True
    
    def select_unit_by_type(self, typeId):
        self.get_my_player().select_units_by_type(typeId)
    
    def select(self, posSelected):
        player = self.get_my_player()
        if player.current_planet == None:
            if not self.multi_select:
                player.select_unit(posSelected)
            else:
                player.multi_select_units(posSelected)
            spaceObj = self.galaxy.select(posSelected, False)
            if isinstance(spaceObj, Planet):
                player.select_planet(spaceObj)
            else:
                player.select_object(spaceObj, False)
        else:
            planet = player.current_planet
            groundObj = planet.ground_select(posSelected)
            player.select_object(groundObj, False)
        self.parent.change_action_menu_type(View.MAIN_MENU)
    
    def select_object_from_menu(self, unitId):
        self.get_my_player().select_object_from_menu(unitId)
    
    def select_all(self, posSelected):
        self.get_my_player().select_all(posSelected)
        self.parent.change_action_menu_type(View.MAIN_MENU)

    def right_click(self, pos):
        empty = True
        if self.get_current_planet() == None:
            unit = self.get_my_player().get_first_unit()
            if unit:
                clickedObj = self.galaxy.select(pos)
                if not clickedObj:
                    for i in self.players:
                        clickedObj = i.right_click(pos, self.player_id)
                        if clickedObj:
                            break
                if clickedObj and not isinstance(unit, Building):
                    if unit.type == unit.HEALING_UNIT:
                        if isinstance(clickedObj, Unit):
                            if clickedObj.owner == self.player_id:
                                self.set_action_heal_unit(clickedObj, 0)
                        elif isinstance(clickedObj, Building):
                            if clickedObj.owner == self.player_id:
                                self.set_action_heal_unit(clickedObj, 1)
                    if unit.type == unit.TRANSPORT:
                        if isinstance(clickedObj, Planet):
                            self.set_landing_flag(unit, clickedObj)
                        elif isinstance(clickedObj, MotherShip):
                            self.set_gather_flag(unit, clickedObj)
                    elif unit.type == unit.CARGO:
                        if isinstance(clickedObj, AstronomicalObject):
                            self.set_all_gather_flag(clickedObj)
                        elif isinstance(clickedObj, MotherShip) or isinstance(clickedObj, Waypoint):
                            if clickedObj.owner == self.player_id:
                                self.set_gather_flag(unit, clickedObj)
                    elif unit.type in (unit.ATTACK_SHIP, unit.NYAN_CAT):
                        if (isinstance(clickedObj, Unit) or isinstance(clickedObj, SpaceBuilding) or isinstance(clickedObj, MotherShip) or isinstance(clickedObj, Utility) or isinstance(clickedObj, Barrack)) and  not isinstance(clickedObj, GroundUnit):
                            if clickedObj.owner != self.player_id:
                                self.set_attack_flag(clickedObj)
                    elif unit.type == unit.SPACE_BUILDING_ATTACK:
                        if (isinstance(clickedObj, Unit) or isinstance(clickedObj, SpaceBuilding) or isinstance(clickedObj, MotherShip) or isinstance(clickedObj, Utility) or isinstance(clickedObj, Barrack)) and  not isinstance(clickedObj, GroundUnit):
                            if clickedObj.owner != self.player_id:
                                pos = clickedObj.position
                            self.set_attack_building_flag([pos[0], pos[1], 0])
                    elif unit.type == unit.SCOUT:
                        if isinstance(clickedObj, Building):
                            if clickedObj.owner == self.player_id:
                                if clickedObj.finished == False:
                                    self.resume_building_flag(clickedObj)
                    if isinstance(clickedObj, WormHole):
                        if clickedObj.duration > 0 and clickedObj.playerId == self.player_id:
                            self.set_worm_hole_flag(clickedObj)
                else:
                    if isinstance(unit, ConstructionBuilding):
                        self.set_rally_point_position(pos)
                    else:
                        self.set_moving_flag(pos[0], pos[1])
        else:
            unit = self.get_my_player().get_first_unit()
            clickedObj = self.get_current_planet().ground_select(pos)
            if unit != None:
                if clickedObj != None and not isinstance(unit, Building):
                    if unit.type == unit.GROUND_GATHER:
                        if isinstance(clickedObj, MineralStack) or isinstance(clickedObj, GazStack) or isinstance(clickedObj, LandingZone) or isinstance(clickedObj, Farm):
                            self.set_all_ground_gather_flag(clickedObj)
                    elif unit.type == unit.GROUND_ATTACK:
                        if isinstance(clickedObj, Unit) or isinstance(clickedObj, Building):
                            if clickedObj.owner != self.player_id and not self.get_my_player().is_ally(clickedObj.owner):
                                self.set_attack_flag(clickedObj)
                    elif unit.type == unit.GROUND_BUILDER_UNIT:
                        if isinstance(clickedObj, Building):
                            if clickedObj.owner == self.player_id:
                                if clickedObj.finished == False:
                                    self.resume_building_flag(clickedObj)
                    elif unit.type == unit.SPECIAL_GATHER:
                        if isinstance(clickedObj, NuclearSite):
                            self.set_ground_gather_flag(unit, clickedObj)
                    if isinstance(clickedObj, LandingZone) and clickedObj.owner == self.player_id:
                        if clickedObj.LandedShip != None:
                            self.set_load_flag(self.get_my_player().selectedObjects, clickedObj)
                else:
                    if isinstance(unit, LandingZone):
                        self.set_rally_point_position(pos)
                    else:
                        self.set_ground_moving_flag(pos[0], pos[1])
                
    #Selection avec le clic-drag
    def box_select(self, selectStart, selectEnd):
        realStart = self.get_my_player().camera.calc_point_in_world(selectStart[0], selectStart[1])
        realEnd = self.get_my_player().camera.calc_point_in_world(selectEnd[0], selectEnd[1])
        temp = [0,0]
        if realStart[0] > realEnd[0]:
            temp[0] = realStart[0]
            realStart[0] = realEnd[0]
            realEnd[0] = temp[0]
        if realStart[1] > realEnd[1]:
            temp[1] = realStart[1]
            realStart[1] = realEnd[1]
            realEnd[1] = temp[1]
        self.get_my_player().box_select(realStart, realEnd)
        self.parent.view.actionMenuType = self.parent.view.MAIN_MENU
        
    #Deplacement rapide de la camera vers un endroit de la minimap
    def quick_move(self, x, y):
        if self.get_my_player().current_planet == None:
            posSelected = self.get_my_player().camera.calc_point_on_map(x,y)
            self.get_my_player().camera.position = posSelected
        else:
            posSelected = self.get_my_player().camera.calc_point_on_planet_map(x,y)
            self.get_my_player().camera.position = posSelected

    def ping_allies(self, x, y):
        self.parent.push_change(self.get_my_player().name, Flag(None,[self.player_id,Notification.PING,x,y],Flag.NOTIFICATION))
    
    def take_off(self, ship, planet, player_id):
        ship.take_off(planet)
        self.players[player_id].current_planet = None
        self.parent.redraw_mini_map()
        self.parent.draw_world()

    def get_current_camera(self):
        return self.get_my_player().camera

    def is_on_planet(self):
        if not self.get_my_player().current_planet:
            return False
        else:
            return True

    def get_current_planet(self):
        return self.get_my_player().current_planet

    def change_formation(self, playerId, newType, units, action):
        self.players[playerId].formation = newType
        self.players[playerId].make_formation(units, self.galaxy, action = action)

    def make_formation(self, playerId, units, target, action):
        self.players[playerId].make_formation(units, self.galaxy, target, action)

    def select_memory(self, selected):
        self.get_my_player().select_memory(selected)

    def new_memory(self, selected):
        self.get_my_player().new_memory(selected)

    def make_worm_hole(self, playerId, startPosition, endPosition, mothership):
        gazCost = Helper.calc_distance(startPosition[0], startPosition[1], endPosition[0], endPosition[1])
        gazCost = int(math.trunc(gazCost))
        if self.players[playerId].can_afford(0, gazCost, 0,WormHole.NUKECOST) and mothership.wormhole == None:
            self.players[playerId].ressources[Player.NUCLEAR] -= WormHole.NUKECOST
            self.players[playerId].ressources[Player.GAS] -= gazCost
            newWormHole = WormHole(startPosition, endPosition, playerId)
            self.galaxy.wormholes.append(newWormHole)
            mothership.wormhole = newWormHole
        
    def create_worm_hole(self, position):
        mothership = self.get_my_player().selectedObjects[0]
        motherIndex = self.get_my_player().motherships.index(mothership)
        self.parent.push_change(motherIndex, (mothership.position, position, 'WORMHOLE'))

    def can_set_attack(self):
        player = self.get_my_player()
        for i in player.selectedObjects:
            if i.type == Unit.ATTACK_SHIP or i.type == Unit.GROUND_ATTACK:
                return 'Normal'
            elif i.type == Unit.SPACE_BUILDING_ATTACK:
                return 'Building'
        return None
