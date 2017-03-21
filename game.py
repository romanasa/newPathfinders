class Playfield(object):
    FREE = 0
    WALL = 1
    POINT = 2
    def __init__(self, map, width, heigth):
        self.map = map
        self.width = width
        self.heigth = heigth
        self.points = []

    def add_point(self, x, y):
        self.map[x][y] = self.POINT

    def move_to(self, x, y):
        return


class Player(object):
    pass


class Game(object):

    # Game state
    STOPPED = 0
    GOING = 1
    PAUSED = 2
    ENDED = 3

    def start(self):
        pass

    def state(self):
        return self.state

    def step(self):
        pass


