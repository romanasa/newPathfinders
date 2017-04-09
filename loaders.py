import os
import ConfigParser
import imp
import random

import game


class LoadError(Exception):
    pass


class GameLoader(object):
    game_section = "pathfinders"
    web_section = "web"

    def __init__(self, configfile):
        self.load_config(configfile)

    def load_config(self, filename):
        c_parser = ConfigParser.ConfigParser()
        c_parser.read([filename])

        if not c_parser.has_section(self.game_section):
            raise LoadError("Config file has not got {} section".format(self.game_section))

        self.maze_file = c_parser.get(self.game_section, "map_file")
        self.maze_file = os.path.abspath(self.maze_file)
        self.move_timeout = c_parser.getfloat(self.game_section, "move_timeout")
        self.players_dir = c_parser.get(self.game_section, "players_dir")
        self.players_dir = os.path.abspath(self.players_dir)
        self.num_coins = c_parser.getint(self.game_section, "num_coins")
        self.max_moves = c_parser.getint(self.game_section, "max_moves")

        if not c_parser.has_section(self.web_section):
            raise LoadError("Config file has not got '{}' section".format(self.game_section))

        self.field_size = c_parser.getint(self.web_section, "field_size")

    def load_maze(self):
        maze = []
        with open(self.maze_file) as f:
            for line in f:
                row = []
                for point in line:
                    if point == "#":
                        row.append(1)
                    elif point == '.':
                        row.append(0)
                maze.append(row)

        return maze

    def generate_points(self, playground):
        num = self.num_coins
        while num > 0:
            try:
                x = random.randint(0, playground.width-1)
                y = random.randint(0, playground.height-1)
                playground.add_point(x, y)
            except game.PlaygroundError:
                continue
            num -= 1
        return playground

    def load_playground(self):
        maze = self.load_maze()
        pg = game.Playground(maze)
        return self.generate_points(pg)

    @staticmethod
    def load_player(filename):
        name = os.path.basename(filename)[:-3]
        players_dir = os.path.dirname(filename)
        try:
            fp, pathname, description = imp.find_module(name, [players_dir])
            p = imp.load_module(name, fp, pathname, description)
            move_function = p.move  # Get module classes from imported modules
        except Exception as e:
            raise LoadError("Error loading player '{}': {}".format(name, e))

        return game.Player(name, move_function)

    def load_game(self):
        pg = self.load_playground()
        pf_game = game.Game(pg, self.max_moves, self.move_timeout)

        for p_file in os.listdir(self.players_dir):
            if p_file[-3:] != ".py":
                continue
            player = self.load_player(os.path.join(self.players_dir, p_file))

            while True:
                x = random.randint(0, pg.width-1)
                y = random.randint(0, pg.height-1)
                if pg.is_free(x, y):
                    player.set_position(x, y)
                    break

            pf_game.add_player(player)

        return pf_game

    def load_web_conf(self):
        maze = self.load_maze()
        width = len(maze[0])
        height = len(maze)

        conf = {
            "field": self.field_size,
            "tot_width": (width+1) * self.field_size,
            "tot_height": (height +1) * self.field_size
        }

        return conf