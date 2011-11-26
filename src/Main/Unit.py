# -*- coding: UTF-8 -*-
from Target import *
from Flag import *
import World as w
import Player as p
import Building as b
from Helper import *
import math

class Unit(PlayerObject):
    DEFAULT = 0
    SCOUT = 1
    ATTACK_SHIP = 2
    TRANSPORT = 3
    CARGO = 4
    GROUND_UNIT = 5
    GROUND_GATHER = 6
    SPECIAL_GATHER = 7
    GROUND_ATTACK = 8
    GROUND_BUILDER_UNIT = 9
    NAME = ('Unité','Scout', "Vaisseau d'attaque", "Vaisseau de Transport", "Cargo", 'Unité terrestre', 'Unité de collecte', '', 'Unité d\'attaque', 'Unité de construction')
    MINERAL=0
    GAS=1
    FOOD=2
    SIZE=((0,0),  (18,15), (28,32), (32,29), (20,30),(24,24),(23,37), (0,0), (36,33),(20,20))
    MAX_HP = (50, 50, 100,125, 75, 100, 100, 100, 100,100)
    MOVE_SPEED=(1.0,  4.0, 2.0, 3.0, 3.0, 5.0, 5.0, 3.0, 3.5, 4.0)
    ATTACK_SPEED=(0,0,10,0,0,0,0,0,15,0)
    ATTACK_DAMAGE=(0,0,5,0,0,0,0,0,12,0)
    ATTACK_RANGE=(0,0,150,0,0,0,0,0,150,0)
    BUILD_TIME=(300,  200, 400, 300, 250, 200, 200, 200, 200, 200)
    BUILD_COST=((50,50,1),  (50,0,1), (150,100,1), (75,20,1), (50,10,1), (50,10,1),(50,10,1), (50,15,1), (60,60,1), (30,25,1))
    VIEW_RANGE=(150,  200, 150, 175, 175,200, 200, 200, 200, 200)
    
    def __init__(self, type, position, owner):
        PlayerObject.__init__(self, type, position, owner)
        self.viewRange = self.VIEW_RANGE[type]
        self.hitpoints = self.MAX_HP[type]
        self.maxHP=self.hitpoints
        self.buildTime = self.BUILD_TIME[type]
        self.buildCost = self.BUILD_COST[type]
        self.name = self.NAME[type]
        self.moveSpeed = self.MOVE_SPEED[type]

    def action(self, parent):
        if self.flag.flagState == FlagState.MOVE or self.flag.flagState == FlagState.GROUND_MOVE:
            self.move()
        elif self.flag.flagState == FlagState.ATTACK:
            if isinstance(self.flag.finalTarget, TransportShip):
                if self.flag.finalTarget.landed:
                    parent.game.setAStandByFlag(self)
            killedIndex = self.attack(parent.game.players)
            if killedIndex[0] > -1:
                parent.killUnit(killedIndex)
        elif self.flag.flagState == FlagState.PATROL:
            self.patrol()
        elif self.flag.flagState == FlagState.BUILD:
            self.build(self.flag.finalTarget)
    
    #La deplace d'un pas vers son flag et si elle est rendu, elle change arrete de bouger    
    def move(self):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.moveSpeed:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            if self.flag.flagState == FlagState.MOVE or self.flag.flagState == FlagState.GROUND_MOVE:
                self.flag.flagState = FlagState.STANDBY
            elif self.flag.flagState == FlagState.MOVE+FlagState.ATTACK:
                self.flag.flagState = FlagState.ATTACK
        else:
            angle = Helper.calcAngle(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
            temp = Helper.getAngledPoint(angle, self.moveSpeed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]

    def patrol(self):
        arrived = True
        if self.position[0] < self.flag.finalTarget.position[0] or self.position[0] > self.flag.finalTarget.position[0]:
                if self.position[1] < self.flag.finalTarget.position[1] or self.position[1] > self.flag.finalTarget.position[1]:
                    self.move()
                    arrived = False
        if arrived == True:
            self.before = self.flag.initialTarget
            self.flag.initialTarget = self.flag.finalTarget
            self.flag.finalTarget = self.before
            self.move()
        return None

    def select(self, position):
        if self.isAlive:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def boxSelect(self, startPos, endPos):
        if self.isAlive:
            if self.position[0] > startPos[0] - self.SIZE[self.type][0]/2 and self.position[0] < endPos[0] + self.SIZE[self.type][0]/2:
                if self.position[1] > startPos[1] - self.SIZE[self.type][1]/2 and  self.position[1] < endPos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def build(self, building):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) >= self.moveSpeed:
            self.move()
        else:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            
            if building.buildingTimer < building.TIME[building.type]:
                building.buildingTimer += 1
            else:
                building.finished = True
                self.flag.flagState = FlagState.STANDBY
            
    #Efface la unit
    def eraseUnit(self):
        self.flag.flagState = 0
        self.position = [-1500,-1500,0]

    #Applique les bonus du Unit selon les upgrades
    def applyBonuses(self, bonuses):
        self.moveSpeed = self.MOVE_SPEED[self.type]+bonuses[p.Player.MOVE_SPEED_BONUS]
        self.viewRange = self.VIEW_RANGE[self.type]+bonuses[p.Player.VIEW_RANGE_BONUS]
        
    #Retourne le flag de la unit    
    def getFlag(self):
        return self.flag
              
