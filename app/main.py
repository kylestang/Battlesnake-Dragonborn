import json
import os
import bottle

from copy import copy

from api import ping_response, start_response, move_response, end_response

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
        for tile in snake["body"][:-1]:
            if tile == pos:
                return True
    
    # If no collisions, return False
    return False

# Check if snake can escape from tile
def can_escape(board, you, pos, gone):
    # My tail is safe
    if pos == you["body"][-1]:
        return True

    # Store number of blocked tiles and list of available tiles
    blocked = 0
    available = []

   # Find blocked and available tiles
    for tile in getAdjacent(pos):
        if will_collide(board, tile, gone):
            blocked += 1
        else:
            available.append(tile)
    
    # If free, return True
    if blocked == 1:
        return True
    
    # Set current tile to unavailable
    gone.append(pos)

    # Recursively check if there's a route out
    for tile in available:
        if can_escape(board, you, tile, copy(gone)):
            return True
    
    # If there's no route out, return False
    return False

# Find largest area to escape
def checkArea(board, pos, gone):
    if(will_collide(board, pos, gone)):
        return 0

    count = 1
    gone.append(pos)
    for tile in getAdjacent(pos):
        count += checkArea(board, tile, gone)
    
    return count

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
def nearHead(board, you, pos):

    for snake in board["snakes"]:
        if snake != you and len(snake["body"]) >= len(you["body"]):
            for tile in getAdjacent(snake["body"][0]):
                if tile == pos:
                    return True

    return False

# Returns the four tiles adjacent to pos
def getAdjacent(pos):
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
    down, up, right, left = getAdjacent(current_pos)
    
    # Find closest food
    closest_food = None
    if len(board["food"]) > 0:

        for f in board["food"]:
            if closest_food == None:
                closest_food = f
                closest_distance = (abs(f["x"] - current_pos["x"])
                + abs(f["y"] - current_pos["y"]))

            else:
                distance = (abs(f["x"] - current_pos["x"]) 
                + abs(f["y"] - current_pos["y"]))
                
                if distance < closest_distance:
                    closest_food = f
                    closest_distance = distance
    
    area = -1

    # Move towards closest food, checking for collisions, headon, and nearHead
    if (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not nearHead(board, you, down)
        and can_escape(board, you, down, [])
        ):
        direction = "down"
        print(1)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not nearHead(board, you, up)
        and can_escape(board, you, up, [])
        ):
        direction = "up"
        print(2)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not nearHead(board, you, right)
        and can_escape(board, you, right, [])
        ):
        direction = "right"
        print(3)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not nearHead(board, you, left)
        and can_escape(board, you, left, [])
        ):
        direction = "left"
        print(4)
    
    # Escape alive
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not nearHead(board, you, down)
        and can_escape(board, you, down, [])
        ):
        direction = "down"
        print(5)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not nearHead(board, you, up)
        and can_escape(board, you, up, [])
        ):
        direction = "up"
        print(6)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not nearHead(board, you, right)
        and can_escape(board, you, right, [])
        ):
        direction = "right"
        print(7)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not nearHead(board, you, left)
        and can_escape(board, you, left, [])
        ):
        direction = "left"
        print(8)

    # Escape alive, accepting nearHead
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and can_escape(board, you, down, [])
        ):
        direction = "down"
        print(9)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and can_escape(board, you, up, [])
        ):
        direction = "up"
        print(10)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and can_escape(board, you, right, [])
        ):
        direction = "right"
        print(11)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and can_escape(board, you, left, [])
        ):
        direction = "left"
        print(12)
    
    # Move towards largest area, checking for collisions, headon, and nearHead, no escape
    elif (
        not will_collide(board, down, [])
        and not headon_death(board, you, down)
        and not nearHead(board, you, down)
        and checkArea(board, down, []) >= checkArea(board, up, [])
        and checkArea(board, down, []) >= checkArea(board, right, [])
        and checkArea(board, down, []) >= checkArea(board, up, [])
        ):
        direction = "down"
        print(13)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not nearHead(board, you, up)
        and checkArea(board, up, []) >= checkArea(board, down, [])
        and checkArea(board, up, []) >= checkArea(board, right, [])
        and checkArea(board, up, []) >= checkArea(board, left, [])
        ):
        direction = "up"
        print(14)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not nearHead(board, you, right)
        and checkArea(board, right, []) >= checkArea(board, down, [])
        and checkArea(board, right, []) >= checkArea(board, up, [])
        and checkArea(board, right, []) >= checkArea(board, left, [])
        ):
        direction = "right"
        print(15)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not nearHead(board, you, left)
        and checkArea(board, left, []) >= checkArea(board, down, [])
        and checkArea(board, left, []) >= checkArea(board, up, [])
        and checkArea(board, left, []) >= checkArea(board, right, [])
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
        and not nearHead(board, you, down)
        ):
        direction = "down"
        print(21)
    elif (
        not will_collide(board, up, [])
        and not headon_death(board, you, up)
        and not nearHead(board, you, up)
        ):
        direction = "up"
        print(22)
    elif (
        not will_collide(board, right, [])
        and not headon_death(board, you, right)
        and not nearHead(board, you, right)
        ):
        direction = "right"
        print(23)
    elif (
        not will_collide(board, left, [])
        and not headon_death(board, you, left)
        and not nearHead(board, you, left)
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
