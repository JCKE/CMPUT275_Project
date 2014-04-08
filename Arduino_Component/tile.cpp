#include "tile.h"

hashtable *ht_new(byte tiles_y)
{
    hashtable *ht = (hashtable *) malloc(sizeof(hashtable));

    ht->buckets = (ht_node **) calloc(tiles_y, sizeof(ht_node *));

    return ht;
}

void fill_tiles(hashtable *ht, tile tile_list[], byte tiles_x, byte tile_y)
{
  for(int i = 0; i< (tiles_x * tile_y); i++)
    {
      tile t = tile_list[i];
      byte cont_region = t.resource_amount_1;
      byte cont_multiplier = 0;
      t.resource_type_1 = NULL;
      t.resource_type_2 = NULL;

      byte resource_2_spawn = int(random(6)/5); // 1/6 chance of spawning a secondary resource
	  
      if(cont_region == 1)
	cont_multiplier = random(5); // Between 0 and 20
      else if(cont_region == 2)
	cont_multiplier = random(4, 19); // Between 20 and 90
      else if(cont_region == 3)
	cont_multiplier = random(12, 31); // Between 60 and 150

      // No resources for tile types Beach, Wall, and None
      if(t.type == 'G') // Grass
	{
	  t.resource_amount_1 = cont_multiplier*random(1, 3);
	  t.resource_type_1 = 'F';
	}
      else if(t.type == 'F')
	{
	  t.resource_amount_1 = cont_multiplier*random(3, 6);
	  t.resource_type_1 = 'W';

	  if(resource_2_spawn)
	    {
	      t.resource_amount_2 = cont_multiplier*random(1, 3);
	      t.resource_type_2 = 'F';
	    }
	}
      else if(t.type == 'M')
	{
	  t.resource_amount_1 = cont_multiplier*random(3, 6);
	  t.resource_type_1 = 'G';

	  if(resource_2_spawn)
	    {
	      t.resource_amount_2 = cont_multiplier*random(1, 3);
	      t.resource_type_2 = 'W';
	    }
	}
      else if(t.type == 'R')
	{
	  if(resource_2_spawn*random(2)) // Very, very small chance of finding gold, but when you do it's a lot!
	    {
	      t.resource_amount_2 = random(100, 151);
	      t.resource_type_2 = 'G';
	    }
	}
      else if(t.type == 'H')
	{
	  t.resource_amount_1 = cont_multiplier*random(2, 4);
	  t.resource_type_1 = 'F';

	  if(resource_2_spawn)
	    {
	      t.resource_amount_2 = cont_multiplier*random(1, 3);
	      t.resource_type_2 = 'G';
	    }
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
  ht_node *node = ht->buckets[y_pos];

  while(node){
    if(node->t.x_pos == x_pos && node->t.y_pos == y_pos)
      return &node->t;

    node = node->next;
  }

  return NULL;
}

int get_speed_info(hashtable *ht, byte x_pos, byte y_pos)
{
  tile *t = tile_lookup(ht, x_pos, y_pos);
  char tile_type = t->type;
  if(tile_type == 'B' || tile_type == 'G' || tile_type == 'R')
    return(250);
  else if(tile_type == 'H' || tile_type == 'F')
    return(500);
  else if(tile_type == 'M' )
    return(750);
}

unsigned long color565(unsigned long redNumber, long greenNumber, long blueNumber)
{
  redNumber = redNumber/8;
  greenNumber = greenNumber/4;
  blueNumber = blueNumber/8;

  redNumber = redNumber << 11;
  greenNumber = greenNumber << 5;
  unsigned long finalNumber = redNumber+greenNumber+blueNumber;
    
  return(finalNumber);
}
