# -*- coding: iso-8859-1 -*-
import Pyro4
import socket
import player

class ControleurServeur(object):
    def __init__(self):
        self.sockets=[]
        self.numClient=0
    
    def addMessage(self, text, num):
        self.sockets[num].setText(text)

    def getNewMessage(self, num):
        messages=[]
        for i in range(0,len(self.sockets)):
            if i != num:
                messages.append(self.sockets[i].getText())
        if len(messages) == 0:
            return ['Aucun message']
        return messages
        
    def getNumSocket(self, player):
        n=0
        for i in range(0,len(self.sockets)):
            if self.sockets[i].getIP() == player.getIP():
                print('a trouver le meme socket que le precedent')
                self.sockets[i]=player
                return i
            n=n+1
        print('ajoute le socket a la fin')
        self.sockets.append(player)
        return n

# le processus qui ecoute les messages des clients
adresse=socket.gethostbyname(socket.getfqdn())
daemon = Pyro4.core.Daemon(host=adresse,port=54440) 
# un objet ControleurServeur() dont les methodes peuvent etre invoquees, 
# connu sous le nom de controleurServeur
daemon.register(ControleurServeur(), "controleurServeur")  
 
 # juste pour voir quelque chose sur la console du serveur
print("Serveur Pyro actif sous le nom \'controleurServeur\' avec l'adresse "+adresse)

#on demarre l'ecoute des requetes
daemon.requestLoop()