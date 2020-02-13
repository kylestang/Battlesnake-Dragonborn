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
    for tile in gone:
        if(tile == pos):
            return True

    # Check snakes for collisions
    for snake in board["snakes"]:
        for tile in snake["body"]:
            if tile == pos:
                return True
    
    # If no collisions, return False
    return False

# Check if snake can escape from tile
def can_escape(board, pos, gone):

    # Store number of blocked tiles and list of available tiles
    blocked = 0
    available = []

    down = dict(x=pos["x"], y=pos["y"] + 1)
    up = dict(x=pos["x"], y=pos["y"] - 1)
    right = dict(x=pos["x"] + 1, y=pos["y"])
    left = dict(x=pos["x"] - 1, y=pos["y"])

   # Find blocked and available tiles
    if will_collide(board, down, gone): blocked += 1
    else: available.append(down)
    if will_collide(board, up, gone): blocked += 1
    else: available.append(up)
    if will_collide(board, right, gone): blocked += 1
    else: available.append(right)
    if will_collide(board, left, gone): blocked += 1
    else: available.append(left)
    
    # Set current tile to unavailable
    gone.append(pos)

    # If free, return True
    if blocked == 1:
        return True

    # Recursively check if there's a route out
    for tile in available:
        if can_escape(board, tile, copy(gone)):
            return True
    
    # If there's no route out, return False
    return False

# Returns True if about to die from headon collision
def headon_death(board, you, pos):

    for snake in board["snakes"]:
        if snake != you:
            next = {
                "x": 2 * snake["body"][0]["x"] - snake["body"][1]["x"],
                "y": 2 * snake["body"][0]["y"] - snake["body"][1]["y"]
                }

            if pos == next and len(snake["body"]) >= len(you["body"]):
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
    # Create initial variables
    current_pos = data["you"]["body"][0]
    down = dict(x=current_pos["x"], y=current_pos["y"] + 1)
    up = dict(x=current_pos["x"], y=current_pos["y"] - 1)
    right = dict(x=current_pos["x"] + 1, y=current_pos["y"])
    left = dict(x=current_pos["x"] - 1, y=current_pos["y"])

    # Find closest food
    closest_food = None
    if len(data["board"]["food"]) > 0:

        for f in data["board"]["food"]:
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
    
    # Move towards closest food, checking for collisions and headon
    if (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(data["board"], down, [])
        and not headon_death(data["board"], data["you"], down)
        and can_escape(data["board"], down, [])
        ):
        direction = "down"
        print(1)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(data["board"], up, [])
        and not headon_death(data["board"], data["you"], up)
        and can_escape(data["board"], up, [])
        ):
        direction = "up"
        print(2)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(data["board"], right, [])
        and not headon_death(data["board"], data["you"], right)
        and can_escape(data["board"], right, [])
        ):
        direction = "right"
        print(3)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(data["board"], left, [])
        and not headon_death(data["board"], data["you"], left)
        and can_escape(data["board"], left, [])
        ):
        direction = "left"
        print(4)
    
    # Escape alive
    elif (
        not will_collide(data["board"], down, [])
        and not headon_death(data["board"], data["you"], down)
        and can_escape(data["board"], down, [])
        ):
        direction = "down"
        print(5)
    elif (
        not will_collide(data["board"], up, [])
        and not headon_death(data["board"], data["you"], up)
        and can_escape(data["board"], up, [])
        ):
        direction = "up"
        print(6)
    elif (
        not will_collide(data["board"], right, [])
        and not headon_death(data["board"], data["you"], right)
        and can_escape(data["board"], right, [])
        ):
        direction = "right"
        print(7)
    elif (
        not will_collide(data["board"], left, [])
        and not headon_death(data["board"], data["you"], left)
        and can_escape(data["board"], left, [])
        ):
        direction = "left"
        print(8)
    
    # Move towards closest food, checking for collisions and headon, no escape
    elif (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(data["board"], down, [])
        and not headon_death(data["board"], data["you"], down)
        ):
        direction = "down"
        print(9)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(data["board"], up, [])
        and not headon_death(data["board"], data["you"], up)
        ):
        direction = "up"
        print(10)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(data["board"], right, [])
        and not headon_death(data["board"], data["you"], right)
        ):
        direction = "right"
        print(11)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(data["board"], left, [])
        and not headon_death(data["board"], data["you"], left)
        ):
        direction = "left"
        print(12)
    
    # Avoid collision and headon, no escape and no food
    elif (
        not will_collide(data["board"], down, [])
        and not headon_death(data["board"], data["you"], down)
        ):
        direction = "down"
        print(13)
    elif (
        not will_collide(data["board"], up, [])
        and not headon_death(data["board"], data["you"], up)
        ):
        direction = "up"
        print(14)
    elif (
        not will_collide(data["board"], right, [])
        and not headon_death(data["board"], data["you"], right)
        ):
        direction = "right"
        print(15)
    elif (
        not will_collide(data["board"], left, [])
        and not headon_death(data["board"], data["you"], left)
        ):
        direction = "left"
        print(16)

    # Move towards closest food, checking for collisions, accept headon and no escape
    elif (
        closest_food != None
        and closest_food["y"] > current_pos["y"] 
        and not will_collide(data["board"], down, [])
        ):
        direction = "down"
        print(17)
    elif (
        closest_food != None
        and closest_food["y"] < current_pos["y"]
        and not will_collide(data["board"], up, [])
        ):
        direction = "up"
        print(18)
    elif (
        closest_food != None
        and closest_food["x"] > current_pos["x"]
        and not will_collide(data["board"], right, [])
        ):
        direction = "right"
        print(19)
    elif (
        closest_food != None
        and closest_food["x"] < current_pos["x"]
        and not will_collide(data["board"], left, [])
        ):
        direction = "left"
        print(20)

    # Pray, no escape and accept headon
    elif not will_collide(data["board"], down, []):
        direction = "down"
        print(21)
    elif not will_collide(data["board"], up, []):
        direction = "up"
        print(22)
    elif not will_collide(data["board"], right, []):
        direction = "right"
        print(23)
    elif not will_collide(data["board"], left, []):
        direction = "left"
        print(24)
    
    # Accept death
    else:
        direction = "up"
        print(25)
    
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
