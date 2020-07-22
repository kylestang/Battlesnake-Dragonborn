import json
import os
import bottle

from ctypes import *
from api import ping_response, start_response, move_response, end_response

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

    # Create initial variables
    board = data["board"]
    you = data["you"]
    current_pos = you["head"]
    tail = you["body"][-1]
    health = you["health"]
    turn = data["turn"]
    down, up, right, left = get_adjacent(current_pos)

    
        
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
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
