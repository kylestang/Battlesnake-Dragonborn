import json
import os

import bottle

from api import ping_response, start_response, move_response, end_response

# Global Variables
direction = None

def print_error(code):
    print("Error: " + str(code))

# Returns true if this position will kill the snake
def will_collide(board, pos, gone):
    
    # Check walls
    if  (
        pos.get("x") < 0 
        or pos.get("y") < 0
        or pos.get("x") > board.get("width") - 1
        or pos.get("y") > board.get("height") - 1
        ):
        return True
    
    for tile in gone:
        if(tile == pos):
            return True

    # Check snakes
    for snake in board.get("snakes"):
        for tile in snake.get("body"):
            if tile == pos:
                return True
    
    return False

# Check if snake can escape from tile - throws error 1
def can_escape(board, pos, gone):
    blocked = 0
    available = []
    # Find number of blocked tiles
    down = dict(x=pos.get("x"), y=pos.get("y") + 1)
    up = dict(x=pos.get("x"), y=pos.get("y") - 1)
    right = dict(x=pos.get("x") + 1, y=pos.get("y"))
    left = dict(x=pos.get("x") - 1, y=pos.get("y"))

    if will_collide(board, down, gone): blocked += 1
    else: available.append(down)
    if will_collide(board, up, gone): blocked += 1
    else: available.append(up)
    if will_collide(board, right, gone): blocked += 1
    else: available.append(right)
    if will_collide(board, left, gone): blocked += 1
    else: available.append(left)
    
    gone.append(pos)
    # Check blocked tiles
    if blocked == 1:
        return True

    for tile in available:
        if can_escape(board, tile, gone):
            return True
    
    return False


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

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#050352"
    head_type = "fang"
    tail_type = "curled"

    return start_response(color, head_type, tail_type)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    
    print("Test data start\n")
    the_object = data.get("game").get("id")
    print(the_object)
    print("Test data end\n")

    current_pos = data.get("you").get("body")[0]
    down = dict(x=current_pos.get("x"), y=current_pos.get("y") + 1)
    up = dict(x=current_pos.get("x"), y=current_pos.get("y") - 1)
    right = dict(x=current_pos.get("x") + 1, y=current_pos.get("y"))
    left = dict(x=current_pos.get("x") - 1, y=current_pos.get("y"))

    # Eat food
    # Find closest food
    if len(data.get("board").get("food")) > 0:
        closest_food = None
        closest_distance = None
        for f in data.get("board").get("food"):
            if closest_food == None:
                closest_food = f
                closest_distance = abs(f.get("x") - current_pos.get("x")) + abs(f.get("y") - current_pos.get("y"))

            else:
                distance = abs(f.get("x") - current_pos.get("x")) + abs(f.get("y") - current_pos.get("y"))
                if distance < closest_distance:
                    closest_food = f
                    closest_distance = distance
        
        # Move towards closest food, checking for escapes
        if (
            closest_food.get("y") > current_pos.get("y") 
            and not will_collide(data.get("board"), down, [])
            and can_escape(data.get("board"), down, [])
            ):
            direction = "down"
        elif (
            closest_food.get("y") < current_pos.get("y")
            and not will_collide(data.get("board"), up, [])
            and can_escape(data.get("board"), up, [])
            ):
            direction = "up"
        elif (
            closest_food.get("x") > current_pos.get("x")
            and not will_collide(data.get("board"), right, [])
            and can_escape(data.get("board"), right, [])
            ):
            direction = "right"
        elif (
            closest_food.get("x") < current_pos.get("x")
            and not will_collide(data.get("board"), left, [])
            and can_escape(data.get("board"), left, [])
            ):
            direction = "left"
        # Escape alive
        elif (
            not will_collide(data.get("board"), down, [])
            and can_escape(data.get("board"), down, [])
            ):
            direction = "down"
        elif (
            not will_collide(data.get("board"), up, [])
            and can_escape(data.get("board"), up, [])
            ):
            direction = "up"
        elif (
            not will_collide(data.get("board"), right, [])
            and can_escape(data.get("board"), right, [])
            ):
            direction = "right"
        elif (
            not will_collide(data.get("board"), left, [])
            and can_escape(data.get("board"), left, [])
            ):
            direction = "left"
        # Move towards closest food, checking for collisions, no escape
        elif (
            closest_food.get("y") > current_pos.get("y") 
            and not will_collide(data.get("board"), down, [])
            ):
            direction = "down"
        elif (
            closest_food.get("y") < current_pos.get("y")
            and not will_collide(data.get("board"), up, [])
            ):
            direction = "up"
        elif (
            closest_food.get("x") > current_pos.get("x")
            and not will_collide(data.get("board"), right, [])
            ):
            direction = "right"
        elif (
            closest_food.get("x") < current_pos.get("x")
            and not will_collide(data.get("board"), left, [])
            ):
            direction = "left"
        # pray
        elif not will_collide(data.get("board"), down, []):
            direction = "down"
        elif not will_collide(data.get("board"), up, []):
            direction = "up"
        elif not will_collide(data.get("board"), right, []):
            direction = "right"
        elif not will_collide(data.get("board"), left, []):
            direction = "left"
        # Accept death
        else: direction = "up"
    
    print("pos: " + json.dumps(current_pos) + "\n" + "dir: " + direction)


    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

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