class SpaceUnit(Unit):
    def __init__(self,  type, position, owner):
        Unit.__init__(self, type, position, owner)

class GroundUnit(Unit):
    def __init__(self, type, position, owner, planetId, sunId, isLanded = False):
        Unit.__init__(self, type, position, owner)
        self.sunId = sunId
        self.planetId = planetId
        self.planet = None
        self.isLanded = isLanded

    def isInRange(self, position, range, onPlanet = False, planetId = -1, solarSystemId = -1):
        if self.isLanded and onPlanet:
            if self.sunId == solarSystemId and self.planetId == planetId:
                if self.position[0] > position[0]-range and self.position[0] < position[0]+range:
                    if self.position[1] > position[1]-range and self.position[1] < position[1]+range:
                        return self
        return None

    def land(self, planet, position):
        self.isLanded = True
        self.position = position
        self.planet = planet
        self.planetId = planet.id
        self.sunId = planet.solarSystem.sunId
        planet.units.append(self)

    def takeOff(self):
        self.isLanded = False
        self.planetId = -1
        self.sunId = -1
        self.planet = None

    def action(self, parent):
        if self.flag.flagState == FlagState.LOAD:
            self.load(parent.game)
        else:
            Unit.action(self, parent)

    def load(self, game):
        landingZone = self.flag.finalTarget
        planet = game.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        arrived = True
        if self.position[0] < landingZone.position[0] or self.position[0] > landingZone.position[0]:
            if self.position[1] < landingZone.position[1] or self.position[1] > landingZone.position[1]:
                arrived = False
                self.move()
        if arrived and landingZone.LandedShip != None:
            self.planet = None
            self.position = [-100000, -100000]
            self.planetId = -1
            self.sunId = -1
            planet.units.pop(planet.units.index(self))
            landingZone.LandedShip.units.append(self)
            if self in game.players[self.owner].selectedObjects:
                game.players[self.owner].selectedObjects.pop(game.players[self.owner].selectedObjects.index(self))
            self.flag.flagState = FlagState.STANDBY

class GroundBuilderUnit(GroundUnit):
    def __init__(self,  type, position, owner, planetId, sunId, isLanded = False):
        GroundUnit.__init__(self,  type, position, owner, planetId, sunId, isLanded)

    def action(self, parent):
        if self.flag.flagState == FlagState.BUILD:
            self.build(self.flag.finalTarget, parent)
        else:
            GroundUnit.action(self, parent)

    def build(self, building, player):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) >= self.moveSpeed:
            self.move()
        else:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            
            if building.buildingTimer < building.TIME[building.type]:
                building.buildingTimer += 1
            else:
                building.finished = True
                self.flag.flagState = FlagState.STANDBY
                if building.type == b.Building.FARM:
                    player.MAX_FOOD +=5

    def load(self, game):
        landingZone = self.flag.finalTarget
        planet = game.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        arrived = True
        if self.position[0] < landingZone.position[0] or self.position[0] > landingZone.position[0]:
            if self.position[1] < landingZone.position[1] or self.position[1] > landingZone.position[1]:
                arrived = False
                self.move()
        if arrived and landingZone.LandedShip != None:
            self.planet = None
            self.position = [-100000, -100000]
            self.planetId = -1
            self.sunId = -1
            planet.units.pop(planet.units.index(self))
            landingZone.LandedShip.units.append(self)
            if self in game.players[self.owner].selectedObjects:
                game.players[self.owner].selectedObjects.pop(game.players[self.owner].selectedObjects.index(self))
            self.flag.flagState = FlagState.STANDBY
               
            
