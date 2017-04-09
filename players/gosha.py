import random

def move(info, ctx=None):
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
