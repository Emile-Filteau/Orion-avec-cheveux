# -*- coding: UTF-8 -*-
import Pyro4
import socket
import sys
from time import time


class Server(object):
    def __init__(self):
        self.sockets = []
        self.refreshes = []
        self.game_is_started = False
        self.is_stopped = True
        self.seed = int(time())
        self.messages = [
            [-1, 'Choisissez la couleur de votre battalion', False],
            [-1, '________________________________________________________________', False],
            [-1, 'Le but est détruire le vaisseau mère des autres équipes', False],
            [-1, 'en bâtissant votre propre battalion et en dominant.', False],
            [-1, '________________________________________________________________', False]]
        self.change_list = []
        self.ready_players = []
        self.choice_colors = [["Orange", False], ["Rouge", False], ["Bleu", False], ["Vert", False], ["Jaune", False], ["Brun", False], ["Blanc", False], ["Rose", False]]
    
    def start_game(self):
        self.seed = int(time())
        self.game_is_started = True
        self.is_stopped = False
        for i in range(0, self.get_number_of_players()):
            self.change_list.append([])
            self.refreshes.append(0)
            self.ready_players.append(False)
    
    def remove_player(self, login, player_id):
        self.sockets[player_id][2] = True
        if player_id == 0:
            self.is_stopped = True
            self.game_is_started = False
            self.refreshes = []
            self.change_list = []
            self.sockets = []
            self.ready_players = []
            self.choice_colors = [["Orange", False], ["Rouge", False], ["Bleu", False], ["Vert", False], ["Jaune", False], ["Brun", False], ["Blanc", False], ["Rose", False]]
            self.messages = [[-1, 'Choisissez la couleur de votre battalion',False],[-1, '________________________________________________________________',False],[-1, 'Le but est détruire le vaisseau mère des autres équipes',False],[-1, 'en bâtissant votre propre battalion et en dominant.',False],[-1, '________________________________________________________________',False]]
    
    def add_message(self, text, name, id_player, allies):
        self.messages.append([id_player, name+" : "+text, allies])
        
    def add_change(self, change):
        change = change+'/'+str(self.decide_action_refresh())
        for ch in self.change_list:
            ch.append(change)
  
    def is_this_color_chosen(self, color_name, player_id):
        for i in range(0, len(self.choice_colors)):
            if color_name == self.choice_colors[i][0]:
                color_id = i
        if self.choice_colors[color_id][1]:
            return True
        else:
            if self.sockets[player_id][3] != -1:
                self.choice_colors[self.sockets[player_id][3]][1] = False
            self.sockets[player_id][3] = color_id
            self.choice_colors[color_id][1] = True
            return False

    def first_color_not_chosen(self, player_id):
        for color in self.choice_colors:
            if not color[1]:
                color[1] = True
                self.sockets[player_id][3] = self.choice_colors.index(color)
                break
      
    def ai_color(self):
        for i in self.choice_colors:
            if not i[1]:
                i[1] = True
                return self.choice_colors.index(i)
              
    def refresh_player(self, player_id, refresh):
        self.refreshes[player_id] = refresh
    
    def decide_action_refresh(self):
        return max(self.refreshes)+2

    def frame_difference(self):
        frame_list = []
        for refresh in self.refreshes:
            frame_list.append(refresh)
        return max(frame_list) - min(frame_list)

    def am_i_too_high(self, playerId):
        refresh = []
        for r in range(len(self.refreshes)):
            if not self.sockets[r][2] and not self.sockets[r][4]:
                refresh.append(self.refreshes[r])
        min_frame = min(refresh)
        if self.refreshes[playerId] - min_frame > 5:
            return (self.refreshes[playerId] - min_frame)*50
        return 50

    def is_everyone_ready(self, player_id):
        self.ready_players[player_id] = True
        for i in self.ready_players:
            if not i:
                return False
        return True
                
    def get_number_of_players(self):
        return len(self.sockets)
      
    def get_changes(self, num, refresh):
        self.refreshes[num] = refresh
        changes = self.change_list[num]
        self.change_list[num] = []
        return changes
       
    def get_num_socket(self, login, ip, ia):
        if len(self.sockets) < 8:
            for s in self.sockets:
                if s[1].upper() == login.upper():
                    return -1
            self.sockets.append([ip, login, False, -1, ia])
            return len(self.sockets)-1
          

if len(sys.argv) > 1:
    address = sys.argv[1]
else:
    address = socket.gethostbyname(socket.getfqdn())
try:
    daemon = Pyro4.core.Daemon(host=address, port=54400)
    uri = daemon.register(Server(), "ServeurOrion")
    print("Orion Server is active at address: " + address + ' on port 54400')
    daemon.requestLoop()
except socket.error:
    print("Error in server ! The server did not start")
    sys.exit(1)