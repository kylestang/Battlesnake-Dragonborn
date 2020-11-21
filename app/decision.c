#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include "functions.h"
#include "constants.h"

// Takes data and returns direction
int decision(Game *game, Board *board, Battlesnake *you, int turn){
    // Null variables
    Coordinate *null_coord;

    // Initial variables
    Coordinate current_pos = you->head;
    CoordArray adjacent;
    Coordinate adjacent_pointer[4];
    adjacent.p_elements = adjacent_pointer;
    get_adjacent(current_pos, &adjacent);
    Coordinate down = adjacent.p_elements[0];
    Coordinate up = adjacent.p_elements[1];
    Coordinate right = adjacent.p_elements[2];
    Coordinate left = adjacent.p_elements[3];
    int health = you->health;

    // Data
    // closest_weak_head
    Coordinate closest_head_pointer[1];
    CoordArray closest_weak_head = find_weak_head(game, board, you, current_pos, closest_head_pointer);

    // will_collide
    bool will_collide_down = will_collide(board, down, coord_array(0, null_coord));
    bool will_collide_up = will_collide(board, up, coord_array(0, null_coord));
    bool will_collide_right = will_collide(board, right, coord_array(0, null_coord));
    bool will_collide_left = will_collide(board, left, coord_array(0, null_coord));

    // Check for hazards
    bool hazard_down = contains_coord(board->hazards, down);
    bool hazard_up = contains_coord(board->hazards, up);
    bool hazard_right = contains_coord(board->hazards, right);
    bool hazard_left = contains_coord(board->hazards, left);

    // area_size, check_area
    int max_area = you->length < MAX_SEARCH ? you->length : MAX_SEARCH;
    Coordinate *gone_pointer = malloc(max_area * sizeof(Coordinate));

    int down_area = 0;
    if(!will_collide_down){
        down_area = check_area(game, board, you, down, coord_array(max_area, gone_pointer), 0, 0, max_area);
        if(hazard_down){down_area = down_area / 2 + 1;}
        
        char p_data[STRING_SIZE];
        snprintf(p_data, STRING_SIZE, "max_down: %d down_area: %d", max_area, down_area);
        log_data(game->p_id, p_data);
    }

    int up_area = 0;
    if(!will_collide_up){
        up_area = check_area(game, board, you, up, coord_array(max_area, gone_pointer), 0, 0, max_area);
        if(hazard_up){up_area = up_area / 2 + 1;}

        char p_data[STRING_SIZE];
        snprintf(p_data, STRING_SIZE, "max_up: %d up_area: %d", max_area, up_area);
        log_data(game->p_id, p_data);
    }

    int right_area = 0;
    if(!will_collide_right){
        right_area = check_area(game, board, you, right, coord_array(max_area, gone_pointer), 0, 0, max_area);
        if(hazard_right){right_area = right_area / 2 + 1;}

        char p_data[STRING_SIZE];
        snprintf(p_data, STRING_SIZE, "max_right: %d right_area: %d", max_area, right_area);
        log_data(game->p_id, p_data);
    }

    int left_area = 0;
    if(!will_collide_left){
        left_area = check_area(game, board, you, left, coord_array(max_area, gone_pointer), 0, 0, max_area);
        if(hazard_left){left_area = left_area / 2 + 1;}

        char p_data[STRING_SIZE];
        snprintf(p_data, STRING_SIZE, "max_left: %d left_area: %d", max_area, left_area);
        log_data(game->p_id, p_data);
    }

    free(gone_pointer);

    // can_escape
    bool can_escape_down = can_escape(you, down_area, MAX_SEARCH);
    bool can_escape_up = can_escape(you, up_area, MAX_SEARCH);
    bool can_escape_right = can_escape(you, right_area, MAX_SEARCH);
    bool can_escape_left = can_escape(you, left_area, MAX_SEARCH);

    // against_wall
    bool against_wall_down = distance_from_wall(board, down, 0);
    bool against_wall_up = distance_from_wall(board, up, 0);
    bool against_wall_right = distance_from_wall(board, right, 0);
    bool against_wall_left = distance_from_wall(board, left, 0);

    // safe_zone
    bool safe_zone_down = distance_from_wall(board, down, SAFE_DISTANCE);
    bool safe_zone_up = distance_from_wall(board, up, SAFE_DISTANCE);
    bool safe_zone_right = distance_from_wall(board, right, SAFE_DISTANCE);
    bool safe_zone_left = distance_from_wall(board, left, SAFE_DISTANCE);

    // near_head
    bool near_head_down = near_head(board, you, down);
    bool near_head_up = near_head(board, you, up);
    bool near_head_right = near_head(board, you, right);
    bool near_head_left = near_head(board, you, left);

    // headon_death
    bool headon_death_down = headon_death(board, you, down);
    bool headon_death_up = headon_death(board, you, up);
    bool headon_death_right = headon_death(board, you, right);
    bool headon_death_left = headon_death(board, you, left);

    // headon_kill
    bool headon_kill_down = headon_kill(board, you, down);
    bool headon_kill_up = headon_kill(board, you, up);
    bool headon_kill_right = headon_kill(board, you, right);
    bool headon_kill_left = headon_kill(board, you, left);

    // wall_trap
    bool wall_trap_down = wall_trap(board, you, down);
    bool wall_trap_up = wall_trap(board, you, up);
    bool wall_trap_right = wall_trap(board, you, right);
    bool wall_trap_left = wall_trap(board, you, left);

    enum Direction direction;
    int decision;

    // Decision
    // If possible, kill a nearby snake
    if(
        !will_collide_down
        && !near_head_down
        && headon_kill_down
    ){
        direction = e_down;
        decision = 1;
    }else if(
        !will_collide_up
        && !near_head_up
        && headon_kill_up
    ){
        direction = e_up;
        decision = 2;
    }else if(
        !will_collide_right
        && !near_head_right
        && headon_kill_right
    ){
        direction = e_right;
        decision = 3;
    }else if(
        !will_collide_left
        && !near_head_left
        && headon_kill_left
    ){
        direction = e_left;
        decision = 4;
    }

    // If safe, trap other snaeks against the wall
    else if(
        !will_collide_down
        && can_escape_down
        && !near_head_down
        && wall_trap_down
    ){
        direction = e_down;
        decision = 5;
    }else if(
        !will_collide_up
        && can_escape_up
        && !near_head_up
        && wall_trap_up
    ){
        direction = e_up;
        decision = 6;
    }else if(
        !will_collide_right
        && can_escape_right
        && !near_head_right
        && wall_trap_right
    ){
        direction = e_right;
        decision = 7;
    }else if(
        !will_collide_left
        && can_escape_left
        && !near_head_left
        && wall_trap_left
    ){
        direction = e_left;
        decision = 8;
    // Move towards closest snake that I can kill, avoid walls, checking for collisions, can_escape, and near_head
    }else if(
        closest_weak_head.size == 1 && closest_weak_head.p_elements[0].y < current_pos.y
        && !will_collide_down
        && can_escape_down
        && !against_wall_down
        && !near_head_down
    ){
        direction = e_down;
        decision = 17;
    }else if(
        closest_weak_head.size == 1 && closest_weak_head.p_elements[0].y > current_pos.y
        && !will_collide_up
        && can_escape_up
        && !against_wall_up
        && !near_head_up
    ){
        direction = e_up;
        decision = 18;
    }else if(
        closest_weak_head.size == 1 && closest_weak_head.p_elements[0].x > current_pos.x
        && !will_collide_right
        && can_escape_right
        && !against_wall_right
        && !near_head_right
    ){
        direction = e_right;
        decision = 19;
    }else if(
        closest_weak_head.size == 1 && closest_weak_head.p_elements[0].x < current_pos.x
        && !will_collide_left
        && can_escape_left
        && !against_wall_left
        && !near_head_left
    ){
        direction = e_left;
        decision = 20;
    
    // Circle board in safe zone, avoid walls, hazards, checking for collisions, can_escape, and near_head
    }else if(
        !will_collide_down
        && !hazard_down
        && can_escape_down
        && !against_wall_down
        && safe_zone_down
        && !near_head_down
    ){
        direction = e_down;
        decision = 21;
    }else if(
        !will_collide_up
        && !hazard_up
        && can_escape_up
        && !against_wall_up
        && safe_zone_up
        && !near_head_up
    ){
        direction = e_up;
        decision = 22;
    }else if(
        !will_collide_right
        && !hazard_right
        && can_escape_right
        && !against_wall_right
        && safe_zone_right
        && !near_head_right
    ){
        direction = e_right;
        decision = 23;
    }else if(
        !will_collide_left
        && !hazard_left
        && can_escape_left
        && !against_wall_left
        && safe_zone_left
        && !near_head_left
    ){
        direction = e_left;
        decision = 24;

    // Escape alive, avoid walls, hazards, checking for collisions, can_escape, and near_head
    }else if(
        !will_collide_down
        && !hazard_down
        && can_escape_down
        && !against_wall_down
        && !near_head_down
    ){
        direction = e_down;
        decision = 25;
    }else if(
        !will_collide_up
        && !hazard_up
        && can_escape_up
        && !against_wall_up
        && !near_head_up
    ){
        direction = e_up;
        decision = 26;
    }else if(
        !will_collide_right
        && !hazard_right
        && can_escape_right
        && !against_wall_right
        && !near_head_right
    ){
        direction = e_right;
        decision = 27;
    }else if(
        !will_collide_left
        && !hazard_left
        && can_escape_left
        && !against_wall_left
        && !near_head_left
    ){
        direction = e_left;
        decision = 28;
    
    // Escape alive, avoid walls, checking for collisions, can_escape, and near_head
    }else if(
        !will_collide_down
        && can_escape_down
        && !against_wall_down
        && !near_head_down
    ){
        direction = e_down;
        decision = 29;
    }else if(
        !will_collide_up
        && can_escape_up
        && !against_wall_up
        && !near_head_up
    ){
        direction = e_up;
        decision = 30;
    }else if(
        !will_collide_right
        && can_escape_right
        && !against_wall_right
        && !near_head_right
    ){
        direction = e_right;
        decision = 31;
    }else if(
        !will_collide_left
        && can_escape_left
        && !against_wall_left
        && !near_head_left
    ){
        direction = e_left;
        decision = 32;

    // Escape alive, checking for collisions, can_escape, and near_head
    }else if(
        !will_collide_down
        && can_escape_down
        && !near_head_down
    ){
        direction = e_down;
        decision = 33;
    }else if(
        !will_collide_up
        && can_escape_up
        && !near_head_up
    ){
        direction = e_up;
        decision = 34;
    }else if(
        !will_collide_right
        && can_escape_right
        && !near_head_right
    ){
        direction = e_right;
        decision = 35;
    }else if(
        !will_collide_left
        && can_escape_left
        && !near_head_left
    ){
        direction = e_left;
        decision = 36;

    // Escape alive, checking for collisions, can_escape, and headon_death
    }else if(
        !will_collide_down
        && can_escape_down
        && !headon_death_down
    ){
        direction = e_down;
        decision = 37;
    }else if(
        !will_collide_up
        && can_escape_up
        && !headon_death_up
    ){
        direction = e_up;
        decision = 38;
    }else if(
        !will_collide_right
        && can_escape_right
        && !headon_death_right
    ){
        direction = e_right;
        decision = 39;
    }else if(
        !will_collide_left
        && can_escape_left
        && !headon_death_left
    ){
        direction = e_left;
        decision = 40;
    
    // Move towards largest area, checking for collisions, and near_head
    }else if(
        !will_collide_down
        && down_area == max(down_area, up_area, right_area, left_area)
        && !near_head_down
    ){
        direction = e_down;
        decision = 41;
    }else if(
        !will_collide_up
        && up_area == max(down_area, up_area, right_area, left_area)
        && !near_head_up
    ){
        direction = e_up;
        decision = 42;
    }else if(
        !will_collide_right
        && right_area == max(down_area, up_area, right_area, left_area)
        && !near_head_right
    ){
        direction = e_right;
        decision = 43;
    }else if(
        !will_collide_left
        && left_area == max(down_area, up_area, right_area, left_area)
        && !near_head_left
    ){
        direction = e_left;
        decision = 44;
    
    // Move towards largest area, checking for collisions, and headon_death
    }else if(
        !will_collide_down
        && down_area == max(down_area, up_area, right_area, left_area)
        && !headon_death_down
    ){
        direction = e_down;
        decision = 45;
    }else if(
        !will_collide_up
        && up_area == max(down_area, up_area, right_area, left_area)
        && !headon_death_up
    ){
        direction = e_up;
        decision = 46;
    }else if(
        !will_collide_right
        && right_area == max(down_area, up_area, right_area, left_area)
        && !headon_death_right
    ){
        direction = e_right;
        decision = 47;
    }else if(
        !will_collide_left
        && left_area == max(down_area, up_area, right_area, left_area)
        && !headon_death_left
    ){
        direction = e_left;
        decision = 48;
    }
    
    // Move towards largest area, checking for collisions
    else if(
        !will_collide_down
        && down_area == max(down_area, up_area, right_area, left_area)
    ){
        direction = e_down;
        decision = 49;
    }else if(
        !will_collide_up
        && up_area == max(down_area, up_area, right_area, left_area)
    ){
        direction = e_up;
        decision = 50;
    }else if(
        !will_collide_right
        && right_area == max(down_area, up_area, right_area, left_area)
    ){
        direction = e_right;
        decision = 51;
    }else if(
        !will_collide_left
        && left_area == max(down_area, up_area, right_area, left_area)
    ){
        direction = e_left;
        decision = 52;
    }

    // Pray, no escape and accept headon
    else if(!will_collide_down){
        direction = e_down;
        decision = 53;
    }else if(!will_collide_up){
        direction = e_up;
        decision = 54;
    }else if(!will_collide_right){
        direction = e_right;
        decision = 55;
    }else if(!will_collide_left){
        direction = e_left;
        decision = 56;
    
    // Accept death
    }else{
        direction = e_up;
        decision = 57;
    }

    // Log data
    char data[STRING_SIZE];
    snprintf(data, STRING_SIZE, "health: %d\ndecision: %d\npos: x:%d y:%d\ndir: %d\nturn: %d\n",
        health, decision, current_pos.x, current_pos.y, direction, turn);
    log_data(game->p_id, data);

    return direction;
}
