import json
import os
import bottle

from .api import ping_response, start_response, move_response, end_response
from .functions import find_closest_food, will_collide, can_escape, check_area, area_size, headon_death, near_head, get_adjacent, against_wall, wall_trap

# Constants
MAX_SEARCH = 26
STARVING_THRESHOLD = 15


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

    print(json.dumps(data))

    color = "#050352"
    head_type = "fang"
    tail_type = "curled"

    return start_response(color, head_type, tail_type)


@bottle.post('/move')
def move():
    data = bottle.request.json

    # Create initial variables
    board = data["board"]
    you = data["you"]
    current_pos = you["head"]
    down, up, right, left = get_adjacent(current_pos)
    
    closest_food = find_closest_food(board, current_pos, you["health"], STARVING_THRESHOLD)

    if will_collide(board, down, []):
        down_area = 0
    else:
        max_area = min(area_size(board, down, [], 1, you["length"]), MAX_SEARCH)
        down_area = check_area(board, you, down, [], 0, max_area)
    
    if will_collide(board, up, []):
        up_area = 0
    else:
        max_area = min(area_size(board, up, [], 1, you["length"]), MAX_SEARCH)
        up_area = check_area(board, you, up, [], 0, max_area)
    
    if will_collide(board, right, []):
        right_area = 0
    else:
        max_area = min(area_size(board, right, [], 1, you["length"]), MAX_SEARCH)
        right_area = check_area(board, you, right, [], 0, max_area)
    
    if will_collide(board, left, []):
        left_area = 0
    else:
        max_area = min(area_size(board, left, [], 1, you["length"]), MAX_SEARCH)
        left_area = check_area(board, you, left, [], 0, max_area)

    print("Areas: down:", down_area, "up:", up_area, "left:", left_area, "right:", right_area)

    # If safe, trap other snakes against the wall
    if (
        not will_collide(board, down, [])
        and wall_trap(board, you, down)
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and can_escape(you, down_area, MAX_SEARCH)
        ):
        direction = "down"
        print(1)
    elif (
        not will_collide(board, up, [])
        and wall_trap(board, you, up)
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and can_escape(you, up_area, MAX_SEARCH)
        ):
        direction = "up"
        print(2)
    elif (
        not will_collide(board, right, [])
        and wall_trap(board, you, right)
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and can_escape(you, right_area, MAX_SEARCH)
        ):
        direction = "right"
        print(3)
    elif (
        not will_collide(board, left, [])
        and wall_trap(board, you, left)
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and can_escape(you, left_area, MAX_SEARCH)
        ):
        direction = "left"
        print(4)

    # Move towards closest food, checking for collisions, headon, and nearHead
    elif (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and can_escape(you, down_area, MAX_SEARCH)
        ):
        direction = "down"
        print(5)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and can_escape(you, up_area, MAX_SEARCH)
        ):
        direction = "up"
        print(6)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and can_escape(you, right_area, MAX_SEARCH)
        ):
        direction = "right"
        print(7)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and can_escape(you, left_area, MAX_SEARCH)
        ):
        direction = "left"
        print(8)
    
    # Escape alive, not walls
    elif (
        not will_collide(board, down, [])
        and not against_wall(board, down)
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and can_escape(you, down_area, MAX_SEARCH)
        ):
        direction = "down"
        print(9)
    elif (
        not will_collide(board, up, [])
        and not against_wall(board, up)
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and can_escape(you, up_area, MAX_SEARCH)
        ):
        direction = "up"
        print(10)
    elif (
        not will_collide(board, right, [])
        and not against_wall(board, right)
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and can_escape(you, right_area, MAX_SEARCH)
        ):
        direction = "right"
        print(11)
    elif (
        not will_collide(board, left, [])
        and not against_wall(board, left)
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and can_escape(you, left_area, MAX_SEARCH)
        ):
        direction = "left"
        print(12)

    # Escape alive, allowing walls
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and can_escape(you, down_area, MAX_SEARCH)
        ):
        direction = "down"
        print(13)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and can_escape(you, up_area, MAX_SEARCH)
        ):
        direction = "up"
        print(14)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and can_escape(you, right_area, MAX_SEARCH)
        ):
        direction = "right"
        print(15)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and can_escape(you, left_area, MAX_SEARCH)
        ):
        direction = "left"
        print(16)

    # Escape alive, accepting nearHead
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and can_escape(you, down_area, MAX_SEARCH)
        ):
        direction = "down"
        print(17)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and can_escape(you, up_area, MAX_SEARCH)
        ):
        direction = "up"
        print(18)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and can_escape(you, right_area, MAX_SEARCH)
        ):
        direction = "right"
        print(19)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and can_escape(you, left_area, MAX_SEARCH)
        ):
        direction = "left"
        print(20)
    
    # Move towards largest area, checking for collisions, headon, and nearHead, no escape
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and down_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "down"
        print(21)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and up_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "up"
        print(22)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and right_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "right"
        print(23)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and left_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "left"
        print(24)

    # Move towards closest food, checking for collisions and headon, no escape
    elif (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(board, down, [])
        and not headon_death(board, you, down)
        ):
        direction = "down"
        print(25)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        and not headon_death(board, you, up)
        ):
        direction = "up"
        print(26)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        and not headon_death(board, you, right)
        ):
        direction = "right"
        print(27)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        and not headon_death(board, you, left)
        ):
        direction = "left"
        print(28)
    
    # Avoid collision, headon, and nearHead, no escape and no food
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        ):
        direction = "down"
        print(29)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        ):
        direction = "up"
        print(30)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        ):
        direction = "right"
        print(31)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        ):
        direction = "left"
        print(32)
    
    # Avoid collision and headon, no escape
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        ):
        direction = "down"
        print(33)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        ):
        direction = "up"
        print(34)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        ):
        direction = "right"
        print(35)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        ):
        direction = "left"
        print(36)

    # Move towards closest food, checking for collisions, accept headon and no escape
    elif (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(board, down, [])
        ):
        direction = "down"
        print(37)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        ):
        direction = "up"
        print(38)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        ):
        direction = "right"
        print(39)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        ):
        direction = "left"
        print(40)

    # Pray, no escape and accept headon
    elif not will_collide(board, down, []):
        direction = "down"
        print(41)
    elif not will_collide(board, up, []):
        direction = "up"
        print(42)
    elif not will_collide(board, right, []):
        direction = "right"
        print(43)
    elif not will_collide(board, left, []):
        direction = "left"
        print(44)
    
    # Accept death
    else:
        direction = "up"
        print(45)
    
    # Print to help debug
    print("pos: " + json.dumps(current_pos) + "\n" + "dir: " + direction
    + "\n" + "food: " + json.dumps(closest_food) + "\n" + "turn: " + str(data["turn"]))

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
