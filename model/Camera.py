from model import *


class Camera():
    def __init__(self, default_pos, galaxy, player, width, height):
        self.default_pos = default_pos
        self.position = default_pos
        self.screenCenter = (width/2, (height/2))
        self.screenWidth = width
        self.screenHeight = height
        self.galaxy = galaxy
        self.player = player
        self.movingDirection = []
        self.recalculate_default()

    def recalculate_default(self):
        if self.default_pos[0] - self.screenCenter[0] < (self.galaxy.width * -1)/2:
            self.position[0] = (self.galaxy.width*-1)/2 + self.screenCenter[0]
        if self.default_pos[0] + self.screenCenter[0] > self.galaxy.width/2:
            self.position[0] = self.galaxy.width/2 - self.screenCenter[0]
        if self.default_pos[1] - self.screenCenter[1] < (self.galaxy.height * -1)/2:
            self.position[1] = (self.galaxy.height * -1)/2 + self.screenCenter[1]
        if self.default_pos[1] + self.screenCenter[1] > self.galaxy.height/2:
            self.position[1] = self.galaxy.height/2 - self.screenCenter[1]
        self.default_pos = [self.position[0], self.position[1]]

    def in_game_area(self, position):
        if self.position[0] - self.screenWidth/2 < position[0] < self.position[0] + self.screenWidth/2:
            if self.position[1] - self.screenHeight/2 < position[1] < self.position[1] + self.screenHeight/2:
                return True
        return False

    def ensure_position_is_in_world(self, position):
        if position[0] > self.galaxy.width/2 - self.screenWidth/2:
            position[0] = self.galaxy.width/2 - self.screenWidth/2
        elif position[0] < self.galaxy.width/2*-1 + self.screenWidth/2:
            position[0] = self.galaxy.width/2*-1 + self.screenWidth/2
        if position[1] > self.galaxy.height/2 - self.screenHeight/2:
            position[1] = self.galaxy.height/2 - self.screenHeight/2
        elif position[1] < self.galaxy.height/2*-1 + self.screenHeight/2:
            position[1] = self.galaxy.height/2*-1 + self.screenHeight/2
        return position

    def ensure_position_is_on_planet(self, position):
        if position[0] > Planet.WIDTH - self.screenWidth/2:
            position[0] = Planet.WIDTH - self.screenWidth/2
        elif position[0] < self.screenWidth/2:
            position[0] = self.screenWidth/2
        if position[1] > Planet.HEIGHT - self.screenHeight/2:
            position[1] = Planet.HEIGHT - self.screenHeight/2
        elif position[1] < self.screenHeight/2:
            position[1] = self.screenHeight/2
        return position

    def calc_distance(self, position):
        delta_x = position[0] - self.position[0]
        delta_y = position[1] - self.position[1]
        return [delta_x + self.screenCenter[0], delta_y + self.screenCenter[1]]

    def calc_point_in_world(self, x, y):
        return [self.position[0] - self.screenCenter[0] + x,
                self.position[1] - self.screenCenter[1] + y,
                0]

    def calc_point_on_map(self, x, y):
        position_x = x/200 * self.galaxy.width - self.galaxy.width/2
        position_y = y/200 * self.galaxy.height - self.galaxy.height/2
        if position_x < 0 - self.galaxy.width/2 + self.screenWidth/2:
            position_x = 0 - self.galaxy.width/2 + self.screenWidth/2
        elif position_x > self.galaxy.width/2-self.screenWidth/2:
            position_x = self.galaxy.width/2-self.screenWidth/2
            
        if position_y < 0-self.galaxy.height/2+self.screenHeight/2:
            position_y = 0-self.galaxy.height/2+self.screenHeight/2
        elif position_y > self.galaxy.height/2-self.screenHeight/2:
            position_y = self.galaxy.height/2-self.screenHeight/2
        return [position_x, position_y]

    def calc_point_on_planet_map(self, x, y):
        position_x = x * self.player.currentPlanet.WIDTH / 200
        position_y = y * self.player.currentPlanet.HEIGHT / 200
        if position_x < 0 + self.screenWidth/2:
            position_x = 0 + self.screenWidth/2
        elif position_x > self.player.currentPlanet.WIDTH - self.screenWidth/2:
            position_x = self.player.currentPlanet.WIDTH - self.screenWidth/2
        if position_y < 0 + self.screenHeight/2:
            position_y = 0 + self.screenHeight/2
        elif position_y > self.player.currentPlanet.HEIGHT - self.screenHeight/2:
            position_y = self.player.currentPlanet.HEIGHT - self.screenHeight/2
        return [position_x, position_y]

    def calc_point_mini_map(self, x, y):
        position_x = x/200 * self.galaxy.width - self.galaxy.width/2
        position_y = y/200 * self.galaxy.height - self.galaxy.height/2
        return [position_x, position_y]

    def is_in_field_of_view(self, position):
        if self.position[0]-self.screenWidth/2-20 < position[0] < self.position[0]+self.screenWidth/2+20:
            if self.position[1]-self.screenHeight/2-20 < position[1] < self.position[1]+self.screenHeight/2+20:
                return True
        return False

    def place_on_landing(self, landing_zone):
        planet = self.player.currentPlanet
        self.position = [landing_zone.position[0], landing_zone.position[1]]
        if self.position[0]-self.screenCenter[0] < 0:
            self.position[0] = 0 + self.screenCenter[0]
        if self.position[0] + self.screenCenter[0] > planet.WIDTH:
            self.position[0] = planet.WIDTH-self.screenCenter[0]
        if self.position[1] - self.screenCenter[1] < 0:
            self.position[1] = 0+self.screenCenter[1]
        if self.position[1] + self.screenCenter[1] > planet.HEIGHT:
            self.position[1] = planet.HEIGHT - self.screenCenter[1]

    def place_over_planet(self):
        if self.position[0]-self.screenCenter[0] < (self.galaxy.width*-1)/2:
            self.position[0] = (self.galaxy.width*-1)/2+self.screenCenter[0]
        if self.position[0]+self.screenCenter[0] > self.galaxy.width/2:
            self.position[0] = self.galaxy.width/2-self.screenCenter[0]
        if self.position[1]-self.screenCenter[1] < (self.galaxy.height*-1)/2:
            self.position[1] = (self.galaxy.height*-1)/2+self.screenCenter[1]
        if self.position[1]+self.screenCenter[1] > self.galaxy.height/2:
            self.position[1] = self.galaxy.height/2-self.screenCenter[1]

    def move(self):
        if not self.player.currentPlanet:
            if 'LEFT' in self.movingDirection:
                if self.position[0] > (self.galaxy.width*-1)/2+self.screenCenter[0]:
                    self.position[0] -= 20
            elif 'RIGHT' in self.movingDirection:
                if self.position[0] < self.galaxy.width/2 - self.screenCenter[0]:
                    self.position[0] += 20
            if 'UP' in self.movingDirection:
                if self.position[1] > (self.galaxy.height*-1)/2 + self.screenCenter[1]:
                    self.position[1] -= 20
            elif 'DOWN' in self.movingDirection:
                if self.position[1] < self.galaxy.height/2 - self.screenCenter[1]:
                    self.position[1] += 20
        else:
            planet = self.player.currentPlanet
            if 'LEFT' in self.movingDirection:
                if self.position[0] > 0 + self.screenCenter[0]:
                    self.position[0] -= 20
                else:
                    self.position[0] = self.screenCenter[0]
            elif 'RIGHT' in self.movingDirection:
                if self.position[0] < planet.WIDTH - self.screenCenter[0]:
                    self.position[0] += 20
                else:
                    self.position[0] = planet.WIDTH - self.screenCenter[0]
            if 'UP' in self.movingDirection:
                if self.position[1] > 0 + self.screenCenter[1]:
                    self.position[1] -= 20
                else:
                    self.position[1] = self.screenCenter[1]
            elif 'DOWN' in self.movingDirection:
                if self.position[1] < planet.HEIGHT - self.screenCenter[1]:
                    self.position[1] += 20
                else:
                    self.position[1] = planet.HEIGHT - self.screenCenter[1]