class GroundGatherUnit(GroundUnit):
    def __init__(self,  type, position, owner, planetId, sunId, isLanded = False):
        GroundUnit.__init__(self, type, position, owner, planetId, sunId, isLanded)
        self.maxGather = 50
        self.gatherSpeed = 20
        self.container = [0,0]
        self.returning = False

    def action(self, parent):
        if self.flag.flagState == FlagState.GROUND_GATHER:
            self.gather(parent, parent.game)
        else:
            GroundUnit.action(self, parent)

    def gather(self, player, game):
        ressource = self.flag.finalTarget
        arrived = True
        if isinstance(ressource, w.MineralStack) or isinstance(ressource, w.GazStack):
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gatherSpeed==0:
                    if isinstance(ressource, w.MineralStack):
                        if self.container[0] < self.maxGather:
                            if ressource.nbMinerals >= 5:
                                self.container[0]+=5
                                ressource.nbMinerals-=5
                            else:
                                self.container[0]+=ressource.nbMinerals
                                ressource.nbMinerals = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget =player.getNearestReturnRessourceCenterOnSpace(self.position, self)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = 20
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenterOnSpace(self.position, self)
                    else:
                        if self.container[1]<self.maxGather:
                            if ressource.nbGaz >= 5:
                                self.container[1]+=5
                                ressource.nbGaz-=5
                            else:
                                self.container[1]+=ressource.nbGaz
                                ressource.nbGaz = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.getNearestReturnRessourceCenterOnSpace(self.position, self)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = 20
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenterOnSpace(self.position, self)
                else:
                    self.gatherSpeed-=1
        else:
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                player.ressources[player.MINERAL] += self.container[0]
                player.ressources[player.GAS] += self.container[1]
                self.container[0] = 0
                self.container[1] = 0
                if isinstance(self.flag.initialTarget, w.MineralStack) or isinstance(self.flag.initialTarget, w.GazStack):
                    self.flag.finalTarget = self.flag.initialTarget
                    if isinstance(self.flag.initialTarget, w.MineralStack):
                        if self.flag.finalTarget.nbMinerals == 0:
                            self.flag.flagState = FlagState.STANDBY
                    else:
                        if self.flag.finalTarget.nbGaz == 0:
                            self.flag.flagState = FlagState.STANDBY
                else:
                    self.flag.finalTarget = self.position
                    self.flag.flagState = FlagState.STANDBY
 
class GroundAttackUnit(GroundUnit):
    def __init__(self,  type, position, owner, planetId, sunId, isLanded = False):
        GroundUnit.__init__(self,  type, position, owner, planetId, sunId, isLanded)
        self.range=self.ATTACK_RANGE[type]
        self.AttackSpeed=self.ATTACK_SPEED[type]
        self.AttackDamage=self.ATTACK_DAMAGE[type]
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.isLanded:
            if self.flag.flagState == FlagState.ATTACK:
                killedIndex = self.attack(parent.game.players)
                if killedIndex[0] > -1:
                    parent.killUnit(killedIndex)
            elif self.flag.flagState == FlagState.PATROL:
                self.patrol()
                parent.game.checkIfEnemyInRange(self, True, self.planetId, self.sunId)
            elif self.flag.flagState == FlagState.STANDBY:
                parent.game.checkIfEnemyInRange(self, True, self.planetId, self.sunId)
            else:
                GroundUnit.action(self, parent)

    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance > self.range :
                self.attackcount=self.AttackSpeed
                self.move()
            else:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    if unitToAttack.takeDammage(self.AttackDamage, players):
                        if isinstance(unitToAttack, b.Building) == False:
                            index = players[unitToAttack.owner].units.index(unitToAttack)
                        else:
                            index = players[unitToAttack.owner].buildings.index(unitToAttack)
                            isBuilding = True
                        killedOwner = unitToAttack.owner
                        self.killCount +=1
                    self.attackcount=self.AttackSpeed
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1)
                    
