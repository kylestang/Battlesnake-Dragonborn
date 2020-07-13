import json
import os
import bottle

from api import ping_response, start_response, move_response, end_response
from functions import (get_adjacent, find_closest_food, find_weak_head, will_collide, area_size,
    check_area, can_escape, distance_from_wall, near_head, headon_death, headon_kill, wall_trap, log_data)

# Constants
MAX_SEARCH = 26
STARVING_THRESHOLD = 15
SAFE_DISTANCE = 2
OPENING_TURNS = 20
LOGGING = False
LOG_LOCATION = "logs/{}.log"

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

    log_data(LOGGING, LOG_LOCATION.format(data["game"]["id"]), json.dumps(data))

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

    # Data
    # closest_food
    closest_food = find_closest_food(board, you, current_pos, turn, STARVING_THRESHOLD, OPENING_TURNS)

    # closest_weak_snake
    closest_weak_head = find_weak_head(board, you, current_pos)

    # will_collide
    will_collide_down = will_collide(board, down, [])
    will_collide_up = will_collide(board, up, [])
    will_collide_right = will_collide(board, right, [])
    will_collide_left = will_collide(board, left, [])

    # area_size, check_area
    #TODO max_area may be unnecessary
    if will_collide_down:
        down_area = 0
    else:
        max_area = area_size(board, down, [], 1, min(you["length"], MAX_SEARCH))
        down_area = check_area(board, you, down, [], 0, max_area)
        log_data(LOGGING, LOG_LOCATION.format(data["game"]["id"]), "max_down: " + str(max_area) + " down_area: " + str(down_area))

    if will_collide_up:
        up_area = 0
    else:
        max_area = area_size(board, up, [], 1, min(you["length"], MAX_SEARCH))
        up_area = check_area(board, you, up, [], 0, max_area)
        log_data(LOGGING, LOG_LOCATION.format(data["game"]["id"]), "max_up: " + str(max_area) + " up_area: " + str(up_area))
    
    if will_collide_right:
        right_area = 0
    else:
        max_area = min(area_size(board, right, [], 1, you["length"]), MAX_SEARCH)
        right_area = check_area(board, you, right, [], 0, max_area)
        log_data(LOGGING, LOG_LOCATION.format(data["game"]["id"]), "max_right: " + str(max_area) + " right_area: " + str(right_area))
    
    if will_collide_left:
        left_area = 0
    else:
        max_area = min(area_size(board, left, [], 1, you["length"]), MAX_SEARCH)
        left_area = check_area(board, you, left, [], 0, max_area)
        log_data(LOGGING, LOG_LOCATION.format(data["game"]["id"]), "max_left: " + str(max_area) + " left_area: " + str(left_area))
    
    # can_escape
    can_escape_down = can_escape(you, down_area, MAX_SEARCH)
    can_escape_up = can_escape(you, up_area, MAX_SEARCH)
    can_escape_right = can_escape(you, right_area, MAX_SEARCH)
    can_escape_left = can_escape(you, left_area, MAX_SEARCH)

    # against_wall
    against_wall_down = distance_from_wall(board, down, 0)
    against_wall_up = distance_from_wall(board, up, 0)
    against_wall_right = distance_from_wall(board, right, 0)
    against_wall_left = distance_from_wall(board, left, 0)

    # Safe zone
    safe_zone_down = distance_from_wall(board, down, SAFE_DISTANCE)
    safe_zone_up = distance_from_wall(board, up, SAFE_DISTANCE)
    safe_zone_right = distance_from_wall(board, right, SAFE_DISTANCE)
    safe_zone_left = distance_from_wall(board, left, SAFE_DISTANCE)

    # near_head
    near_head_down = near_head(board, you, down)
    near_head_up = near_head(board, you, up)
    near_head_right = near_head(board, you, right)
    near_head_left = near_head(board, you, left)

    # headon_death
    headon_death_down = headon_death(board, you, down)
    headon_death_up = headon_death(board, you, up)
    headon_death_right = headon_death(board, you, right)
    headon_death_left = headon_death(board, you, left)

    # headon_kill
    headon_kill_down = headon_kill(board, you, down)
    headon_kill_up = headon_kill(board, you, up)
    headon_kill_right = headon_kill(board, you, right)
    headon_kill_left = headon_kill(board, you, left)

    # wall_trap
    wall_trap_down = wall_trap(board, you, down)
    wall_trap_up = wall_trap(board, you, up)
    wall_trap_right = wall_trap(board, you, right)
    wall_trap_left = wall_trap(board, you, left)

    # Decision
    # If possible, kill a nearby snake
    if (
        not will_collide_down
        and not near_head_down
        and headon_kill_down
        ):
        direction = "down"
        decision = "1"
    elif (
        not will_collide_up
        and not near_head_up
        and headon_kill_up
        ):
        direction = "up"
        decision = "2"
    elif (
        not will_collide_right
        and not near_head_right
        and headon_kill_right
        ):
        direction = "right"
        decision = "3"
    elif (
        not will_collide_left
        and not near_head_left
        and headon_kill_left
        ):
        direction = "left"
        decision = "4"

    # If safe, trap other snakes against the wall
    elif (
        not will_collide_down
        and can_escape_down
        and not near_head_down
        and wall_trap_down
        ):
        direction = "down"
        decision = "5"
    elif (
        not will_collide_up
        and can_escape_up
        and not near_head_up
        and wall_trap_up
        ):
        direction = "up"
        decision = "6"
    elif (
        not will_collide_right
        and can_escape_right
        and not near_head_right
        and wall_trap_right
        ):
        direction = "right"
        decision = "7"
    elif (
        not will_collide_left
        and can_escape_left
        and not near_head_left
        and wall_trap_left
        ):
        direction = "left"
        decision = "8"

    # Move towards closest food if game opening or starving, checking for collisions, can_escape and near_head
    elif (
        closest_food is not None and closest_food["y"] > current_pos["y"] 
        and (health <= STARVING_THRESHOLD or turn <= OPENING_TURNS)
        and not will_collide_down
        and can_escape_down
        and not near_head_down
        ):
        direction = "down"
        decision = "9"
    elif (
        closest_food is not None and closest_food["y"] < current_pos["y"]
        and (health <= STARVING_THRESHOLD or turn <= OPENING_TURNS)
        and not will_collide_up
        and can_escape_up
        and not near_head_up
        ):
        direction = "up"
        decision = "10"
    elif (
        closest_food is not None and closest_food["x"] > current_pos["x"]
        and (health <= STARVING_THRESHOLD or turn <= OPENING_TURNS)
        and not will_collide_right
        and can_escape_right
        and not near_head_right
        ):
        direction = "right"
        decision = "11"
    elif (
        closest_food is not None and closest_food["x"] < current_pos["x"]
        and (health <= STARVING_THRESHOLD or turn <= OPENING_TURNS)
        and not will_collide_left
        and can_escape_left
        and not near_head_left
        ):
        direction = "left"
        decision = "12"

    # Move towards closest food, avoid walls, checking for collisions, can_escape and near_head
    elif (
        closest_food is not None and closest_food["y"] > current_pos["y"] 
        and not will_collide_down
        and can_escape_down
        and not against_wall_down
        and not near_head_down
        ):
        direction = "down"
        decision = "13"
    elif (
        closest_food is not None and closest_food["y"] < current_pos["y"]
        and not will_collide_up
        and can_escape_up
        and not against_wall_up
        and not near_head_up
        ):
        direction = "up"
        decision = "14"
    elif (
        closest_food is not None and closest_food["x"] > current_pos["x"]
        and not will_collide_right
        and can_escape_right
        and not against_wall_right
        and not near_head_right
        ):
        direction = "right"
        decision = "15"
    elif (
        closest_food is not None and closest_food["x"] < current_pos["x"]
        and not will_collide_left
        and can_escape_left
        and not against_wall_left
        and not near_head_left
        ):
        direction = "left"
        decision = "16"
    
    # Move towards closest snake that I can kill, avoid walls, checking for collisions, can_escape, and near_head
    elif (
        closest_weak_head is not None and closest_weak_head["y"] > current_pos["y"]
        and not will_collide_down
        and can_escape_down
        and not against_wall_down
        and not near_head_down
        ):
        direction = "down"
        decision = "17"
    elif (
        closest_weak_head is not None and closest_weak_head["y"] < current_pos["y"]
        and not will_collide_up
        and can_escape_up
        and not against_wall_up
        and not near_head_up
        ):
        direction = "up"
        decision = "18"
    elif (
        closest_weak_head is not None and closest_weak_head["x"] > current_pos["x"]
        and not will_collide_right
        and can_escape_right
        and not against_wall_right
        and not near_head_right
        ):
        direction = "right"
        decision = "19"
    elif (
        closest_weak_head is not None and closest_weak_head["x"] < current_pos["x"]
        and not will_collide_left
        and can_escape_left
        and not against_wall_left
        and not near_head_left
        ):
        direction = "left"
        decision = "20"
    
    # Circle board in safe zone, avoid walls, checking for collisions, can_escape, and near_head
    elif (
        not will_collide_down
        and can_escape_down
        and not against_wall_down
        and safe_zone_down
        and not near_head_down
        ):
        direction = "down"
        decision = "21"
    elif (
        not will_collide_up
        and can_escape_up
        and not against_wall_up
        and safe_zone_up
        and not near_head_up
        ):
        direction = "up"
        decision = "22"
    elif (
        not will_collide_right
        and can_escape_right
        and not against_wall_right
        and safe_zone_right
        and not near_head_right
        ):
        direction = "right"
        decision = "23"
    elif (
        not will_collide_left
        and can_escape_left
        and not against_wall_left
        and safe_zone_left
        and not near_head_left
        ):
        direction = "left"
        decision = "24"

    # Escape alive, avoid walls, checking for collisions, can_escape, and near_head
    elif (
        not will_collide_down
        and can_escape_down
        and not against_wall_down
        and not near_head_down
        ):
        direction = "down"
        decision = "25"
    elif (
        not will_collide_up
        and can_escape_up
        and not against_wall_up
        and not near_head_up
        ):
        direction = "up"
        decision = "26"
    elif (
        not will_collide_right
        and can_escape_right
        and not against_wall_right
        and not near_head_right
        ):
        direction = "right"
        decision = "27"
    elif (
        not will_collide_left
        and can_escape_left
        and not against_wall_left
        and not near_head_left
        ):
        direction = "left"
        decision = "28"

    # Escape alive, checking for collisions, can_escape, and near_head
    elif (
        not will_collide_down
        and can_escape_down
        and not near_head_down
        ):
        direction = "down"
        decision = "29"
    elif (
        not will_collide_up
        and can_escape_up
        and not near_head_up
        ):
        direction = "up"
        decision = "30"
    elif (
        not will_collide_right
        and can_escape_right
        and not near_head_right
        ):
        direction = "right"
        decision = "31"
    elif (
        not will_collide_left
        and can_escape_left
        and not near_head_left
        ):
        direction = "left"
        decision = "32"

    # Escape alive, checking for collisions, can_escape, and headon_death
    elif (
        not will_collide_down
        and can_escape_down
        and not headon_death_down
        ):
        direction = "down"
        decision = "33"
    elif (
        not will_collide_up
        and can_escape_up
        and not headon_death_up
        ):
        direction = "up"
        decision = "34"
    elif (
        not will_collide_right
        and can_escape_right
        and not headon_death_right
        ):
        direction = "right"
        decision = "35"
    elif (
        not will_collide_left
        and can_escape_left
        and not headon_death_left
        ):
        direction = "left"
        decision = "36"
    
    # Move towards largest area, checking for collisions, and near_head
    elif (
        not will_collide_down
        and down_area == max(down_area, up_area, right_area, left_area)
        and not near_head_down
        ):
        direction = "down"
        decision = "37"
    elif (
        not will_collide_up
        and up_area == max(down_area, up_area, right_area, left_area)
        and not near_head_up
        ):
        direction = "up"
        decision = "38"
    elif (
        not will_collide_right
        and right_area == max(down_area, up_area, right_area, left_area)
        and not near_head_right
        ):
        direction = "right"
        decision = "39"
    elif (
        not will_collide_left
        and left_area == max(down_area, up_area, right_area, left_area)
        and not near_head_left
        ):
        direction = "left"
        decision = "40"
    
    # Move towards largest area, checking for collisions, and headon_death
    elif (
        not will_collide_down
        and down_area == max(down_area, up_area, right_area, left_area)
        and not headon_death_down
        ):
        direction = "down"
        decision = "41"
    elif (
        not will_collide_up
        and up_area == max(down_area, up_area, right_area, left_area)
        and not headon_death_up
        ):
        direction = "up"
        decision = "42"
    elif (
        not will_collide_right
        and right_area == max(down_area, up_area, right_area, left_area)
        and not headon_death_right
        ):
        direction = "right"
        decision = "43"
    elif (
        not will_collide_left
        and left_area == max(down_area, up_area, right_area, left_area)
        and not headon_death_left
        ):
        direction = "left"
        decision = "44"
    
    # Move towards largest area, checking for collisions
    elif (
        not will_collide_down
        and down_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "down"
        decision = "45"
    elif (
        not will_collide_up
        and up_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "up"
        decision = "46"
    elif (
        not will_collide_right
        and right_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "right"
        decision = "47"
    elif (
        not will_collide_left
        and left_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "left"
        decision = "48"

    # Pray, no escape and accept headon
    elif not will_collide_down:
        direction = "down"
        decision = "49"
    elif not will_collide_up:
        direction = "up"
        decision = "50"
    elif not will_collide_right:
        direction = "right"
        decision = "51"
    elif not will_collide_left:
        direction = "left"
        decision = "52"
    
    # Accept death
    else:
        direction = "up"
        decision = "53"
    
    # Log decision for debugging
    log_data(LOGGING, LOG_LOCATION.format(data["game"]["id"]),
        "decision: " + decision + "\npos: " + json.dumps(current_pos) + "\ndir: " + direction
        + "\nfood: " + json.dumps(closest_food) + "\nturn: " + str(data["turn"]) + "\n"
    )
        
    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    log_data(LOGGING, LOG_LOCATION.format(data["game"]["id"]), json.dumps(data))

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
