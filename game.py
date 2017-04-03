import threading
import copy
import time

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

FREE = 0
WALL = 1

# Game state
STOPPED = 0
STARTED = 1
ENDED = 2


class GameError(Exception):
    pass


class PlaygroundError(Exception):
    pass


class Playground(object):
    FREE = 0
    WALL = 1

    class PlaygroundError(Exception):
        pass

    def __init__(self, map):
        if len(map) == 0:
            raise PlaygroundError("Map has not rows")

        for row in map:
            if len(row) != len(map[0]):
                raise PlaygroundError("Rows in map nave not got the same length")

        self.map = map
        self.width = len(map[0])
        self.height = len(map)
        self.points = []

    def add_point(self, x, y):
        if not self.is_free(x, y) or self.is_point(x, y):
            raise self.PlaygroundError("Can not add point ({0}, {1})".format(x, y))
        self.points.append((x,y))

    def del_point(self, x, y):
        if self.is_point(x, y):
            self.points.remove((x, y))
        else:
            raise self.PlaygroundError("Can not remove point ({0}, {1})".format(x, y))

    def is_point(self, x, y):
        if not self.is_into(x, y):
            return False

        return (x, y) in self.points

    def is_free(self, x, y):
        if not self.is_into(x, y):
            return False

        return self.map[y][x] != WALL

    def is_into(self, x, y):
        return 0 <= x < self.width and 0 <= y <= self.height


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
        # Function for move:
        # move_function(map, points, x, y, players, ctx = None)
        self.x = x
        self.y = y

        # Save history of all moves
        self.history = []
        self.history.append((x,y))

    def move(self, map, points, x, y, players, ctx=None):
        return self.move_func(map, points, x, y, players, ctx)


class Game(object):
    def __init__(self, playground):
        self.state = STOPPED
        self.playground = playground
        self.players = {}
        self.lock = threading.Lock()
        self.game_thread = threading.Thread(target=self._game)

    def add_player(self, player):
        if self.state == STOPPED:
            self.players[player.name] = player
        else:
            raise GameError("Can not add player. Game not in STOPPED state")

    def do_player_move(self, player):
        x = player.x
        y = player.y
        map = copy.deepcopy(self.playground.map)
        points = copy.deepcopy(self.playground.points)
        players = [(p.x, p.y) for n, p in self.players.items() if n != player.name]

        move = player.move(map, points, x, y, players)

        if move == UP:
            y -= 1
        elif move == DOWN:
            y += 1
        elif move == LEFT:
            x -= 1
        elif move == RIGHT :
            x += 1
        else:
            return

        self.lock.acquire()
        if self.playground.is_free(x,y):
            if self.playground.is_point(x, y):
                self.playground.del_point(x, y)
                player.score += 1

            player.x, player.y = x, y

        player.history.append((x,y))
        self.lock.release()

    def do_move(self):
        time.sleep(0.1)
        for n, p in self.players.items():
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
