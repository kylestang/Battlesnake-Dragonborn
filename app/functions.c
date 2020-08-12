#include <stdbool.h>
#include <stdlib.h>
#include "functions.h"

// Stores an array of adjacent tiles in order down, up, right, left
void get_adjacent(Coordinate pos, CoordArray *adjacent){
    adjacent->p_elements[0] = coordinate(pos.x, pos.y + 1);
    adjacent->p_elements[1] = coordinate(pos.x, pos.y - 1);
    adjacent->p_elements[2] = coordinate(pos.x + 1, pos.y);
    adjacent->p_elements[3] = coordinate(pos.x - 1, pos.y);

    adjacent->size = 4;
    adjacent->max_size = 4;
}

// Returns an array of size 1 containing the closest food, if it exists
CoordArray find_closest_food(Game *game, Board *board, Battlesnake *you, Coordinate pos, int turn, int starving_threshold, int opening_turns, Coordinate* closest_food_pointer){
    Coordinate food;
    CoordArray closest_food = coord_array(1, closest_food_pointer);
    int distance, closest_distance;

    for(int i = 0; i < board->food.size; i++){
        food = board->food.p_elements[i];

        if((!distance_from_wall(board, food, 0) || you->health <= starving_threshold || turn <= opening_turns) && !contains_coord(board->hazards, food)){
            distance = abs(food.x - pos.x) + abs(food.y - pos.y);
            if(closest_food.size == 0){
                append_coord(&closest_food, food, game->p_id);
                closest_distance = distance;
            } else if(distance < closest_distance){
                closest_food.p_elements[0] = food;
                closest_distance = distance;
            }
        }
    }
    return closest_food;
}

// Returns an array of size 1 containing the closest weak head, if it exists
CoordArray find_weak_head(Game *game, Board *board, Battlesnake *you, Coordinate pos, Coordinate* closest_head_pointer){
    Battlesnake snake;
    Coordinate head;
    int distance, closest_distance;
    CoordArray closest_head = coord_array(1, closest_head_pointer);

    for(int i = 0; i < board->snakes.size; i++){
        snake = board->snakes.p_elements[i];

        if(snake.length < you->length && !contains_coord(board->hazards, snake.head)){
            head = snake.head;
            distance = abs(head.x - pos.x) + abs(head.y - pos.y);
            if(closest_head.size == 0){
                append_coord(&closest_head, head, game->p_id);
                closest_distance = distance;
            } else if(distance < closest_distance){
                closest_head.p_elements[0] = head;
                closest_distance = distance;
            }
        }
    }
    return closest_head;
}

// Returns true if snake will collide in pos
bool will_collide(Board *board, Coordinate pos, CoordArray gone){
    Battlesnake snake;
    Coordinate tile;

    if(
        pos.x < 0
        || pos.y < 0
        || pos.x > board->width - 1
        || pos.y > board->height - 1
    ){
        return true;
    }

    if(contains_coord(gone, pos)){
        return true;
    }

    for(int i = 0; i < board->snakes.size; i++){
        snake = board->snakes.p_elements[i];
        for(int j = 0; j < snake.body.size - 1; j++){
            tile = snake.body.p_elements[j];
            if(equals_coord(pos, tile)){
                return true;
            }
        }
    }
    return false;
}

// Returns the longest path a snake can take, limited to max_area
int check_area(Game *game, Board *board, Battlesnake *you, Coordinate pos, CoordArray gone, int current_area, int food_count, int max_area){
    Battlesnake snake;
    int largest_area, new_area;
    CoordArray adjacent;
    Coordinate adjacent_pointer[4];
    adjacent.p_elements = adjacent_pointer;
    Coordinate tile;

    if(contains_coord(board->food, pos)){
        food_count++;
    }

    for(int i = 0; i < board->snakes.size; i++){
        snake = board->snakes.p_elements[i];
        for(int j = 0; j <= max_area; j++){
            if(
                ((snake.id == you->id && current_area - food_count >= j)
                || (snake.id != you->id && current_area >= j))
                && equals_coord(pos, snake.body.p_elements[snake.length - j - 1])
            ){
                return max_area;
            }
        }
    }

    if(will_collide(board, pos, gone)){
        return current_area;
    }

    current_area++;

    if(current_area < max_area){
        append_coord(&gone, pos, game->p_id);
        largest_area = current_area;
        get_adjacent(pos, &adjacent);
        for(int i = 0; i < adjacent.size; i++){
            tile = adjacent.p_elements[i];
            new_area = check_area(game, board, you, tile, gone, current_area, food_count, max_area);
            if(new_area >= max_area){
                return max_area;
            }
            if(new_area > largest_area){
                largest_area = new_area;
            }
        }
        return largest_area;
    }
    return current_area;
}

