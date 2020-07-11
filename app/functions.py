# Returns the four tiles adjacent to pos
def get_adjacent(pos):
    down = {"x" : pos["x"], "y" : pos["y"] + 1}
    up = {"x" : pos["x"], "y" : pos["y"] - 1}
    right = {"x" : pos["x"] + 1, "y" : pos["y"]}
    left = {"x" : pos["x"] - 1, "y" : pos["y"]}

    return down, up, right, left

# Returns location of closest food to current_pos, or None
def find_closest_food(board, you, pos, turn, starving_threshold, opening_turns):
    closest_food = None

    # Check each piece of food
    for food in board["food"]:
        if not distance_from_wall(board, food, 0) or you["health"] <= starving_threshold or turn <= opening_turns:
            if closest_food is None:
                closest_food = food
                closest_distance = (abs(food["x"] - pos["x"])
                + abs(food["y"] - pos["y"]))

            else:
                distance = (abs(food["x"] - pos["x"]) 
                + abs(food["y"] - pos["y"]))
                
                if distance < closest_distance:
                    closest_food = food
                    closest_distance = distance
    
    return closest_food

# Returns the closest head of a snake that I can kill
def find_weak_head(board, you, pos):
    closest_head = None

    for snake in board["snakes"]:
        if snake["length"] < you["length"]:
            head = snake["head"]
            if closest_head is None:
                closest_head = head
                closest_distance = (abs(head["x"] - pos["x"])
                + abs(head["y"] - pos["y"]))

            else:
                distance = (abs(head["x"] - pos["x"]) 
                + abs(head["y"] - pos["y"]))
                
                if distance < closest_distance:
                    closest_head = head
                    closest_distance = distance

    return closest_head

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

# Checks size of available area, limited to max
def area_size(board, pos, gone, size, max):
    for snake in board["snakes"]:
        if pos == snake["body"][-1]:
            return max
    
    gone.append(pos)
    for tile in get_adjacent(pos):
        if size < max and not will_collide(board, tile, gone):
            size = area_size(board, tile, gone, size + 1, max)
    return size

# Find largest area to escape
# TODO test iterating through entire snake for escape
def check_area(board, you, pos, gone, current_area, max_area):
    for snake in board["snakes"]:
        if pos == snake["body"][-1] or (current_area > 1 and pos == snake["body"][-2]):
            return max_area

    if will_collide(board, pos, gone):
        return current_area

    current_area += 1
    
    if current_area < max_area:
        gone.append(pos)
        largest_area = current_area
        for tile in get_adjacent(pos):
                new_area = check_area(board, you, tile, gone.copy(), current_area, max_area)
                if new_area >= max_area:
                    return new_area
                if new_area > largest_area:
                    largest_area = new_area
        return largest_area

    return current_area

# Check if snake can escape from tile
def can_escape(you, area, max_search):
    return area >= you["length"] or area >= max_search

# Returns True if pos is distance from wall
def distance_from_wall(board, pos, distance):
    return (
        ((pos["x"] == distance or pos["x"] == board["width"] - distance - 1)
        and distance <= pos["y"] <= board["height"] - distance - 1)
        or ((pos["y"] == distance or pos["y"] == board["height"] - distance - 1) 
        and distance <= pos["x"] <= board["width"] - distance - 1))

# Returns true if pos is beside the head of a snake that can kill it headon
def near_head(board, you, pos):
    for snake in board["snakes"]:
        if snake["id"] != you["id"] and snake["length"] >= you["length"]:
            if pos in get_adjacent(snake["head"]):
                return True

    return False

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

# Returns true if my snake can kill another snake headon
def headon_kill(board, you, pos):
    for snake in board["snakes"]:
        can_kill = True
        if snake["length"] >= you["length"] or not pos in get_adjacent(snake["head"]):
            can_kill = False
        else:
            for tile in get_adjacent(snake["head"]):
                if not will_collide(board, tile, []) and tile != pos:
                    can_kill = False

        if can_kill:
            return True
    
    return False

# Returns true if my snake can trap another against a wall
def wall_trap(board, you, pos):
    if not distance_from_wall(board, pos, 0) or distance_from_wall(board, you["head"], 0):
        return False
    
    for snake in board["snakes"]:
        if distance_from_wall(board, snake["head"], 0) and snake["id"] != you["id"]:
            for tile in get_adjacent(snake["head"]):
                if tile in you["body"]:
                    return True
    
    return False
