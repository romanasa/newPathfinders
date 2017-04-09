#!/usr/bin/python

from flask import Flask
from flask import jsonify, redirect, url_for, render_template, request, make_response
import logging

import game
import loaders


app = Flask(__name__)


# Global game object (quick and dirty)
pf = None

# Global web app config (quick and dirty too)
web_conf = None


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
        res.append({"name": p.name, "x": p.x, "y": p.y, "score": p.score, "timeout": p.timeout})
    return jsonify({"players": res})

@app.route("/v1/api/game")
def get_gameinfo():
    info = pf.get_gameinfo()
    return jsonify({"game": info})

@app.route("/")
def game():
    return render_template("index.html", width=pf.playground.width, height = pf.playground.height, web_conf = web_conf)


if __name__ == '__main__':
    try:
        loader = loaders.GameLoader("config")
        pf = loader.load_game()
        web_conf = loader.load_web_conf()
    except Exception as e:
        print "ERROR: {}".format(e)
        exit(1)    #   log.disabled = True


    pf.start_game()

    # Disable flask logging
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True

    app.run(debug=False, use_reloader=False, host="127.0.0.1")

    pf.stop_game()