// Returns true if you can escape from area
bool can_escape(Battlesnake *you, int area, int max_search){
    return area >= you->length || area >= max_search;
}

// Returns true if pos is exactly distance from a wall
bool distance_from_wall(Board *board, Coordinate pos, int distance){
    return
        ((pos.x == distance || pos.x == board->width - distance - 1)
        && distance <= pos.y && pos.y <= board->height - distance - 1)
        || ((pos.y == distance || pos.y == board->height - distance - 1)
        && distance <= pos.x && pos.x <= board->width - distance - 1);
}

// Returns true if pos is beside the head of another snake
bool near_head(Board *board, Battlesnake *you, Coordinate pos){
    Battlesnake snake;
    CoordArray adjacent;
    Coordinate adjacent_pointer[4];
    adjacent.p_elements = adjacent_pointer;

    for(int i = 0; i < board->snakes.size; i++){
        snake = board->snakes.p_elements[i];
        if(snake.id != you->id && snake.length >= you->length){
            get_adjacent(snake.head, &adjacent);
            if(contains_coord(adjacent, pos)){
                return true;
            }
        }
    }
    return false;
}

// Returns true if a snake is likely to move into pos
bool headon_death(Board *board, Battlesnake *you, Coordinate pos){
    Battlesnake snake;
    Coordinate next;

    for(int i = 0; i < board->snakes.size; i++){
        snake = board->snakes.p_elements[i];
        if(snake.id != you->id && snake.length >= you->length){
            next.x = 2 * snake.head.x - snake.body.p_elements[1].x;
            next.y = 2 * snake.head.y - snake.body.p_elements[1].y;
            if(equals_coord(pos, next)){
                return true;
            }
        }
    }
    return false;
}

// Returns true if you can kill another snake headon
bool headon_kill(Board *board, Battlesnake *you, Coordinate pos){
    Battlesnake snake;
    bool can_kill;
    CoordArray adjacent;
    Coordinate adjacent_pointer[4];
    adjacent.p_elements = adjacent_pointer;
    Coordinate tile;
    Coordinate *null_coord;

    for(int i = 0; i < board->snakes.size; i++){
        snake = board->snakes.p_elements[i];
        can_kill = true;

        get_adjacent(snake.head, &adjacent);
        if(snake.length >= you->length || !contains_coord(adjacent, pos)){
            can_kill = false;
        } else{
            for(int j = 0; j < adjacent.size; j++){
                tile = adjacent.p_elements[j];
                if(!will_collide(board, tile, coord_array(0, null_coord))){
                    can_kill = false;
                }
            }
        }
        if(can_kill){
            return true;
        }
    }
    return false;
}

// Returns true if you can trap another snake against the wall
bool wall_trap(Board *board, Battlesnake *you, Coordinate pos){
    Battlesnake snake;
    CoordArray adjacent;
    Coordinate adjacent_pointer[4];
    adjacent.p_elements = adjacent_pointer;
    Coordinate tile;

    if(!distance_from_wall(board, pos, 0) || distance_from_wall(board, you->head, 0)){
        return false;
    }

    for(int i = 0; i < board->snakes.size; i++){
        snake = board->snakes.p_elements[i];
        if(distance_from_wall(board, snake.head, 0) && snake.id != you->id){
            get_adjacent(snake.head, &adjacent);
            for(int j = 0; j < adjacent.size; j++){
                tile = adjacent.p_elements[j];
                if(contains_coord(you->body, tile)){
                    return true;
                }
            }
        }
    }
    return false;
}

// Returns max of a, b, c, d
int max(int a, int b, int c, int d){
    int largest = a > b ? a : b;
    largest = largest > c ? largest : c;
    largest = largest > d ? largest : d;
    return largest;
}