class SpaceAttackUnit(SpaceUnit):
    def __init__(self,  type, position, owner):
        SpaceUnit.__init__(self,  type, position, owner)
        self.range=self.ATTACK_RANGE[type]
        self.AttackSpeed=self.ATTACK_SPEED[type]
        self.AttackDamage=self.ATTACK_DAMAGE[type]
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.flag.flagState == FlagState.ATTACK:
            if isinstance(self.flag.finalTarget, TransportShip):
                if self.flag.finalTarget.landed:
                    parent.game.setAStandByFlag(self)
            else:
                killedIndex = self.attack(parent.game.players)
                if killedIndex[0] > -1:
                    parent.killUnit(killedIndex)
        elif self.flag.flagState == FlagState.PATROL:
            self.patrol()
            parent.game.checkIfEnemyInRange(self)
        elif self.flag.flagState == FlagState.STANDBY:
            parent.game.checkIfEnemyInRange(self)
        else:
            Unit.action(self, parent)

    def changeFlag(self, finalTarget, state):
        self.attackcount=self.AttackSpeed
        Unit.changeFlag(self, finalTarget, state)
        
    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance > self.range :
                self.attackcount=self.AttackSpeed
                self.move()
            else:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    if unitToAttack.takeDammage(self.AttackDamage, players):
                        if isinstance(unitToAttack, b.Building) == False:
                            index = players[unitToAttack.owner].units.index(unitToAttack)
                        else:
                            index = players[unitToAttack.owner].buildings.index(unitToAttack)
                            isBuilding = True
                        killedOwner = unitToAttack.owner
                        self.killCount +=1
                    self.attackcount=self.AttackSpeed
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1)

    def patrol(self):
        arrived = True
        if self.position[0] < self.flag.finalTarget.position[0] or self.position[0] > self.flag.finalTarget.position[0]:
                if self.position[1] < self.flag.finalTarget.position[1] or self.position[1] > self.flag.finalTarget.position[1]:
                    self.move()
                    arrived = False
        if arrived == True:
            self.before = self.flag.initialTarget
            self.flag.initialTarget = self.flag.finalTarget
            self.flag.finalTarget = self.before

    #Applique les bonus du Unit selon les upgrades
    def applyBonuses(self, bonuses):
        Unit.applyBonuses(self, bonuses)

