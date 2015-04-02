from model import *
import random


class SolarSystem(object):
    HEIGHT = 400
    WIDTH = 400
    SUN_WIDTH = 64
    SUN_HEIGHT = 64
    MAX_PLANETS = 6
    MAX_ASTRONOMICAL_OBJECTS = 8
    NEBULA = 0
    ASTEROID = 1
    
    def __init__(self, position, sun_id):
        self.sun_id = sun_id
        self.sun_position = position
        self.planets = []
        self.nebulas = []
        self.asteroids = []
        self.discovered = False
        n_planet = int(random.random()*self.MAX_PLANETS)+1
        n_res = int(random.random()*self.MAX_ASTRONOMICAL_OBJECTS)+1
        n_nebu = 0
        n_astero = 0
        for i in range(0, n_res):
            if i % 2 == 1:
                n_nebu += 1
            else:
                n_astero += 1
        for i in range(0, n_planet):
            temp_x = ""
            temp_y = ""
            place_found = False
            while not place_found:
                place_found = True
                temp_x = random.randrange(self.WIDTH/2*-1, self.WIDTH/2)
                temp_y = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)
                if -40 < temp_x < 40:
                    place_found = False
                if -40 < temp_y < 40:
                    place_found = False
                for planet in self.planets:
                    if planet.position[0]-planet.IMAGE_WIDTH < self.sun_position[0]+temp_x < planet.position[0]+planet.IMAGE_WIDTH:
                        if planet.position[1]-planet.IMAGE_HEIGHT < self.sun_position[1]+temp_y < planet.position[1]+planet.IMAGE_HEIGHT:
                            place_found = False
                            break
            self.planets.append(Planet([self.sun_position[0]+temp_x, self.sun_position[1]+temp_y], int(random.random()*3), int(random.random()*3), i, self))
        for i in range(0,n_nebu):
            temp_x = ""
            temp_y = ""
            place_found = False
            while not place_found:
                place_found = True
                temp_x = random.randrange(self.WIDTH/2*-1, self.WIDTH/2)
                temp_y = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)
                if -40 < temp_x < 40:
                    place_found = False
                if -40 < temp_y < 40:
                    place_found = False
                for planet in self.planets:
                    if planet.position[0]-planet.IMAGE_WIDTH < self.sun_position[0]+temp_x < planet.position[0]+planet.IMAGE_WIDTH:
                        if planet.position[1]-planet.IMAGE_HEIGHT < self.sun_position[1]+temp_y < planet.position[1]+planet.IMAGE_HEIGHT:
                            place_found = False
                            break
                for nebula in self.nebulas:
                    if nebula.position[0]-nebula.NEBULA_WIDTH < self.sun_position[0]+temp_x < nebula.position[0]+nebula.NEBULA_WIDTH:
                        if nebula.position[1]-nebula.NEBULA_HEIGHT < self.sun_position[1]+temp_y < nebula.position[1]+nebula.NEBULA_HEIGHT:
                            place_found = False
                            break
            self.nebulas.append(AstronomicalObject(SolarSystem.NEBULA, (self.sun_position[0]+temp_x, self.sun_position[1]+temp_y), i, self))
        for i in range(0, n_astero):
            temp_x = ""
            temp_y = ""
            place_found = False
            while not place_found:
                place_found = True
                temp_x = random.randrange(self.WIDTH/2*-1, self.WIDTH/2)
                temp_y = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)
                if -40 < temp_x < 40:
                    place_found = False
                if -40 < temp_y < 40:
                    place_found = False
                for planet in self.planets:
                    if planet.position[0]-planet.IMAGE_WIDTH < self.sun_position[0]+temp_x < planet.position[0]+planet.IMAGE_WIDTH:
                        if planet.position[1]-planet.IMAGE_HEIGHT < self.sun_position[1]+temp_y < planet.position[1]+planet.IMAGE_HEIGHT:
                            place_found = False
                            break
                for nebula in self.nebulas:
                    if nebula.position[0]-nebula.NEBULA_WIDTH < self.sun_position[0]+temp_x < nebula.position[0]+nebula.NEBULA_WIDTH:
                        if nebula.position[1]-nebula.NEBULA_HEIGHT < self.sun_position[1]+temp_y < nebula.position[1]+nebula.NEBULA_HEIGHT:
                            place_found = False
                            break
                for asteroid in self.asteroids:
                    if asteroid.position[0]-asteroid.ASTEROID_WIDTH < self.sun_position[0]+temp_x < asteroid.position[0]+asteroid.ASTEROID_WIDTH:
                        if asteroid.position[1]-asteroid.ASTEROID_HEIGHT < self.sun_position[1]+temp_y < asteroid.position[1]+asteroid.ASTEROID_HEIGHT:
                            place_found = False
                            break
            self.asteroids.append(AstronomicalObject(SolarSystem.ASTEROID, (self.sun_position[0]+temp_x, self.sun_position[1]+temp_y), i, self))

    def over(self, position_start, position_end):
        if position_end[0] > self.sun_position[0] - self.SUN_WIDTH/2 and position_start[0] < self.sun_position[0] + self.SUN_WIDTH/2:
            if position_end[1] > self.sun_position[1] - self.SUN_HEIGHT/2 and position_start[1] < self.sun_position[1] + self.SUN_HEIGHT/2:
                return True
        for i in self.planets:
            if i.over(position_start, position_end):
                return True
        for i in self.nebulas:
            if i.over_nebula(position_start, position_end):
                return True
        for i in self.asteroids:
            if i.over_asteroid(position_start, position_end):
                return True
        return False

    def select(self, position):
        clicked_obj = None
        for i in self.planets:
            planet = i.select(position)
            if planet and not clicked_obj:
                clicked_obj = planet
        for i in self.nebulas:
            nebula = i.select_nebula(position)
            if nebula and not clicked_obj:
                clicked_obj = nebula
        for i in self.asteroids:
            asteroid = i.select_asteroid(position)
            if asteroid and not clicked_obj:
                clicked_obj = asteroid
        return clicked_obj