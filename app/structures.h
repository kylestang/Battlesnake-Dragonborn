#include <stdbool.h>

// Enumerations
enum Direction{e_down, e_up, e_right, e_left};

// Structures
typedef struct
{
    int x;
    int y;
} Coordinate;

typedef struct
{
    int size;
    int max_size;
    Coordinate *p_elements;
} CoordArray;

typedef struct
{
    int id;
    int health;
    CoordArray body;
    Coordinate head;
    int length;
} Battlesnake;

typedef struct
{
    int size;
    int max_size;
    Battlesnake *p_elements;
} SnakeArray;

typedef struct
{
    int timeout;
    char *p_id;
} Game;

typedef struct
{
    int height;
    int width;
    CoordArray food;
    SnakeArray snakes;
} Board;

// Functions
Coordinate coordinate(int x, int y);
bool equals_coord(Coordinate pos1, Coordinate pos2);
void append_coord(CoordArray *array, Coordinate pos, char *p_game_id);
bool contains_coord(CoordArray array, Coordinate pos);
void append_snake(SnakeArray *array, Battlesnake snake, char *p_game_id);
CoordArray coord_array(int max_size, Coordinate *p_elements);
void log_data(char *game_id, char *data);
