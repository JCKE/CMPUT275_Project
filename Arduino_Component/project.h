#ifndef __PROJECT_H__
#define __PROJECT_H__

#include <UTFT.h>
#include "tile.h"
#include "Maps/mp1.h"
#include <avr/pgmspace.h>

tile *current_map = mp1;
const int tile_gather_time = 150; // Time it takes to mine from a tile in millis

char unit_names[20][6] = {"Leah", "Sarah", "Tracy", "Julia", "Ava", "Alice", "Jill", "Megan", "Kyla", "Casey", // Ladies first
			  "Mike", "Walt", "Zack", "Jack", "Tyler", "Mack", "Smith", "Alex", "Jared", "Dan"};

typedef struct {
  bool active; // Basic true/false for checking
  bool moving;
  bool gathering;

  char profficiency; // Profficiency related variables
  byte prof_lvl;
  int wood;
  int gold;
  int food;

  char resource_type; // Resources the unit is currently carrying
  byte resource_amount;
  unsigned long gather_time;
  byte y_pos; // preset info end here
  byte x_pos;

  unsigned long depart_time; // Moving variables
  int move_speed;
  byte x_dest;
  byte y_dest;

  byte sprite;
  char name[6];
} unit;

typedef struct {
  char team[10];
  byte num_units;
  int gold;
  int wood;
  int food;

  int resource_box_x; // The top left corners of each player's resource box
  int resource_box_y;
  byte gate_x; // The gate corners
  byte gate_y;
  unit units[10];
} player;

// Declare which fonts we will be using
extern uint8_t SmallFont[];
extern uint8_t BigFont[];

UTFT myGLCD(ITDB32S,38,39,40,41);   // For the Arduino Mega
UTFT myGLCD2(ITDB32S,2,3,4,5);
UTFT myGLCD3(ITDB32S,6,7,8,9);
UTFT myGLCD4(ITDB32S,10,11,12,18);

/* Total number of tiles covering the width and height of the screens,
   and the size of each tile's x and y dimensions*/
#define tile_width  20
#define tile_height 16
#define tile_x_size 32
#define tile_y_size 30
hashtable *tile_data;

const int ScrXsize = 320; // Size of the screen's width (prettier than typing 'myGLCD.getDisplayYSize()' everywhere...
const int ScrYsize = 240; // Size of the screen's height


player green = { "GREEN", 1, 0, 0, 0, 0, ScrYsize - (3 * tile_y_size), 3, 13 };
player red = { "RED", 1, 0, 0, 0, ScrXsize - (4 * tile_x_size), ScrYsize - (3 * tile_y_size), 16, 13 };

player *current_player = &red;
unit *current_unit = &red.units[0];

/* Joystick Definitions */
#define VERT   0
#define HORIZ  1
#define SEL    14
#define SEL_2  15

#define VERT_2   2
#define HORIZ_2  3
#define SEL_3    16
#define SEL_4    17

byte current_VERT = VERT;
byte current_HORIZ = HORIZ;
byte current_SEL = SEL;
byte current_SEL_2 = SEL_2;

/* Cursor X and Y coordinates */
int CursorX = 15;
int CursorY = 12;
int prev_CursorX = CursorX;
int prev_CursorY = CursorY;
int JoyCenterY;
int JoyCenterX;
int JoyCenterY_2;
int JoyCenterX_2;

int current_JoyCenterY;
int current_JoyCenterX;

unsigned long cursor_last_move = 0;

/* Increment of how many pixels Cursor will move in a direction 
   Region around resting position of Joystick that vertical 
   or horixontal values must exceed to move pixel */
const int INCREMENT = 1;
const int OFFSET = 30;
const int DelayTime = 15;


const unsigned long gold_color = color565(124, 102, 0);
const unsigned long wood_color = color565(61, 30, 7);
const unsigned long food_color = color565(108, 0, 0);


/* All of the tile images go here*/
extern prog_uint16_t Beach[960]; // 32x30
extern prog_uint16_t Forest[960];
extern prog_uint16_t Grass[960];
extern prog_uint16_t Mountain[960];
extern prog_uint16_t Road[960];
extern prog_uint16_t Wall[960];
extern prog_uint16_t Water[960];

// All the images for the bases
extern prog_uint16_t Green_Corner[960];    // 32x30
extern prog_uint16_t Green_Wall_X[154];    // 14x11
extern prog_uint16_t Green_Wall_Y[154];    // 11x14
extern prog_uint16_t Red_Corner[960];      // 32x30
extern prog_uint16_t Red_Wall_X[154];      // 14x11
extern prog_uint16_t Red_Wall_Y[154];      // 11x14

extern prog_uint16_t Gold_Sprite[560];     // 28x20
extern prog_uint16_t Wood_Sprite[704];     // 32x22
extern prog_uint16_t Food_Sprite[572];     // 26x22
extern prog_uint16_t Resource_Board[2304]; // 96x24
extern prog_uint16_t Unit_Sprite[210];     // 10x21
extern prog_uint16_t Units_Sprite[462];    // 22x21

// The unit sprites
//<><>UNITS<><>
extern prog_uint16_t Canoe[560]; // 20x28
extern prog_uint16_t Male_3_F[672]; // 24x28
extern prog_uint16_t Male_3_B[560]; // 20x28
extern prog_uint16_t Male_2_F[672]; // 24x28
extern prog_uint16_t Male_2_B[560]; // 20x28
extern prog_uint16_t Male_1_F[672]; // 24x28
extern prog_uint16_t Male_1_B[560]; // 20x28
extern prog_uint16_t Female_3_F[672]; // 24x28
extern prog_uint16_t Female_3_B[560]; // 20x28
extern prog_uint16_t Female_2_F[672]; // 24x28
extern prog_uint16_t Female_2_B[560]; // 20x28
extern prog_uint16_t Female_1_F[672]; // 24x28
extern prog_uint16_t Female_1_B[560]; // 20x28

void assign_names();
void load_map(hashtable *ht);
void initialize_LCD();
void draw_tile(hashtable *ht, byte x_pos, byte y_pos);
void Move_Cursor(hashtable *ht);
void draw_cursor(int x_pos, int y_pos);
void print_txt_to_box(char message[], byte x_shift, byte y_shift, player *sel_player = current_player, unsigned long back_color = VGA_TRANSPARENT);
void print_int_to_box(int value, byte x_shift, byte y_shift, player *sel_player = current_player, unsigned long back_color = VGA_TRANSPARENT);

void print_unit_info(unit *sel_unit = current_unit, player *sel_player = current_player);
void update_unit_resources(char resource_type, int resource_amount, unit *sel_unit = current_unit, player *sel_player = current_player);

void draw_unit(hashtable *ht, int x_pos, int y_pos, byte sprite, char front_back, unit *sel_unit = current_unit, char team[] = current_player->team);
void check_button_press(hashtable *ht);
void move_units(hashtable *ht, player *sel_player = current_player);
void transfer_resources(hashtable *ht, player *sel_player = current_player);
void gather_resources(hashtable *ht, player *sel_player = current_player);

void draw_bases();
void draw_base_corner(char team);

void print_assets(char asset_type, int asset_amount, char cursor_or_player, player *sel_player = current_player);
void update_cursor_assets(char asset_type_1, int asset_amount_1, char asset_type_2, int asset_amount_2, player *sel_player = current_player);
void change_turns(hashtable *ht, player *sel_player = current_player);
void print_unit_resources(char resource_type, int resource_amount, unit *sel_unit, player *sel_player);
#endif
