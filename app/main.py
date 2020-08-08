import json
import os
import bottle

from ctypes import *
from api import ping_response, start_response, move_response, end_response

decision = CDLL("app/decision.so").decision

class Coordinate(Structure):
    _fields_ = [("x", c_int),
                ("y", c_int)]

class CoordArray(Structure):
    _fields_ = [("size", c_int),
                ("max_size", c_int),
                ("p_elements", POINTER(Coordinate))]

class Battlesnake(Structure):
    _fields_ = [("id", c_int),
                ("health", c_int),
                ("body", CoordArray),
                ("head", Coordinate),
                ("length", c_int)]

class SnakeArray(Structure):
    _fields_ = [("size", c_int),
                ("max_size", c_int),
                ("p_elements", POINTER(Battlesnake))]

class Game(Structure):
    _fields_ = [("timeout", c_int),
                ("p_id", c_char_p)]

class Board(Structure):
    _fields_ = [("height", c_int),
                ("width", c_int),
                ("food", CoordArray),
                ("snakes", SnakeArray)]

def coord_array(array_size, array_max_size, coord_list):
    return CoordArray(
        size = array_size,
        max_size = array_max_size,
        p_elements = (Coordinate * array_max_size)(*[Coordinate(x = pos["x"], y = pos["y"]) for pos in coord_list])
    )

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.com">https://docs.battlesnake.com</a>.
    '''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    color = "#808080"
    head_type = "smile"
    tail_type = "bolt"

    return start_response(color, head_type, tail_type)


@bottle.post('/move')
def move():
    data = bottle.request.json

    # Game
    game = Game(
        timeout = data["game"]["timeout"],
        p_id = bytes(data["game"]["id"], "utf-8")
    )

    # Board
    food_list = data["board"]["food"]
    print("food list: " + str(food_list))
    food_array = coord_array(len(food_list), len(food_list), food_list)
    print(len(food_array.p_elements))

    snake_list = data["board"]["snakes"]    
    snake_elements = (Battlesnake * len(snake_list))(*[Battlesnake(
        id = 0 if snake_list[i]["id"] == data["you"]["id"] else i + 10,
        health = snake_list[i]["health"],
        body = coord_array(len(snake_list[i]["body"]), len(snake_list[i]["body"]), snake_list[i]["body"]),
        head = Coordinate(x = snake_list[i]["head"]["x"], y = snake_list[i]["head"]["y"]),
        length = snake_list[i]["length"]
    ) for i in range(len(snake_list))])

    snake_array = SnakeArray(
        size = len(snake_list),
        max_size = len(snake_list),
        p_elements = snake_elements
    )

    board = Board(
        height = data["board"]["height"],
        width = data["board"]["width"],
        food = food_array,
        snakes = snake_array
    )

    # You
    you_object = data["you"]
    you = Battlesnake(
        id = 0,
        health = you_object["health"],
        body = coord_array(len(you_object["body"]), len(you_object["body"]), you_object["body"]),
        head = Coordinate(x = you_object["head"]["x"], y = you_object["head"]["y"]),
        length = you_object["length"]
    )
    
    # Turn
    turn = data["turn"]

    result = decision(byref(game), byref(board), byref(you), turn)

    if result == 0: direction = "down"
    elif result == 1: direction = "up"
    elif result == 2: direction = "right"
    elif result == 3: direction = "left"
    else:
        print("Python: Error: decision: " + str(result))
        direction = "down"
        
    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    return end_response()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '25567'),
        debug=os.getenv('DEBUG', True)
    )
