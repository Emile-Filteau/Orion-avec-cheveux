# -*- coding: UTF-8 -*-
from Unit import u
from Flag import *
import socket

#Represente un joueur
class Player():
    def __init__(self, name, id , colorId, civilization=None):
        self.name = name
        self.civilization = civilization
        self.colorId = colorId
        self.selectedObjects = [] #Liste des unites selectionnes
        self.units = [] #Liste de toute les unites
        self.buildings = [] #Liste de tous les buildings
        self.id = id #Numero du joueur dans la liste de joueur
        self.startPos = [0,0,0] #Position de depart du joueur (pour le mothership)
        self.motherShip = None
        self.formation="carre"
        self.currentPlanet = None
        self.gaz = 100
        self.mineral = 100

    def addBaseUnits(self, startPos):
        self.units.append(u.Mothership('Mothership', u.Unit.MOTHERSHIP,startPos, self.id))
        self.motherShip = self.units[0]
        self.units.append(u.Unit('Scout', u.Unit.SCOUT,[startPos[0] + 20, startPos[1] + 20 ,0], self.id))
        self.units.append(u.GatherShip('Gather ship', u.Unit.CARGO,[startPos[0] + 40, startPos[1]+40], self.id))
        
    #Ajoute une camera au joueur seulement quand la partie commence    
    def addCamera(self, galaxy, taille):
        pos = [0,0,0]
        for i in self.units:
            if i.type == i.MOTHERSHIP:
                pos = i.position
        default = [pos[0],pos[1]]
        self.camera = Camera(default,galaxy, taille)
        if default[0]-self.camera.screenCenter[0] < (self.camera.galaxy.width*-1)/2:
            self.camera.position[0] = (self.camera.galaxy.width*-1)/2+self.camera.screenCenter[0]
        if default[0]+self.camera.screenCenter[0] > self.camera.galaxy.width/2:
            self.camera.position[0] = (self.camera.galaxy.width)/2-self.camera.screenCenter[0]
        if default[1]-self.camera.screenCenter[1] < (self.camera.galaxy.height*-1)/2:
            self.camera.position[1] = (self.camera.galaxy.height*-1)/2+self.camera.screenCenter[1]
        if default[1]+self.camera.screenCenter[1] > self.camera.galaxy.height/2:
            self.camera.position[1] = (self.camera.galaxy.height)/2-self.camera.screenCenter[1]
        
    def inViewRange(self, position):
        x = position[0]
        y = position[1]
        for i in self.units:
            if i.isAlive:
                if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                    if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                        if i.name == 'Transport':
                            if not i.landed:
                                return True
                        else:
                            return True
        return False
#Represente la camera            
class Camera():
    def __init__(self, defaultPos, galaxy, taille):
        self.defaultPos = defaultPos
        self.position = defaultPos
        self.screenCenter = (taille/2,(taille/2)-100)
        self.screenWidth = taille
        self.screenHeight = taille-200
        self.galaxy = galaxy #reference a la galaxie
        self.movingDirection = []
        
    #Pour calculer la distance entre la camera et un point
    def calcDistance(self, position):
        distX = position[0] - self.position[0]
        distY = position[1] - self.position[1]
        return [distX+self.screenCenter[0], distY+self.screenCenter[1]]
    
    #Pour calculer un point dans la galaxie a partir d'un point dans l'ecran
    def calcPointInWorld(self, x,y):
        dist = self.calcDistance([x,y])
        rX = self.position[0]-self.screenCenter[0]+x
        rY = self.position[1]-self.screenCenter[1]+y
        return [rX,rY,0]
    
    #Pour calculer un point sur la minimap a partir d'un point dans l'espace
    def calcPointOnMap(self, x, y):
        rX = x/200 * self.galaxy.width - self.galaxy.width/2
        rY = y/200 * self.galaxy.height - self.galaxy.height/2
        if rX < 0-self.galaxy.width/2+self.screenWidth/2:
            rX = 0-self.galaxy.width/2+self.screenWidth/2
        elif rX > self.galaxy.width/2-self.screenWidth/2:
            rX = self.galaxy.width/2-self.screenWidth/2
            
        if rY < 0-self.galaxy.height/2+self.screenHeight/2:
            rY = 0-self.galaxy.height/2+self.screenHeight/2
        elif rY > self.galaxy.height/2-self.screenHeight/2:
            rY = self.galaxy.height/2-self.screenHeight/2
        return [rX, rY]
    
    #Pour calculer un point dans la galaxie a partir d'un point dans la minimap
    def calcPointMinimap(self,x ,y ):
        rX = x/200 * self.galaxy.width - self.galaxy.width/2
        rY = y/200 * self.galaxy.height - self.galaxy.height/2
        return [rX, rY]
    
    #Retourne Vrai si la position est visible par la camera en ce moment
    def isInFOV(self, position):
        if position[0] > self.position[0]-self.screenWidth/2-20 and position[0] < self.position[0]+self.screenWidth/2+20:
            if position[1] > self.position[1]-self.screenHeight/2-20 and position[1] < self.position[1]+self.screenHeight/2+20:
                return True
        return False
    
    #Deplace la camera selon le contenu de la liste movingDirection
    def move(self):
        if 'LEFT' in self.movingDirection:
            if self.position[0] > (self.galaxy.width*-1)/2+self.screenCenter[0]:
                self.position[0]-=10
        elif 'RIGHT' in self.movingDirection:
            if self.position[0] < self.galaxy.width/2 - self.screenCenter[0]:
                self.position[0]+=10
        if 'UP' in self.movingDirection:
            if self.position[1] > (self.galaxy.height*-1)/2 + self.screenCenter[1]:
                self.position[1]-=10
        elif 'DOWN' in self.movingDirection:
            if self.position[1] < self.galaxy.height/2 - self.screenCenter[1]:
                self.position[1]+=10

