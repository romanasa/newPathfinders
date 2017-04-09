import threading
import copy
import time

import multiprocessing as mp

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

FREE = 0
WALL = 1

# Game state
STOPPED = 0
STARTED = 1
GAMEOVER = 2


class GameError(Exception):
    pass


class PlaygroundError(Exception):
    pass


class Playground(object):
    FREE = 0
    WALL = 1

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
            raise PlaygroundError("Can not add point ({0}, {1})".format(x, y))
        self.points.append((x, y))

    def del_point(self, x, y):
        if self.is_point(x, y):
            self.points.remove((x, y))
        else:
            raise PlaygroundError("Can not remove point ({0}, {1})".format(x, y))

    def is_point(self, x, y):
        if not self.is_into(x, y):
            return False

        return (x, y) in self.points

    def is_free(self, x, y):
        if not self.is_into(x, y):
            return False

        return self.map[y][x] != WALL

    def is_into(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height


class PlayerInfo(object):
    def __init__(self, player):
        self.name = player.name
        self.score = player.score
        self.x = player.x
        self.y = player.y
        self.timeout = player.timeout


class Player(object):
    def __init__(self, name, move_func, x=0, y=0):
        self.name = name
        self.score = 0
        self.timeout = 0
        self.move_func = move_func
        # Function for move:
        # move_function(info, ctx = None)
        self.x = x
        self.y = y

        # Save history of all moves
        self.history = []
        self.history.append((x, y))

        self.game_pipe, self.player_pipe = mp.Pipe()
        self.process = None

        # Are there any pending move requests
        self.move_in_progress = False

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)

    def start_player(self):
        self.process = mp.Process(target=self.move_processor)
        self.process.start()

    def stop_player(self, timeout=5):
        if self.process and self.process.is_alive():
            # Try to terminate process normally
            self.game_pipe.send(None)
            self.process.join(timeout)

            # Send SIGTERM to the process
            if self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout)

    def move_processor(self):
        print "Process '{}' started".format(self.name)
        self.ctx = {}
        while True:
            try:
                request = self.player_pipe.recv()
            except Exception as e:
                print "ERROR. Process '{}' on pipe receive. {}.".format(self.name, e)
                break

            if request is None:
                break

            try:
                response = self.move_func(request, self.ctx)
            except Exception as e:
                print "ERROR. Process '{}' on move function. {}.".format(self.name, e)
                break

            try:
                self.player_pipe.send(response)
            except Exception as e:
                print "ERROR. Process '{}' on pipe send. {}.".format(self.name, e)
                break

        print "Process {} stopped".format(self.name)

    def move_request(self, gameinfo):
        if self.move_in_progress:
            self.timeout += 1
            return

        self.game_pipe.send(gameinfo)
        self.move_in_progress = True

    def move_result(self):
        if self.move_in_progress:
            if self.game_pipe.poll():
                self.move_in_progress = False
                return self.game_pipe.recv()

        return None


class Game(object):
    def __init__(self, playground, max_move, movetime=1):
        self.state = STOPPED
        self.playground = playground
        self.movetime = movetime
        self.max_move = max_move
        self.n_move = 0
        self.players = {}
        self.lock = threading.Lock()
        self.game_thread = threading.Thread(target=self._game)
        self.stop = False

    def add_player(self, player):
        if self.state == STOPPED:
            self.players[player.name] = player
        else:
            raise GameError("Can not add player. Game not in STOPPED state")

    def do_player_move(self, player, move):
        x, y = player.get_position()

        if move == UP:
            y -= 1
        elif move == DOWN:
            y += 1
        elif move == LEFT:
            x -= 1
        elif move == RIGHT:
            x += 1
        else:
            return

        self.lock.acquire()
        if self.playground.is_free(x, y):
            player.set_position(x, y)
            if self.playground.is_point(x, y):
                self.playground.del_point(x, y)
                player.score += 1

        player.history.append((x, y))
        self.lock.release()

    def do_move(self):
        self.n_move += 1

        for player in self.players.values():
            info = self.player_info(player.name)
            player.move_request(info)

        time.sleep(self.movetime)

        for player in self.players.values():
            move = player.move_result()
            if move is not None:
                self.do_player_move(player, move)

    def start_game(self):
        for player in self.players.values():
            player.start_player()
        self.game_thread.start()
        self.state = STARTED

    def stop_game(self):
        # Stop game thread
        self.stop = True
        self.game_thread.join()

        # Stop all players
        for player in self.players.values():
            player.stop_player()

    def _game(self):
        while True:
            self.do_move()
            if self.is_gameover():
                self.state = GAMEOVER
                break

    def is_gameover(self):
        if len(self.playground.points) == 0 or self.n_move >= self.max_move or self.stop:
            return True
        return False

    def is_going(self):
        return self.game_thread.is_alive()

    def player_info(self, player_name):
        info = dict()
        info["map"] = copy.deepcopy(self.playground.map)
        info["coins"] = copy.deepcopy(self.playground.points)
        info["players"] = [(p.x, p.y) for p in self.players.values() if p.name != player_name]
        info["x"] = self.players[player_name].x
        info["y"] = self.players[player_name].y
        return info

    def get_points(self):
        self.lock.acquire()
        points = copy.deepcopy(self.playground.points)
        self.lock.release()
        return points

    def get_players(self):
        self.lock.acquire()
        players = [PlayerInfo(p) for p in self.players.values()]
        self.lock.release()
        return players

    def get_gameinfo(self):
        info = {
            "move": self.n_move,
            "max_move": self.max_move
        }
        return info