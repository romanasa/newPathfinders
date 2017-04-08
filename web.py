#!/usr/bin/python

from flask import Flask
import game
from flask import jsonify, redirect, url_for, render_template, request, make_response
import random
import time
import signal
import logging


app = Flask(__name__)

maze = [
[0,1,0,0,0,0,0,0,0,0,0],
[0,1,0,0,1,1,1,1,0,0,1],
[0,0,0,0,1,0,0,0,0,0,1],
[0,0,0,0,1,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0,1],
[0,1,0,0,1,1,1,1,0,0,0],
[0,1,0,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0,1]
]


def f1(info, ctx=None):
    map = info["map"]
    x = info["x"]
    y = info["y"]
    height = len(map)
    width = len(map[0])

    def is_into(x, y):
        return 0 <= x < width and 0 <= y < height

    def is_free(x, y):
        if not is_into(x, y):
            return False

        return map[y][x] != 1
    moves = [(0, -1), (0, 1), (-1 , 0), (1, 0)]

    while True:
        move = random.randint(0, 3)
        if is_free(x+moves[move][0], y+moves[move][1]):
            return move

def f2(info):
    map = info["map"]
    x = info["x"]
    y = info["y"]
    height = len(map)
    width = len(map[0])

    def is_into(x, y):
        return 0 <= x < width and 0 <= y < height

    def is_free(x, y):
        if not is_into(x, y):
            return False

        return map[y][x] != 1
    moves = [(0, -1), (0, 1), (-1 , 0), (1, 0)]

    time.sleep(1)
    while True:
        move = random.randint(0, 3)
        if is_free(x+moves[move][0], y+moves[move][1]):
            return move


playground = game.Playground(maze)
playground.points.append((0,3))
playground.points.append((5,4))
playground.points.append((6,6))
pf = game.Game(playground, 1000000, 0.1)
p1 = game.Player("Masha", f1, 8, 4)
p2 = game.Player("Gosha", f1, 3, 7)
p3 = game.Player("XXX", f2, 3, 7)
pf.add_player(p1)
pf.add_player(p2)
pf.add_player(p3)

@app.route("/v1/api/maze")
def get_maze():
    return jsonify({"maze": pf.playground.map})

@app.route("/v1/api/points")
def get_points():
    res = []
    for point in pf.get_points():
        res.append({"x": point[0], "y": point[1]})
    return jsonify({"points": res})

@app.route("/v1/api/players")
def get_players():
    players = pf.get_players()
    res = []
    for p in players:
        res.append({"name": p.name, "x": p.x, "y": p.y, "score": p.score})
    return jsonify({"players": res})

@app.route("/")
def game():
    return render_template("index.html")

def handler(signum, frame):
    pf.stop_game()

if __name__ == '__main__':
    pf.start_game()
    #signal.signal(signal.SIGINT, handler)
    #signal.signal(signal.SIGTERM, handler)
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run(debug=False, use_reloader=False, host="127.0.0.1")
    pf.stop_game()