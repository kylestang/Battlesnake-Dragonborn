#include <stdbool.h>
#include <stdio.h>
#include "structures.h"
#include "constants.h"

// Returns an instance of CoordArray limited to max_size
CoordArray coord_array(int max_size){
    Coordinate elements[max_size];
    CoordArray array;
    array.size = 0;
    array.max_size = max_size;
    array.p_elements = elements;
    return array;
}

// Returns true if pos1 and pos2 are the same location
bool equals_coord(Coordinate pos1, Coordinate pos2){
    return pos1.x == pos2.x && pos1.y == pos2.y;
}

// Appends pos to array if there's space, otherwise logs an error
void append_coord(CoordArray *array, Coordinate pos, char *p_game_id){
    if(array->size < array->max_size){
        array->p_elements[array->size] = pos;
        array->size++;
    } else{
        char data[STRING_SIZE];
        snprintf(data, STRING_SIZE, "Error: structures.c: append_coord(): array full: size: %d", array->size);
        log_data(p_game_id, data);
    }
}

// Returns true if array contains coord
bool contains_coord(CoordArray array, Coordinate pos){
    for(int i = 0; i < array.size; i++){
        if(equals_coord(array.p_elements[i], pos)){
            return true;
        }
    }
    return false;
}

// Appends snake to array if there's space, otherwise logs an error
void append_snake(SnakeArray *array, Battlesnake snake, char *p_game_id){
    if(array->size < array->max_size){
        array->p_elements[array->size] = snake;
        array->size++;
    } else{
        char data[STRING_SIZE];
        snprintf(data, STRING_SIZE, "Error: structures.c: append_snake(): array full: size: %d", array->size);
        log_data(p_game_id, data);
    }
}

// Print log data, if logging is true, log to file
void log_data(char *game_id, char *data){
    char p_log_location[STRING_SIZE];
    snprintf(p_log_location, STRING_SIZE, LOG_FORMAT, game_id);

    FILE *log_file;

    printf("%s\n", data);
    if(LOGGING){
        log_file = fopen(p_log_location, "a");
        fprintf(log_file, "%s\n", data);
        fclose(log_file);
    }
}
