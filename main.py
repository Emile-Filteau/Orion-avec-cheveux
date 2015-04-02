# -*- coding: UTF-8 -*-
import sys
import os
import socket
import subprocess
import time
import Pyro4
import math
from view.View import View
from model import *
from model.utils import Flag, Notification
from model.unit import Unit
from model.building.ground import LandingZone, Farm
from model.world import *


class Client():

    def __init__(self):
        self.ai_amount = 0
        self.refresh_counter = 0
        self.players = []
        self.computers = []
        self.wait_time = 50
        self.died = False
        self.messages = []
        self.player_ip = socket.gethostbyname(socket.getfqdn())
        self.server = None
        self.is_started = False
        self.current_frame = None
        self.wait_write = False
        self.game = Game(self)
        self.view = View(self, self.game)
        self.view.root.mainloop()

    def action(self):
        if self.view.currentFrame != self.view.pLobby:
            if not self.server.is_stopped:
                if self.refresh_counter > 0:
                    if self.game.action(): 
                        if self.refresh_counter % 20 == 0:
                            self.refresh_messages(self.view.menuModes.chat)
                        self.pull_change()
                        if not self.died:
                            self.view.refreshGame(self.game.is_on_planet())
                            self.refresh_counter += 1
                            self.wait_time = self.server.am_i_too_high(self.game.player_id)
                    elif self.game.player_id != 0:
                        self.view.deleteAll()
                else:
                    self.check_if_game_starting()
        else:
            if self.server.game_is_started:
                self.start_game()
            else:
                self.wait_time = 1000
                self.refresh_messages(self.view.chatLobby)
                self.view.redrawLobby(self.view.pLobby)
        if not self.died:
            self.view.root.after(self.wait_time, self.action)

    def check_if_game_starting(self):
        response = self.server.is_everyone_ready(self.game.player_id)
        if response:
            self.refresh_counter += 1
            self.wait_time = 50
            if self.game.player_id == 0:
                self.send_message('La partie va maintenant débuter.')
        else:
            if self.game.player_id == 0 and not self.wait_write:
                self.wait_write = True
                self.send_message("Attente des autres joueurs.")

    def send_message(self, mess):
        if self.ai_amount > len(self.players)-2:  # Let the player use cheat only if he plays against AI
            if mess == "forcegaz":
                self.push_change(0, Flag(None, "forcegaz", Flag.CHEAT))
            elif mess == "forcemine":
                self.push_change(0, Flag(None, "forcemine", Flag.CHEAT))
            elif mess == "forcenuke":
                self.push_change(0, Flag(None, "forcenuke", Flag.CHEAT))
            elif mess == "forcepop":
                self.push_change(0, Flag(None, "forcepop", Flag.CHEAT))
            elif mess == "forcebuild":
                self.push_change(0, Flag(None, "forcebuild",Flag.CHEAT))
            elif mess == "doabarrelroll":
                self.push_change(0, Flag(None, "doabarrelroll", Flag.CHEAT))
            elif mess == "allyourbasesbelongtous":
                self.push_change(0, Flag(None, "allyourbasesbelongtous", Flag.CHEAT))
        if mess.find("\\t ") == 0:
            mess = mess.split("\\t ")
            mess = "(Alliés) "+mess[1]
            self.server.add_message(mess, self.game.players[self.game.player_id].name, self.game.player_id, True)
            self.push_change(mess, Flag(None,[self.game.player_id, Notification.MESSAGE_ALLIES, 0], Flag.NOTIFICATION))
        elif len(mess) > 0:
            mess = mess.replace('\\', '/')
            self.server.add_message(mess, self.game.players[self.game.player_id].name, self.game.player_id, False)
            self.push_change(mess, Flag(None,[self.game.player_id, Notification.MESSAGE_ALL, 0], Flag.NOTIFICATION))

    def send_message_lobby(self, mess, nom):
        mess = mess.replace('\\', '/')
        self.server.add_message(mess, self.server.sockets[self.game.player_id][1], self.game.player_id, False)

    def refresh_messages(self, chat):
        if self.refresh_counter % 10 == 0:
            text_chat = ''
            self.messages = []
            for i in range(len(self.messages), len(self.server.messages)):
                if self.server.messages[i][2]:
                    if self.game.players[self.game.player_id].is_ally(self.server.messages[i][0]):
                        self.messages.append(self.server.messages[i][1])
                else:
                    self.messages.append(self.server.messages[i][1])
            if len(self.messages) > 5:
                for i in range(len(self.messages)-5, len(self.messages)):
                    text_chat += self.messages[i]+'\r'
            else:
                for i in range(0, len(self.messages)):
                    text_chat += self.messages[i]+'\r'
            chat.config(text=text_chat)

    def choose_color(self, name , index, mode):
        response = self.server.is_this_color_chosen(self.view.variableColor.get(), self.game.player_id)
        if response:
            self.view.colorAlreadyChosen()

    def start_server(self, server_address, connect, user_name):
        paths = sys.path
        temp = None
        if os.name == 'nt':
            for i in paths:
                if i.find("\\lib\\") != -1:
                    temp = i.split("\\lib\\")[0]
                    break
            if temp:
                temp += "\\python.exe"
            else:
                temp = "C:\python32\python.exe"
        elif os.name == 'posix':
            temp = 'python'
        child = subprocess.Popen(temp + " server.py " + server_address, shell=True)
        time.sleep(1)
        if child.poll():
            if child.returncode:
                self.view.serverNotCreated()
        else:
            if connect:
                self.connect_server(user_name, server_address)
            else:
                self.view.changeFrame(self.view.mainMenu)

    def connect_server(self, username, server_address):
        self.server = Pyro4.core.Proxy("PYRO:ServeurOrion@"+server_address+":54400")
        print self.server.__class__
        if self.server.game_is_started:
            self.view.gameHasBeenStarted()
            self.view.changeFrame(self.view.mainMenu)
        else:
            self.game.player_id = self.server.get_num_socket(username, self.player_ip, False)
            if self.game.player_id != -1:
                self.view.pLobby = self.view.fLobby()
                self.view.changeFrame(self.view.pLobby)
                self.action()
            else:
                self.view.showNameAlreadyChosen()
                self.view.changeFrame(self.view.joinGame)

    def start_game(self):
        if self.game.player_id == 0:
            self.server.start_game()
        for i in range(0, len(self.server.sockets)):
            if self.server.sockets[i][3] == -1:
                self.server.first_color_not_chosen(i)
            if not self.server.sockets[i][4]:
                self.players.append(Player(self.server.sockets[i][1], self.game, i, self.server.sockets[i][3]))
            else:
                self.players.append(AI(self.server.sockets[i][1], self.game, i, self.server.sockets[i][3]))
                self.server.is_everyone_ready(len(self.players)-1)
        self.game.start(self.players, self.server.seed, self.view.WIDTH, self.view.HEIGHT)
        self.view.gameFrame = self.view.fGame()
        self.view.changeFrame(self.view.gameFrame)
        self.view.root.after(50, self.action)
        
    def add_ai(self):
        self.ai_amount += 1
        self.server.get_num_socket("IA"+str(self.ai_amount), self.player_ip, True)
        
    def draw_world(self):
        self.view.drawWorld()

    def redraw_mini_map(self):
        self.view.redrawMinimap()

    def go_to_win_frame(self, scores):
        self.view.scores = self.view.fScore(scores)
        self.view.changeFrame(self.view.scores)

    def change_background(self, new_background):
        self.view.changeBackground(new_background)
    
    def draw_planet_ground(self, planet):
        self.view.drawPlanetGround(planet)

    def change_action_menu_type(self, new_menu_type):
        self.view.actionMenuType = new_menu_type

    def change_alliance(self, player, new_status):
        self.push_change(player, Flag(finalTarget=new_status, Flag=Flag.DEMAND_ALLIANCE))

    def push_change(self, player_object, flag):
        action_string = ""
        if isinstance(flag, Flag):
            if flag.flag_state in (Flag.MOVE, Flag.STANDBY):
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(flag.final_target.position)
            elif flag.flag_state == Flag.GROUND_MOVE:
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(flag.final_target.position)
            elif flag.flag_state == Flag.HEAL:
                action_string = str(self.game.player_id) + "/" + str(player_object) + "/" + str(flag.flag_state) + "/" + str(flag.final_target.position)
            elif flag.flag_state == Flag.ATTACK:
                if isinstance(flag.final_target, Unit):
                    target_id = self.game.players[flag.final_target.owner].units.index(flag.final_target)
                    type = "u"
                else:
                    type = "b"
                    target_id = self.game.players[flag.final_target.owner].buildings.index(flag.final_target)
                if isinstance(flag.initial_target, int):
                    action_string = str(flag.initial_target)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(target_id)+","+str(flag.final_target.owner)+","+type
                else:
                    action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(target_id)+","+str(flag.final_target.owner)+","+type
            elif flag.flag_state == Flag.FINISH_BUILD:
                building_id = self.game.players[flag.final_target.owner].buildings.index(flag.final_target)
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(building_id)
            elif flag.flag_state == Flag.BUILD:
                for i in flag.initial_target:
                    flag.final_target.position.append(i)
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(flag.final_target.position)
            elif flag.flag_state in (Flag.CREATE, Flag.CHANGE_RALLY_POINT, Flag.NOTIFICATION, Flag.ATTACK_BUILDING, Flag.LINK_WAYPOINTS, Flag.CANCEL_UNIT, Flag.CANCEL_TECH, Flag.CHEAT, Flag.CHANGE_FORMATION, Flag.DESTROY_ALL, Flag.DEMAND_ALLIANCE):
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state) + "/" + str(flag.final_target)
            elif flag.flag_state == Flag.DESTROY:
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/0"
            elif flag.flag_state == Flag.PATROL:
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(flag.final_target.position)
            elif flag.flag_state == Flag.TRADE:
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/["+str(flag.initial_target)+","+str(flag.final_target)+"]"
            elif flag.flag_state == Flag.BUY_TECH:
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(flag.final_target.position)
            elif flag.flag_state == Flag.WORMHOLE:
                wormhole_id = self.game.galaxy.wormholes.index(flag.final_target)
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(wormhole_id)
            elif flag.flag_state == Flag.LOAD:
                planet_id = flag.final_target.planet_id
                solar_id = flag.final_target.sun_id
                zone_id = flag.final_target.id
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(zone_id)+","+str(planet_id)+","+str(solar_id)
            elif flag.flag_state == Flag.GATHER:
                if isinstance(flag.final_target, AstronomicalObject):
                    astro_id = flag.final_target.id
                    solar_id = flag.final_target.solarSystem.sun_id
                    action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(astro_id)+","+str(solar_id)+","+str(flag.final_target.type)
                else:
                    action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag.flag_state)+"/"+str(self.game.players[self.game.player_id].buildings.index(flag.final_target))+",0," + str(flag.final_target.type)
            elif flag.flag_state == Flag.GROUND_GATHER:
                sun_id = flag.final_target.sun_id
                planet_id = flag.final_target.planet_id
                resource_id = 0
                if not isinstance(flag.final_target, NuclearSite) and not isinstance(flag.final_target, Farm):
                    resource_id = flag.final_target.id
                if isinstance(flag.final_target, MineralStack):
                    action_string = str(self.game.player_id) + "/" + str(player_object) + "/" + str(flag.flag_state) + "/" + str(resource_id) + "," + str(planet_id) + "," + str(sun_id) + "," + "mine"
                elif isinstance(flag.final_target, GazStack):
                    action_string = str(self.game.player_id) + "/" + str(player_object) + "/" + str(flag.flag_state) + "/" + str(resource_id) + "," + str(planet_id) + "," + str(sun_id) + "," + "gaz"
                elif isinstance(flag.final_target, NuclearSite):
                    action_string = str(self.game.player_id) + "/" + str(player_object) + "/" + str(flag.flag_state) + "/" + str(resource_id) + "," + str(planet_id) + "," + str(sun_id) + "," + "nuclear"
                elif isinstance(flag.final_target, LandingZone):
                    action_string = str(self.game.player_id) + "/" + str(player_object) + "/" + str(flag.flag_state) + "/" + str(resource_id) + "," + str(planet_id) + "," + str(sun_id) + "," + "landing"
                elif isinstance(flag.final_target, Farm):
                    action_string = str(self.game.player_id) + "/" + str(player_object) + "/" + str(flag.flag_state) + "/" + str(resource_id) + "," + str(planet_id) + "," + str(self.game.get_my_player().buildings.index(flag.final_target)) + "," + "farm"
        elif isinstance(flag, tuple):
            if flag[2] == Flag.LAND:
                action_string = str(self.game.player_id)+"/"+player_object+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            elif flag[2] == 'TAKEOFF':
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            elif flag[2] == 'WORMHOLE':
                action_string = str(self.game.player_id)+"/"+str(player_object)+"/"+str(flag[2])+"/"+str(flag[0][0])+","+str(flag[0][1])+","+str(flag[1][0])+","+str(flag[1][1])
            else:
                action_string = str(self.game.player_id)+"/"+player_object+"/"+flag[0]+"/"+flag[1]
        elif isinstance(flag, str):
            if flag == 'UNLOAD':
                action_string = str(self.game.player_id)+"/"+str(player_object.id)+"/"+flag+"/"+str(player_object.planet_id)+","+str(player_object.sun_id)
        self.server.add_change(action_string)
    
    def pull_change(self):
        to_remove = []
        for i in self.server.get_changes(self.game.player_id, self.refresh_counter):
            self.game.changes.append(i)
        for change_string in self.game.changes:
            if int(change_string.split("/")[4]) <= self.refresh_counter:
                self.do_action(change_string)
                to_remove.append(change_string)
        for tR in to_remove:
            self.game.changes.remove(tR)

    def strip_and_split(self, to_strip_and_split):
        return to_strip_and_split.strip('[').strip(']').split(',')

    def change_to_int(self, to_change):
        for i in range(0, len(to_change)):
            to_change[i] = math.trunc(float(to_change[i]))
        return to_change
    
    def do_action(self, change_string):
        change_informations = change_string.split("/")
        action_player_id = int(change_informations[0])
        unit_index = change_informations[1].split(",")
        action = change_informations[2]
        target = change_informations[3]
        refresh = int(change_informations[4])
        if action in (str(Flag.MOVE), str(Flag.STANDBY), str(Flag.PATROL)):
            target = self.change_to_int(self.strip_and_split(target))
            self.game.make_formation(action_player_id, unit_index, target, action)
            
        elif action == str(Flag.GROUND_MOVE):
            target = self.change_to_int(self.strip_and_split(target))
            self.game.make_formation(action_player_id, unit_index, target, action)
            # for i in unitIndex:
            # if i != '':
            # self.game.players[actionplayer_id].units[int(i)].changeFlag(t.Target([int(target[0]),int(target[1]),int(target[2])]),int(action))
        
        elif action == str(Flag.FINISH_BUILD):
            self.game.resume_building(action_player_id, int(target), unit_index)
            
        elif action == str(Flag.BUILD):
            target = self.change_to_int(self.strip_and_split(target))
            if len(target) == 5:
                self.game.build_building(action_player_id, target, int(action), unit_index, int(target[3]))
            else:
                self.game.build_building(action_player_id, target, int(action), unit_index, int(target[3]), int(target[4]), int(target[5]))
                        
        elif action == str(Flag.ATTACK_BUILDING):
            target = self.change_to_int(self.strip_and_split(target))
            self.game.make_space_building_attack(action_player_id, target, unit_index)

        elif action == str(Flag.ATTACK):
            target = target.split(",")
            self.game.make_units_attack(action_player_id, unit_index, int(target[1]), int(target[0]), target[2])
                    
        elif action == str(Flag.LAND):
            target = target.split(',')
            self.game.make_unit_land(action_player_id, int(unit_index[0]), int(target[0]), int(target[1]))
            
        elif action == 'TAKEOFF':
            target = target.split(',')
            unit = self.game.players[action_player_id].units[int(unit_index[0])]
            planet = self.game.galaxy.solarSystemList[int(target[1])].planets[int(target[0])]
            self.game.take_off(unit, planet, action_player_id)
            if action_player_id == self.game.player_id:
                cam = self.game.get_current_camera()
                cam.position = [unit.position[0], unit.position[1]]
                cam.place_over_planet()
                self.view.changeBackground('GALAXY')

        elif action == 'WORMHOLE':
            target = self.change_to_int(self.strip_and_split(target))
            mother_ship = self.game.players[action_player_id].motherships[int(unit_index[0])]
            self.game.make_worm_hole(action_player_id, [target[0],target[1]], [target[2],target[3]], mother_ship)

        elif action == 'UNLOAD':
            target = target.split(',')
            self.game.make_zone_unload(int(unit_index[0]), action_player_id, int(target[0]), int(target[1]))

        elif action == str(Flag.WORMHOLE):
            target = self.change_to_int(self.strip_and_split(target))
            self.game.make_unit_go_to_wormhole(unit_index, action_player_id, target[0])

        elif action == str(Flag.NOTIFICATION):
            target = self.change_to_int(self.strip_and_split(target))
            self.game.make_notification(action_player_id, target, unit_index)

        elif action == str(Flag.LOAD):
            target = target.split(',')
            self.game.load_unit(unit_index, int(target[1]), int(target[2]), action_player_id)
                
        elif action == str(Flag.GATHER):
            target = target.split(',')
            self.game.make_units_gather(action_player_id, unit_index, int(target[1]), int(target[0]), int(target[2]))

        elif action == str(Flag.GROUND_GATHER):
            target = target.split(',')
            self.game.make_ground_units_gather(action_player_id, unit_index, int(target[0]), int(target[1]), int(target[2]), target[3])
        
        elif action == str(Flag.CREATE):
            self.game.create_unit(action_player_id, int(unit_index[0]), int(target))

        elif action == str(Flag.CHEAT):
            self.game.cheat_player(action_player_id, target)
        
        elif action == str(Flag.CHANGE_RALLY_POINT):
            target = self.change_to_int(self.strip_and_split(target))
            if int(unit_index[0]) < len(self.game.players[action_player_id].buildings) and unit_index[0]:
                self.game.players[action_player_id].buildings[int(unit_index[0])].change_flag(target, int(action))
        
        elif action == str(Flag.CANCEL_UNIT):
            self.game.cancel_unit(action_player_id, int(target), int(unit_index[0]))

        elif action == str(Flag.CANCEL_TECH):
            self.game.cancel_tech(action_player_id, int(target), int(unit_index[0]))

        elif action == str(Flag.DESTROY):
            self.game.kill_unit((int(unit_index[0]),action_player_id,False))
        
        elif action == str(Flag.DESTROY_ALL):
            self.game.kill_player(action_player_id)

        elif action == str(Flag.LINK_WAYPOINTS):
            target = self.change_to_int(self.strip_and_split(target))
            self.game.link_waypoints(action_player_id, target[0], target[1], target[2])
        
        elif action == str(Flag.CHANGE_FORMATION):
            self.game.change_formation(action_player_id, int(target), unit_index, Flag.MOVE)

        elif action == str(Flag.BUY_TECH):
            target = self.change_to_int(self.strip_and_split(target))
            techType = ""
            for i in unit_index:
                techType += i
            self.game.buy_tech(action_player_id, techType, target[0], target[1])

        elif action == str(Flag.TRADE):
            target = self.strip_and_split(target)
            self.game.trade_actions(action_player_id, target, unit_index)
                
        elif action == str(Flag.DEMAND_ALLIANCE):
            self.game.demand_alliance(action_player_id, int(unit_index[0]), target)
            self.view.refreshAlliances()
            
        elif action == str(Flag.HEAL):
            target = self.change_to_int(self.strip_and_split(target))
            self.game.heal_unit_for_real(action_player_id, target, int(unit_index[0]))

    def end_game(self, scores=0):
        self.died = True
        self.view.showGameIsFinished()
        self.view.scores = self.view.fScore(scores)
        self.view.changeFrame(self.view.scores)

    def send_kill_player(self):
        if self.view.currentFrame == self.view.gameFrame:
            if self.server:
                player_id = self.game.player_id
                self.push_change(player_id, Flag(player_id, player_id, Flag.DESTROY_ALL))
            else:
                self.view.root.destroy()
        else:
            self.view.root.destroy()

    def remove_player(self):
        if self.view.currentFrame == self.view.gameFrame:
            self.died = True
            self.view.selectedOnglet = self.view.SELECTED_CHAT
            self.send_message('a quitté la partie')
            self.server.remove_player(self.game.players[self.game.player_id].name, self.game.player_id)
            
if __name__ == '__main__':
    c = Client()
