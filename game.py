import threading
import copy
import time

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

FREE = 0
WALL = 1

class Playfield(object):
    FREE = 0
    WALL = 1

    class PlayfieldError(Exception):
        pass

    def __init__(self, map, width, heigth):
        self.map = map
        self.width = width
        self.heigth = heigth
        self.points = []

    def add_point(self, x, y):
        if not self.is_free(x, y) or self.is_point(x, y):
            raise self.PlayfieldError("Can not add point ({0}, {1})".format(x, y))
        self.points.append((x,y))

    def del_point(self, x, y):
        if self.is_point(x, y):
            self.points.remove((x, y))
        else:
            raise self.PlayfieldError("Can not remove point ({0}, {1})".format(x, y))

    def is_point(self, x, y):
        if not self.is_into(x, y):
            raise self.PlayfieldError("({0}, {1}) is out of field".format(x, y))

        print (x, y)
        print self.points
        return (x, y) in self.points

    def is_free(self, x, y):
        if not self.is_into(x, y):
            return False

        return self.map[y][x] != self.WALL

    def is_into(self, x, y):
        return 0 <= x < self.width and 0 <= y <= self.heigth


class Gameinfo(object):
    def __init__(self, map, points):
        self.map = map
        self.players = {}
        self.points = copy.deepcopy(points)
        self.x = None
        self.y = None

    def add_player_info(self, name, p):
        self.players[name] = (p.x, p.y)

class Player(object):
    def __init__(self, name, move_func, x = 0, y = 0):
        self.name = name
        self.score = 0
        self.move_func = move_func
        self.x = x
        self.y = y

    def move(self, game_info):
        return self.move_func(game_info)



class Game(object):
    #Move

    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


    def __init__(self, playground):
        self.playground = playground
        self.players = {}
        self.lock = threading.Lock()
        self.game_thread = threading.Thread(target=self._game)

    def add_player(self, player):
        self.players[player.name] = player

    def do_player_move(self, player):
        info = Gameinfo(self.playground.map, self.playground.points)
        for name, p in self.players.items():
            info.add_player_info(name, p)
        info.x = player.x
        info.y = player.y

        move = player.move(info)
        x = player.x
        y = player.y

        if move == self.UP:
            y -= 1
        elif move == self.DOWN:
            y += 1
        elif move == self.LEFT:
            x -= 1
        elif move == self.RIGHT :
            x += 1
        else:
            return

        if not self.playground.is_free(x,y) or not self.playground.is_into(x,y):
            return

        self.lock.acquire()
        if self.playground.is_point(x, y):
            self.playground.del_point(x, y)
            player.score =+ 1

        player.x, player.y = x, y
        self.lock.release()

    def do_move(self):
        time.sleep(1)
        for n, p in self.players.items()    :
            self.do_player_move(p)

    def start_game(self):
       self.game_thread.start()

    def _game(self):
        points = len(self.playground.points)

        while True:
            self.do_move()
            if len(self.playground.points) == 0:
                break

    def is_going(self):
        return self.game_thread.is_alive()

    def game_info(self):
        self.lock.acquire()
        info = Gameinfo(self.playground.map, self.playground.points)
        for p_name, p in self.players.items():
            info.add_player_info(p_name, p)
        self.lock.release()
        return info

    def get_players(self):
        self.lock.acquire()
        players = copy.deepcopy(self.players)
        self.lock.release()
        return players