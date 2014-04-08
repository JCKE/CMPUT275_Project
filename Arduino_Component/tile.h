#ifndef __TILE_H__
#define __TILE_H__

#include <Arduino.h>

typedef struct {
  byte x_pos;
  byte y_pos;
  char type; // B, G, F, M, R, W, H
  byte resource_amount_1;
  char resource_type_1; // W ood, G old, F ood
  byte resource_amount_2;
  char resource_type_2;
} tile;

typedef struct _ht_node {
    tile t;
    struct _ht_node *next;
} ht_node;

typedef struct {
    ht_node* *buckets;
} hashtable;

hashtable *ht_new(byte tiles_y);
void fill_tiles(hashtable *ht, tile tile_list[], byte tiles_x, byte tiles_y);
tile *tile_lookup(hashtable *ht, byte x_pos, byte y_pos);
int get_speed_info(hashtable *ht, byte x_pos, byte y_pos);
unsigned long color565(unsigned long redNumber, long greenNumber, long blueNumber);

#endif