class TransportShip(SpaceUnit):
    def __init__(self, type, position, owner):
        SpaceUnit.__init__(self,  type, position, owner)
        self.landed = False
        self.capacity = 10
        self.units = []
        self.planetId = -1
        self.sunId = -1
        self.planet = None
        #self.units.append(GroundUnit('Builder', self.GROUND_UNIT, [0,0,0], self.owner,-1,-1))

    def action(self, parent):
        if self.flag.flagState == FlagState.LAND:
            self.land(parent.game)
        else:
            Unit.action(self, parent)


    def isInRange(self, position, range, onPlanet = False, planetId = -1, solarSystemId = -1):
        if self.landed == onPlanet and onPlanet == False:
            return Unit.isInRange(self, position, range)
        return None

    def select(self, position):
        if self.isAlive and not self.landed:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def boxSelect(self, startPos, endPos):
        if self.isAlive and not self.landed:
            if self.position[0] >= startPos[0] - self.SIZE[self.type][0]/2 and self.position[0] <= endPos[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= startPos[1] - self.SIZE[self.type][1]/2 and self.position[1] <= endPos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None
    
    def land(self, game):
        playerId = self.owner
        galaxy = game.galaxy
        planet = self.flag.finalTarget
        planetId = 0
        sunId = 0
        for i in galaxy.solarSystemList:
            for j in i.planets:
                if planet == j:
                    planetId = i.planets.index(j)
                    sunId = galaxy.solarSystemList.index(i)
        self.arrived = True
        if self.position[0] < planet.position[0] or self.position[0] > planet.position[0]:
            if self.position[1] < planet.position[1] or self.position[1] > planet.position[1]:
                self.arrived = False
                self.move()
        if self.arrived:
            player = game.players[playerId]
            player.currentPlanet = planet
            alreadyLanded = False
            for i in planet.landingZones:
                if i.ownerId == playerId:
                    alreadyLanded = True
            if not alreadyLanded:
                if len(planet.landingZones) < 4:
                    landingZone = planet.addLandingZone(playerId, self, game.players[playerId])
                    player.buildings.append(landingZone)
                    player.selectedObjects = []
                    self.landed = True
                    self.planetId = planetId
                    self.sunId = sunId
                    self.planet = planet
                    if playerId == game.playerId:
                        cam = game.players[playerId].camera
                        cam.placeOnLanding(landingZone)
                    x=40
                    for i in self.units:
                        position = [landingZone.position[0] + x, landingZone.position[1] + 5 * self.units.index(i)]
                        i.land(planet, position)
                        x+=25
                    del self.units[:]
                    if self in game.players[game.playerId].selectedObjects:
                        game.players[game.playerId].selectedObjects.pop(game.players[game.playerId].selectedObjects.index(self))
            else:
                landingZone = None
                for i in planet.landingZones:
                    if i.ownerId == playerId:
                        landingZone = i
                if landingZone.LandedShip == None:
                    self.landed = True
                    self.planetId = planetId
                    self.sunId = sunId
                    self.planet = planet
                    if playerId == game.playerId:
                        cam = game.players[playerId].camera
                        cam.placeOnLanding(landingZone)
                    x=40
                    for i in self.units:
                        position = [landingZone.position[0] + x, landingZone.position[1] + 5 * self.units.index(i)]
                        i.land(planet, position)
                        x+=25
                    del self.units[:]
                    landingZone.LandedShip = self
            if playerId == game.playerId:
                game.parent.changeBackground('PLANET')
                game.parent.drawPlanetGround(planet)
            self.flag = Flag (self.position, self.position, FlagState.STANDBY)
        
    def takeOff(self, planet):
        self.landed = False
        for i in planet.landingZones:
            if i.ownerId == self.owner:
                i.LandedShip = None

    def kill(self):
        self.isAlive = False

    def load(self, unit):
        unit.flag = Flag(unit.position, unit.landingZone, FlagState.LOAD)

class GatherShip(SpaceUnit):
    GATHERTIME=20
    def __init__(self,  type, position, owner):
        SpaceUnit.__init__(self, type, position, owner)
        self.maxGather = 50
        self.gatherSpeed = 20
        self.container = [0,0]
        self.returning = False

    def action(self, parent):
        if self.flag.flagState == FlagState.GATHER:
            self.gather(parent, parent.game)
        else:
            Unit.action(self, parent)

    def gather(self, player, game):
        ressource = self.flag.finalTarget
        arrived = True
        if isinstance(self.flag.finalTarget, w.AstronomicalObject):
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gatherSpeed==0:
                    if ressource.type=='asteroid':
                        if self.container[0] < self.maxGather:
                            if ressource.mineralQte >= 5:
                                self.container[0]+=5
                                ressource.mineralQte-=5
                            else:
                                self.container[0]+=ressource.mineralQte
                                ressource.mineralQte = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = 20
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                    else:
                        if self.container[1]<self.maxGather:
                            if ressource.gazQte >= 5:
                                self.container[1]+=5
                                ressource.gazQte-=5
                            else:
                                self.container[1]+=ressource.gazQte
                                ressource.gazQte = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = 20
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                else:
                    self.gatherSpeed-=1
        else:
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                player.ressources[player.MINERAL] += self.container[0]
                player.ressources[player.GAS] += self.container[1]
                self.container[0] = 0
                self.container[1] = 0
                if isinstance(self.flag.initialTarget, w.AstronomicalObject):
                    self.flag.finalTarget = self.flag.initialTarget
                    if self.flag.finalTarget.type == 'asteroid':
                        if self.flag.finalTarget.mineralQte == 0:
                            self.flag.flagState = FlagState.STANDBY
                    else:
                        if self.flag.finalTarget.gazQte == 0:
                            self.flag.flagState = FlagState.STANDBY
                else:
                    self.flag.finalTarget = self.position
                    self.flag.flagState = FlagState.STANDBY
 
