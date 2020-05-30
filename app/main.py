import json
import os
import bottle

from .api import ping_response, start_response, move_response, end_response

# Constants
MAX_SEARCH = 25

# Returns location of closest food to current_pos, or None
def find_closest_food(board, current_pos):
    closest_food = None
    if len(board["food"]) > 0:

        # Check each piece of food
        for food in board["food"]:
            if closest_food == None:
                closest_food = food
                closest_distance = (abs(food["x"] - current_pos["x"])
                + abs(food["y"] - current_pos["y"]))

            else:
                distance = (abs(food["x"] - current_pos["x"]) 
                + abs(food["y"] - current_pos["y"]))
                
                if distance < closest_distance:
                    closest_food = food
                    closest_distance = distance
    
    return closest_food

# Returns True if this position will kill the snake
def will_collide(board, pos, gone):
    # Check wall collisions
    if  (
        pos["x"] < 0 
        or pos["y"] < 0
        or pos["x"] > board["width"] - 1
        or pos["y"] > board["height"] - 1
        ):
        return True
    
    # Check tiles eliminated by other functions for collisions
    if pos in gone:
        return True

    # Check snakes for collisions, tail will not collide
    for snake in board["snakes"]:
        if pos in snake["body"][:-1]:
            return True
    
    # If no collisions, return False
    return False

# Check if snake can escape from tile
def can_escape(you, area):
    return area >= len(you["body"]) or area >= MAX_SEARCH

# Find largest area to escape, pos must not be a collision
def check_area(board, you, pos, gone, current_area, max_area):
    if pos == you["body"][-1]:
        return len(you["body"])

    current_area += 1
    
    if current_area < max_area:
        gone.append(pos)
        largest_area = current_area
        for tile in get_adjacent(pos):
            if not will_collide(board, tile, gone):
                new_area = check_area(board, you, tile, gone.copy(), current_area, max_area)
                if new_area >= max_area:
                    return new_area
                if new_area > largest_area:
                    largest_area = new_area
        return largest_area

    return current_area

# Checks size of available area, limited to length of snake
def area_size(board, pos, gone, size, max):
    gone.append(pos)
    for tile in get_adjacent(pos):
        if size < max and not will_collide(board, tile, gone):
            size = area_size(board, tile, gone, size + 1, max)
    return size

# Returns True if about to die from headon collision
def headon_death(board, you, pos):
    # Find snake's predicted path
    for snake in board["snakes"]:
        if snake != you:
            next = {
                "x": 2 * snake["body"][0]["x"] - snake["body"][1]["x"],
                "y": 2 * snake["body"][0]["y"] - snake["body"][1]["y"]
                }

            # Return true if my snake is likely to be killed
            if pos == next and len(snake["body"]) >= len(you["body"]):
                return True
    
    return False

# Returns true if pos is beside the head of a snake that can kill it headon
def near_head(board, you, pos):

    for snake in board["snakes"]:
        if snake != you and len(snake["body"]) >= len(you["body"]):
            if pos in get_adjacent(snake["body"][0]):
                return True

    return False

# Returns the four tiles adjacent to pos
def get_adjacent(pos):
    down = dict(x=pos["x"], y=pos["y"] + 1)
    up = dict(x=pos["x"], y=pos["y"] - 1)
    right = dict(x=pos["x"] + 1, y=pos["y"])
    left = dict(x=pos["x"] - 1, y=pos["y"])

    return down, up, right, left


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
    current_pos = you["body"][0]
    down, up, right, left = get_adjacent(current_pos)
    
    closest_food = find_closest_food(board, current_pos)

    if will_collide(board, down, []):
        down_area = 0
    else:
        max_area = min(area_size(board, down, [], 1, len(you["body"])), MAX_SEARCH)
        down_area = check_area(board, you, down, [], 0, max_area)
    
    if will_collide(board, up, []):
        up_area = 0
    else:
        max_area = min(area_size(board, up, [], 1, len(you["body"])), MAX_SEARCH)
        up_area = check_area(board, you, up, [], 0, max_area)
    
    if will_collide(board, right, []):
        right_area = 0
    else:
        max_area = min(area_size(board, right, [], 1, len(you["body"])), MAX_SEARCH)
        right_area = check_area(board, you, right, [], 0, max_area)
    
    if will_collide(board, left, []):
        left_area = 0
    else:
        max_area = min(area_size(board, left, [], 1, len(you["body"])), MAX_SEARCH)
        left_area = check_area(board, you, left, [], 0, max_area)

    print("Areas: down:", down_area, "up:", up_area, "left:", left_area, "right:", right_area)

    # Move towards closest food, checking for collisions, headon, and nearHead
    if (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and can_escape(you, down_area)
        ):
        direction = "down"
        print(1)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and can_escape(you, up_area)
        ):
        direction = "up"
        print(2)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and can_escape(you, right_area)
        ):
        direction = "right"
        print(3)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and can_escape(you, left_area)
        ):
        direction = "left"
        print(4)
    
    # Escape alive
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and can_escape(you, down_area)
        ):
        direction = "down"
        print(5)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and can_escape(you, up_area)
        ):
        direction = "up"
        print(6)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and can_escape(you, right_area)
        ):
        direction = "right"
        print(7)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and can_escape(you, left_area)
        ):
        direction = "left"
        print(8)

    # Escape alive, accepting nearHead
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and can_escape(you, down_area)
        ):
        direction = "down"
        print(9)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and can_escape(you, up_area)
        ):
        direction = "up"
        print(10)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and can_escape(you, right_area)
        ):
        direction = "right"
        print(11)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and can_escape(you, left_area)
        ):
        direction = "left"
        print(12)
    
    # Move towards largest area, checking for collisions, headon, and nearHead, no escape
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        and down_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "down"
        print(13)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        and up_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "up"
        print(14)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        and right_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "right"
        print(15)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        and left_area == max(down_area, up_area, right_area, left_area)
        ):
        direction = "left"
        print(16)

    # Move towards closest food, checking for collisions and headon, no escape
    elif (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(board, down, [])
        and not headon_death(board, you, down)
        ):
        direction = "down"
        print(17)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        and not headon_death(board, you, up)
        ):
        direction = "up"
        print(18)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        and not headon_death(board, you, right)
        ):
        direction = "right"
        print(19)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        and not headon_death(board, you, left)
        ):
        direction = "left"
        print(20)
    
    # Avoid collision, headon, and nearHead, no escape and no food
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not near_head(board, you, down)
        ):
        direction = "down"
        print(21)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not near_head(board, you, up)
        ):
        direction = "up"
        print(22)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not near_head(board, you, right)
        ):
        direction = "right"
        print(23)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not near_head(board, you, left)
        ):
        direction = "left"
        print(24)
    
    # Avoid collision and headon, no escape
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        ):
        direction = "down"
        print(25)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        ):
        direction = "up"
        print(26)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        ):
        direction = "right"
        print(27)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        ):
        direction = "left"
        print(28)

    # Move towards closest food, checking for collisions, accept headon and no escape
    elif (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(board, down, [])
        ):
        direction = "down"
        print(29)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        ):
        direction = "up"
        print(30)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        ):
        direction = "right"
        print(31)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        ):
        direction = "left"
        print(32)

    # Pray, no escape and accept headon
    elif not will_collide(board, down, []):
        direction = "down"
        print(33)
    elif not will_collide(board, up, []):
        direction = "up"
        print(34)
    elif not will_collide(board, right, []):
        direction = "right"
        print(35)
    elif not will_collide(board, left, []):
        direction = "left"
        print(36)
    
    # Accept death
    else:
        direction = "up"
        print(37)
    
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
