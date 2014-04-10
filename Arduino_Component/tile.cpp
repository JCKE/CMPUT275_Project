/* 
   These functions all dictate how tile information is accessed and stored.
   Also, color565() somehow found it's way in here...
*/

#include "tile.h"

hashtable *ht_new(byte tiles_y)
{
  // Sets up a new hashtable where tiles are hashed into buckets according to their y coordinate.
  // There are as many buckets as there are rows of pixels, which is the map's height.

    hashtable *ht = (hashtable *) malloc(sizeof(hashtable));

    ht->buckets = (ht_node **) calloc(tiles_y, sizeof(ht_node *));

    return ht;
}

void fill_tiles(hashtable *ht, tile tile_list[], byte tiles_x, byte tiles_y)
{
  /*
    This function takes in a hashtable created by ht_new(), a massive list of tiles created by my
    map_convertor.py program, and the size of the map's width and height. This is where all the 
    resource generation happens.

    Based on the contour map, resources will spawn with different multipliers ranging from 0-30.
    The contour value is temporarily stored in the 'resource_amount_1' spot to save on memory space 
    since the contour value is useless once the map loads.

    From here, the tile type is determined and different resources and resource types are assigned 
    accordingly. Some tiles have a chance of spawning a secondary resource (wood in mountains, 
    food in the forests, gold in the water)

    After everything has been calculated for a tile, the information is stored into the hashtable 
    using the 'node' stuct we developed last semester.
   */

  for(int i = 0; i < (tiles_x * tiles_y); i++)
    {
      tile t = tile_list[i];
      byte cont_region = t.resource_amount_1;
      byte cont_multiplier = 0;
      t.resource_type_1 = NULL;
      t.resource_type_2 = NULL;

      byte resource_2_spawn = int(random(6)/5); // 1/6 chance of spawning a secondary resource
	  
      if(cont_region == 1)
	cont_multiplier = random(10);
      else if(cont_region == 2)
	cont_multiplier = random(8, 19);
      else if(cont_region == 3)
	cont_multiplier = random(14, 31);

      // No resources for tile types Beach, Wall, and None
      if(t.type == 'G') // Grass
	{
	  t.resource_amount_1 = cont_multiplier*random(1, 3);
	  t.resource_type_1 = 'F';
	}
      else if(t.type == 'F') // Forest
	{
	  t.resource_amount_1 = cont_multiplier*random(3, 6);
	  t.resource_type_1 = 'W';
	  t.resource_type_2 = 'F';
	  if(resource_2_spawn)
	      t.resource_amount_2 = cont_multiplier*random(1, 3);
	}
      else if(t.type == 'M') // Mountain
	{
	  t.resource_amount_1 = cont_multiplier*random(3, 6);
	  t.resource_type_1 = 'G';
	  t.resource_type_2 = 'W';

	  if(resource_2_spawn)
	      t.resource_amount_2 = cont_multiplier*random(1, 3);
	}
      else if(t.type == 'R') // Road
	{
	  if(resource_2_spawn*random(2)) // Very, very small chance of finding gold, but when you do it's a lot!
	    {
	      t.resource_amount_2 = random(100, 151);
	      t.resource_type_2 = 'G';
	    }
	}
      else if(t.type == 'H') // Water ('H' stands for H20 since 'W' was taken by Wall)
	{
	  t.resource_amount_1 = cont_multiplier*random(2, 4);
	  t.resource_type_1 = 'F';
	  t.resource_type_2 = 'G';

	  if(resource_2_spawn)
	      t.resource_amount_2 = cont_multiplier*random(1, 3);
	}

      int index = t.y_pos;
      ht_node *node = (ht_node*) malloc(sizeof(ht_node));

      node->t = t;
      node->next = ht->buckets[index];
      ht->buckets[index] = node;
    }
}

tile *tile_lookup(hashtable *ht, byte x_pos, byte y_pos)
{    
  // Look up a tile based on given coordinates and return it
  ht_node *node = ht->buckets[y_pos];

  while(node)
    {
      if(node->t.x_pos == x_pos && node->t.y_pos == y_pos)
	return &node->t;

      node = node->next;
    }

  return NULL;
}

int get_speed_info(hashtable *ht, byte x_pos, byte y_pos)
{
  /* 
     Returns a number which will be interpretted as millisecond of time to delay a unit's
     movement across a specific tile. Different tiles will slow the units down by different
     amounts. Initially, this was supposed to factor in a lot more than just a few hundred
     milliseconds, but the pyhton side ended turns way too fast for this to be feasable.
  */

  tile *t = tile_lookup(ht, x_pos, y_pos);
  char tile_type = t->type;
  if(tile_type == 'B' || tile_type == 'G' || tile_type == 'R')
    return(80);
  else if(tile_type == 'H' || tile_type == 'F')
    return(220);
  else if(tile_type == 'M' )
    return(340);
}

unsigned long color565(byte redNumber, byte greenNumber, byte blueNumber)
{
  // A color convertor that takes 3 value of RGB from 0-255 and bitshifts them to return a 16-bit version
  redNumber = redNumber/8;
  greenNumber = greenNumber/4;
  blueNumber = blueNumber/8;

  redNumber = redNumber << 11;
  greenNumber = greenNumber << 5;
  unsigned long finalNumber = redNumber+greenNumber+blueNumber;
    
  return(finalNumber);
}
