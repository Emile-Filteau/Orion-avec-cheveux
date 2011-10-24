# -*- coding: UTF-8 -*-
import Pyro4
import socket
from time import time

class ControleurServeur(object):
    def __init__(self):
        self.sockets=[]
        self.refreshes=[]
        self.gameIsStarted = False
        self.isStopped = True
        self.seed = int(time())
        self.mess = ['Système de chat de Orion']
        self.changeList = [] 
    
    def getSeed(self):
        return self.seed;
    
    def getSockets(self):
        return self.sockets

    def isGameStopped(self):
        return self.isStopped
    
    def isGameStarted(self):
        return self.gameIsStarted
    
    def startGame(self):
        self.seed = int(time())
        self.gameIsStarted = True
        self.isStopped = False
        #J'initie mon tableau de changements et de refreshes
        for i in range(0, self.getNumberOfPlayers()):
            self.changeList.append([])
            self.refreshes.append(0)
    
    def removePlayer(self, ip, login, playerId):
        self.sockets[playerId][2] = True
        if playerId == 0:
            self.isStopped = True
            self.gameIsStarted = False
            self.refreshes = []
            self.changeList = []
            self.sockets = []
            self.mess = ['Système de chat de Orion']
    
    def addMessage(self, text, name):
        self.mess.append(name+': '+text)
    
    def getMessage(self):
        return self.mess
        
    def addChange(self, change):
        #décider à quel frame effectuer l'action
        #playerId = int(change.split("/")[0])
        change = change+'/'+str(self.decideActionRefresh())
        for ch in self.changeList:
            ch.append(change)
        
    def refreshPlayer(self, playerId, refresh):
        self.refreshes[playerId] = refresh
    
    def decideActionRefresh(self):
        #décide à quel refresh les clients doivent effectuer la prochaine action
        return (max(self.refreshes)+2)

    def frameDifference(self):
        frameList = []
        for player in self.sockets :
            frameList.append(player.getRefresh)
        #Je détermine le frame maximum et le frame minimum de tout les clients
        frameMax = max(frameList)
        frameMin = min(frameList)
        return (frameMax-frameMin)
    
    # Méthode qui détermine et isole les joueurs dont le frame courant est trop élevé par apport aux autres
    def amITooHigh(self, playerId):
        refresh = []
        #Je détermine le frame minimum de tout les clients
        for r in range(len(self.refreshes)):
            if self.sockets[r][2] != True:
                refresh.append(self.refreshes[r])
        frameMin = min(refresh)
        #Détermine si l'écart entre les joueurs est trop grand (15 étant une valeur arbitraire, destinée à être modifié)
        if self.refreshes[playerId] - frameMin > 5:
            return (self.refreshes[playerId] - frameMin)*50
        return 50
                
    def getNumberOfPlayers(self):
        return len(self.sockets)
      
    def getChange(self,num,refresh):
        self.refreshes[num] = refresh
        changes = self.changeList[num]
        self.changeList[num] = []
        #Si ce joueur fais partie de la liste des joueurs trop rapide, je rajoute le flag à la fin du tableau
        #if self.playersTooDamnHigh().count(num) > 0 :
        #    change.append("*",self.frameDifference())
        return changes
       
    def getNumSocket(self, login, ip):
        n=0
        for i in range(0,len(self.sockets)):
            if self.sockets[i][0] == ip:
                print('a trouver le meme socket que le precedent')
                self.sockets[i]=[ip,login,False]
                return i
            n=n+1
        print('ajoute le socket a la fin')
        if len(self.sockets) < 8:
            self.sockets.append([ip,login,False])
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


        