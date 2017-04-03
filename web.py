#!/usr/bin/python

from flask import Flask
import game
from flask import jsonify, redirect, url_for, render_template, request, make_response
import random


app = Flask(__name__)

maze = [
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,1,1,1,1,0,0],
[0,0,0,0,1,0,0,0,0,0],
[0,0,0,0,1,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,1,1,1,1,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0]
]


def f1(map, points, x, y, players, ctx):
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

def f2(map, points, x, y, players, ctx):
    return 0


playground = game.Playground(maze)
playground.points.append((0,3))
playground.points.append((5,4))
playground.points.append((6,6))
pf = game.Game(playground)
p1 = game.Player("Masha", f1, 8, 4)
p2 = game.Player("Gosha", f1, 3, 7)
pf.add_player(p1)
pf.add_player(p2)

@app.route("/v1/api/maze")
def get_maze():
    return jsonify({"maze": pf.playground.map})

@app.route("/v1/api/points")
def get_points():
    gameinfo = pf.game_info()
    res = []
    for x, y in gameinfo.points:
        res.append({"x": x, "y": y})
    return jsonify({"points": res})

@app.route("/v1/api/players")
def get_players():
    players = pf.get_players()
    res = []
    for p_name, p in players    .items():
        res.append({"name": p_name, "x": p.x, "y": p.y, "score": p.score})
    return jsonify({"players": res})

@app.route("/")
def game():
    return render_template("index.html")

if __name__ == '__main__':
    pf.start_game()
    app.run(debug=True, use_reloader=False, host="127.0.0.1")