import threading
import copy

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

        return self.points.index((x, y)) != -1

    def is_free(self, x, y):
        if not self.is_into(x, y):
            raise self.PlayfieldError("({0}, {1}) is out of field".format(x, y))

        return self.map[x][y] != self.WALL

    def is_into(self, x, y):
        return 0 <= x < self.width and 0 <= y <= self.heigth


class Gameinfo(object):
    def __init__(self, map, points):
        self.map = map
        self.players = []
        self.points = copy.deepcopy(points)

    def add_player_info(self, p):
        self.players.append((p.x, p.y))


class Player(object):
    def __init__(self, name, move_func):
        self.name = name
        self.score = 0
        self.move_func = move_func
        self.x = 0
        self.y = 0

    def move(self, game_info):
        return self.move_func(game_info)


class Game(object):
    #Move

    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


    def __init__(self, playground, queue=None):
        self.playground = playground
        self.players = {}
        self.queue = queue
        self.game_thread = threading.Thread(target=self._game())
        self.lock = threading.Lock()

    def add_player(self, player):
        self.players[player.name] = player

    def do_player_move(self, player):
        info = Gameinfo(self.playground.map, self.playground.points)
        for p in self.players.values():
            info.add_player_info(p)

        move = player.move(info)
        x = player.x
        y = player.y

        if move == self.UP:
            y =- 1
        elif move == self.DOWN:
            y =+ 1
        elif move == self.LEFT:
            x =- 1
        elif move == self.DOWN:
            x =+ 1
        else:
            return

        if not self.playground.is_free(x,y) or not self.playground.is_into(x,y):
            return

        self.lock.acqure()
        if self.playground.is_point(x, y):
            self.playground.del_point(x, y)
            player.score =+ 1

        player.x, player.y = x, y
        self.lock.release()

    def do_move(self):
        for n, p in self.players:
            self.do_player_move(p)

    def start_game(self):
        self.game_thread.start()

    def _game(self):
        points = self.playground.num_points

        while True:
            self.do_move()
            if self.playground.num_points == 0:
                break

    def is_going(self):
        return self.game_thread.is_alive()

    def game_info(self):
        self.lock.acqure()
        info = Gameinfo(self.playground.map, self.playground.points)
        for p in self.players.values():
            info.add_player_info(p)
        self.lock.release()
        return info