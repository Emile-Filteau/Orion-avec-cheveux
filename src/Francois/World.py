# -*- coding: iso-8859-1 -*-
import random
from Target import *
import math
#Echelle pour les objets de la galaxie:
#Grandeur: (1000x1000)xNbJoueur
#Un systeme solaire: 200x200
#Un soleil(�toile): 8x8
#une plan�te: 4x4
#Vaisseau m�re: 3x3
#WayPoint: 2x2
#Autres vaisseau: 1x1
#Ceci n'est qu'une �chelle donc n'importe quel grandeur dans la vue est bonne
#tant qu'on respecte cette �chelle pour les grandeurs

#Classe qui represente la galaxie en entier.
class Galaxy():
    def __init__(self,nbPlayer, seed):
        self.banSpawnArea = []
        self.width=(nbPlayer)*1000
        self.height=(nbPlayer)*1000
        self.depth=(nbPlayer)*1000
        self.seed = seed
        self.spawnPoints = []
        random.seed(self.seed)
        self.solarSystemList = []
        for i in range(1,nbPlayer*(6+(nbPlayer-2))):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                tempX=(random.random()*self.width)-self.width/2
                tempY=(random.random()*self.height)-self.height/2
                placeFound = True
                #Conditions de placement des soleils
                if tempX < -1*(self.width/2)+150 or tempX > self.width/2-150:
                    placeFound = False
                if tempY < -1*(self.height/2)+150 or tempY > self.height/2-150: 
                    placeFound = False
                for j in self.solarSystemList:
                    if tempX > j.sunPosition[0]-250 and tempX < j.sunPosition[0]+250:
                        if tempY > j.sunPosition[1]-250 and tempY < j.sunPosition[1]+250:
                            placeFound = False
            self.solarSystemList.append(SolarSystem(tempX,tempY,0))
            
    def getSpawnPoint(self):
        random.seed(self.seed)
        find = False
        while(find == False):
            x =(random.random()*self.width)-self.width/2
            y = (random.random()*self.height)-self.height/2

            for i in self.solarSystemList:
                if((x > i.sunPosition[0] - 10 and x < i.sunPosition[0] + 10)
                    and (y > i.sunPosition[1] - 10) and y < i.sunPosition[1]+10):
                    find = False
                    break
                else:
                    find = True
            
            
            if find == True:
                for i in self.spawnPoints:
                    if((x > i[0] - 200 and x < i[0] + 200)
                        and (y > i[1] - 200) and (y < i[1] + 200)):
                        find = False
                        break
                    else:
                        find = True

        self.spawnPoints.append((x,y,0))
        return [x,y,0]
        
#Classe qui represente 1 seul systeme solaire                            
class SolarSystem():
    def __init__(self,sunX,sunY,sunZ):
        self.sunPosition = (sunX,sunY,sunZ)
        self.planets = []
        self.nebulas = []
        self.asteroids = []
        self.discovered = False
        nPlanet = int(random.random()*6)+1
        nRes = int(random.random()*4)
        nNebu = 0
        nAstero = 0
        for i  in range(0,nRes):
            type = int(random.random())
            if type < 0.5:
                nNebu +=1
            else:
                nAstero +=1
                
        for i in range(0,nPlanet):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = (random.random()*250)-125
                tempY = (random.random()*250)-125
                #Condition de placement des planetes
                if tempX > -40 and tempX < 40:
                    if tempY > -40 and tempY < 40:
                        placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-20 and self.sunPosition[0]+tempX < j.position[0]+20:
                        if self.sunPosition[1]+tempY > j.position[1]-20 and self.sunPosition[1]+tempY < j.position[1]+20:
                            placeFound = False
            self.planets.append(AstronomicalObject('planet', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY)))

        for i in range(0,nNebu):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = (random.random()*250)-125
                tempY = (random.random()*250)-125
                #Condition de placement des nebuleuses
                if tempX > -40 and tempX < 40:
                    if tempY > -40 and tempY < 40:
                        placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-20 and self.sunPosition[0]+tempX < j.position[0]+20:
                        if self.sunPosition[1]+tempY > j.position[1]-20 and self.sunPosition[1]+tempY < j.position[1]+20:
                            placeFound = False
                for k in self.nebulas:
                    if self.sunPosition[0]+tempX > k.position[0]-20 and self.sunPosition[0]+tempX < k.position[0]+20:
                        if self.sunPosition[1]+tempY > k.position[1]-20 and self.sunPosition[1]+tempY < k.position[1]+20:
                            placeFound = False
            self.nebulas.append(AstronomicalObject('nebula', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY)))

#Represente un objet spacial (Planete, Meteorite, Nebuleuse)
#Le type represente quel objet parmi les 3
class AstronomicalObject(Target):
    def __init__(self, type, position):
        Target.__init__(self, position)
        self.type = type
        self.mineralQte = 100
        self.gazQte = 100
        self.discovered = False
        if type == 'planet':
            self.landable = True
        else:
            self.landable = False
        if type == 'nebula':
            self.gazQte = math.trunc((random.random()*250)+250)
            self.mineralQte = 0
        elif type == 'asteroid':
            self.mineralQte = math.trunc((random.random()*250)+250)
            self.gazQte = 0 
        