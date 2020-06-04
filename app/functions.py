# Returns location of closest food to current_pos, or None
def find_closest_food(board, current_pos, health, starving_threshold):
    closest_food = None
    if len(board["food"]) > 0:

        # Check each piece of food
        for food in board["food"]:
            if not against_wall(board, food) or health <= starving_threshold:
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
def can_escape(you, area, max_search):
    return area >= you["length"] or area >= max_search

# Find largest area to escape, pos must not be a collision
def check_area(board, you, pos, gone, current_area, max_area):
    for snake in board["snakes"]:
        if pos == snake["body"][-1]:
            return you["length"]

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
        if snake["id"] != you["id"]:
            next = {
                "x": 2 * snake["head"]["x"] - snake["body"][1]["x"],
                "y": 2 * snake["head"]["y"] - snake["body"][1]["y"]
                }

            # Return true if my snake is likely to be killed
            if pos == next and snake["length"] >= you["length"]:
                return True
    
    return False

# Returns true if pos is beside the head of a snake that can kill it headon
def near_head(board, you, pos):
    for snake in board["snakes"]:
        if snake["id"] != you["id"] and snake["length"] >= you["length"]:
            if pos in get_adjacent(snake["head"]):
                return True

    return False

# Returns the four tiles adjacent to pos
def get_adjacent(pos):
    down = dict(x=pos["x"], y=pos["y"] + 1)
    up = dict(x=pos["x"], y=pos["y"] - 1)
    right = dict(x=pos["x"] + 1, y=pos["y"])
    left = dict(x=pos["x"] - 1, y=pos["y"])

    return down, up, right, left

# Returns True if pos is not beside a wall
def against_wall(board, pos):
    return pos["x"] == 0 or pos["x"] == board["width"] - 1 or pos["y"] == 0 or pos["y"] == board["height"] - 1

# Returns true if my snake can trap another against a wall
def wall_trap(board, you, pos):
    if not against_wall(board, pos) or against_wall(board, you["head"]):
        return False
    
    for snake in board["snakes"]:
        if against_wall(board, snake["head"]) and snake["id"] != you["id"]:
            for tile in get_adjacent(snake["head"]):
                if tile in you["body"]:
                    return True
    
    return False

# Returns true if my snake will be able to kill another snake headon
def can_kill_headon(board, you, pos):
    for snake in board["snakes"]:
        if you["length"] > snake["length"]:
            for tile in get_adjacent(snake["head"]):
                if tile != pos and not will_collide(board, tile, []):
                    return False
    
    return True
