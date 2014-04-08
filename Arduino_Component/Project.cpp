#include "tile.h"
#include "project.h"

void setup()
{
  Serial.begin(9600);

  randomSeed(analogRead(7));
  pinMode(SEL,INPUT);
  digitalWrite(SEL,HIGH);
  JoyCenterY = analogRead(VERT);
  JoyCenterX = analogRead(HORIZ);
  
  tile_data = ht_new(tile_height);
  initialize_LCD();
  load_map(tile_data);

  Serial.print("MEMORY AVAILABLE: ");
  Serial.println(AVAIL_MEM);
}

void loop()
{
  Move_Cursor(tile_data);
  check_button_press(tile_data);
  move_units(tile_data);
  gather_resources(tile_data);
  transfer_resources(tile_data);
  delay(150);
}

void assign_names()
{  
  char temp_names[20][6];
  for(int i = 0; i < 20; i++)
    strcpy(temp_names[i], unit_names[i]);

  for(int i = 0; i < 1000; i++)
    {
      int swap_pos_1 = random(20);
      int swap_pos_2 = random(20);
      char temp_name[6];
      strcpy(temp_name, temp_names[swap_pos_1]);
      strcpy(temp_names[swap_pos_1], temp_names[swap_pos_2]);
      strcpy(temp_names[swap_pos_2], temp_name);
    }

  // Load Names
  for(int i = 0; i < 20; i++)
    {
      unit temp_unit = { false, false, false, NULL, 0, 0, 0, 0, NULL, 0, 0 };

      strcpy(temp_unit.name, temp_names[i]);
      for(int n = 0; n < 10; n++)
	{
	  if(!strcmp(temp_unit.name, unit_names[n]))
	    {
	      temp_unit.sprite = random(3);
	      break;
	    }
	  else
	    temp_unit.sprite = random(3, 6);
	}

      if(i%2==0)
	{
	  green.units[i/2] = temp_unit;
	  green.units[i/2].x_pos = green.gate_x;
	  green.units[i/2].y_pos = green.gate_y;
	}
      else
	{
	  red.units[i/2] = temp_unit;
	  red.units[i/2].x_pos = red.gate_x;
	  red.units[i/2].y_pos = red.gate_y;
	}
    }
}

void draw_tile(hashtable *ht, byte x_pos, byte y_pos)
{ 
  if(x_pos == 3 && y_pos == 13)
    draw_base_corner('G');
  else if(x_pos == 16 && y_pos == 13)
    draw_base_corner('R');
  else
    {
      tile *t = tile_lookup(ht, x_pos, y_pos);
      prog_uint16_t *Sel_Tile;

      if(t->type == 'B')
	Sel_Tile = Beach;
      else if(t->type == 'G')
	Sel_Tile = Grass;
      else if(t->type == 'F')
	Sel_Tile = Forest;
      else if(t->type == 'M')
	Sel_Tile = Mountain;
      else if(t->type == 'R')
	Sel_Tile = Road;
      else if(t->type == 'W')
	Sel_Tile = Wall;
      else if(t->type == 'H')
	Sel_Tile = Water;

      if(t->type != 'N')// No Draw
	if(x_pos < tile_width/2 && y_pos < tile_height/2)
	  myGLCD.drawBitmap(x_pos*tile_x_size, y_pos*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
	else if(x_pos >= tile_width/2 && y_pos < tile_height/2)
	  myGLCD2.drawBitmap((x_pos - tile_width/2)*tile_x_size, y_pos*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
	else if(x_pos < tile_width/2 && y_pos >= tile_height/2)
	  myGLCD3.drawBitmap(x_pos*tile_x_size, (y_pos- tile_height/2)*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
	else if(x_pos >= tile_width/2 && y_pos >= tile_height/2)
	  myGLCD4.drawBitmap((x_pos - tile_width/2)*tile_x_size, (y_pos- tile_height/2)*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
    }
}

void print_txt_to_box(char message[], byte x_shift, byte y_shift, player *sel_player, unsigned long back_color)
{ 
  if(!strcmp(sel_player->team, "RED"))
    {
      myGLCD4.setBackColor(back_color);
      myGLCD4.setColor(VGA_WHITE);
      myGLCD4.print(message, sel_player->resource_box_x + x_shift+17, sel_player->resource_box_y + y_shift);
    }
  else if(!strcmp(sel_player->team, "GREEN"))
    {
      myGLCD3.setBackColor(back_color);
      myGLCD3.setColor(VGA_WHITE);
      myGLCD3.print(message, sel_player->resource_box_x + x_shift, sel_player->resource_box_y + y_shift);
    }
}

void print_int_to_box(int value, byte x_shift, byte y_shift, player *sel_player, unsigned long back_color)
{ 
  int x_val = sel_player->resource_box_x + x_shift;
  int y_val = sel_player->resource_box_y + y_shift;

  if(!strcmp(sel_player->team, "GREEN"))
    {
      if(back_color == gold_color || back_color == wood_color || back_color == food_color)
	{
	  myGLCD3.setBackColor(VGA_TRANSPARENT);
	  myGLCD3.setColor(back_color);
	  myGLCD3.fillRect(x_val, y_val+2, x_val + 22, y_val + 10);
	}
      else
	myGLCD3.setBackColor(back_color);
      myGLCD3.setColor(VGA_WHITE);
      myGLCD3.printNumI(value, x_val, y_val);
    }
  else if(!strcmp(sel_player->team, "RED"))
    {
      if(back_color == gold_color || back_color == wood_color || back_color == food_color)
	{
	  myGLCD4.setBackColor(VGA_TRANSPARENT);
	  myGLCD4.setColor(back_color);
	  myGLCD4.fillRect(x_val + 17, y_val+2, x_val + 39, y_val + 10);
	}
      else
	myGLCD4.setBackColor(back_color);
      myGLCD4.setColor(VGA_WHITE);
      myGLCD4.printNumI(value, x_val + 17, y_val);
    }
}


void initialize_LCD()
{
  // Setup the LCD
  myGLCD.InitLCD(LANDSCAPE);
  myGLCD.setFont(SmallFont);
  myGLCD.clrScr();
  myGLCD.setColor(VGA_WHITE);
  myGLCD.setBackColor(VGA_TRANSPARENT);

  myGLCD2.InitLCD(LANDSCAPE);
  myGLCD2.setFont(SmallFont);
  myGLCD2.clrScr();
  myGLCD2.setColor(VGA_WHITE);
  myGLCD2.setBackColor(VGA_TRANSPARENT);

  myGLCD3.InitLCD(LANDSCAPE);
  myGLCD3.setFont(SmallFont);
  myGLCD3.clrScr();
  myGLCD3.setColor(VGA_WHITE);
  myGLCD3.setBackColor(VGA_TRANSPARENT);

  myGLCD4.InitLCD(LANDSCAPE);
  myGLCD4.setFont(SmallFont);
  myGLCD4.clrScr();
  myGLCD4.setColor(VGA_WHITE);
  myGLCD4.setBackColor(VGA_TRANSPARENT);
}


int signof(int number){
  if(number < 0)
    return -1;
  else if(number > 0)
    return 1;
  return 0;
}

void load_map(hashtable *ht)
{
  fill_tiles(ht, current_map, tile_width, tile_height);

  for(int y = 0; y < tile_height; y++)
    {
      for(int x = 0; x < tile_width; x++)
	{
	  draw_tile(ht, x, y);
	}
    }

  draw_bases();

  update_assets('A', 0, 'P', &red);
  update_assets('A', 0, 'P', &green);
  draw_cursor(CursorX, CursorY);
  tile *t = tile_lookup(ht, CursorX, CursorY);
  update_cursor_assets(t->resource_type_1, t->resource_amount_1, t->resource_type_2, t->resource_amount_2);

  assign_names();
  for(int n = 0; n < 20; n++)
    Serial.print(unit_names[n]);
  Serial.println();
  green.units[0].active = true;
  red.units[0].active = true;

  Serial.println(current_unit->name);

  update_unit_info();
  draw_unit(current_unit->x_pos, current_unit->y_pos, current_unit->sprite, 'F');
}

void update_assets(char asset_type, int asset_amount, char cursor_or_player, player *sel_player)
{
  int x_shift = 0;
  int y_shift = 0;
  if(cursor_or_player == 'P')
    y_shift += 12;    

  if(!strcmp(sel_player->team, "GREEN"))
    x_shift -= 12;

  if(asset_type == 'G')
    print_int_to_box(asset_amount, 20 + x_shift, 41 + y_shift, sel_player, gold_color);
  else if(asset_type == 'W')
    print_int_to_box(asset_amount, 52 + x_shift, 41 + y_shift, sel_player, wood_color);
  else if(asset_type == 'F')
    print_int_to_box(asset_amount, 84 + x_shift, 41 + y_shift, sel_player, food_color);
  else if(asset_type == 'U')
    print_int_to_box(asset_amount, 94, 73, sel_player, VGA_BLACK);
  else if(asset_type == 'A' && cursor_or_player == 'P')
    {
      update_assets('G', sel_player->gold, cursor_or_player, sel_player);
      update_assets('W', sel_player->wood, cursor_or_player, sel_player);
      update_assets('F', sel_player->food, cursor_or_player, sel_player);
      update_assets('U', sel_player->num_units, cursor_or_player, sel_player);
    }
}

void update_cursor_assets(char asset_type_1, int asset_amount_1, char asset_type_2, int asset_amount_2, player *sel_player)
{
  if(asset_type_1 != 'G' && asset_type_2 != 'G')
    update_assets('G', 0, 'C', sel_player);
  if(asset_type_1 != 'W' && asset_type_2 != 'W')
    update_assets('W', 0, 'C', sel_player);
  if(asset_type_1 != 'F' && asset_type_2 != 'F')
    update_assets('F', 0, 'C', sel_player);

  update_assets(asset_type_1, asset_amount_1, 'C', sel_player);
  update_assets(asset_type_2, asset_amount_2, 'C', sel_player);
}



void update_unit_info(unit *sel_unit, player *sel_player)
{
  for(int space = 0; space < 6; space ++)
    print_txt_to_box(" ", 18 + (8*space), 65, sel_player, VGA_BLACK);
  print_txt_to_box(sel_unit->name, 18, 65, sel_player, VGA_BLACK);
  
  update_unit_resources(sel_unit->resource_type, sel_unit->resource_amount, sel_unit, sel_player);
}

void update_unit_resources(char resource_type, int resource_amount, unit *sel_unit, player *sel_player)
{
  sel_unit->resource_amount += resource_amount;

  if(sel_unit == current_unit && sel_unit->resource_type != NULL)
    {
      char msg[2];
      
      if(resource_type == 'W')
	strcpy(msg, "W");
      else if(resource_type == 'G')
	strcpy(msg, "G");
      else if(resource_type == 'F')
	strcpy(msg, "F");
      else
	strcpy(msg, NULL);

      print_txt_to_box(msg, 18, 76, sel_player, VGA_BLACK);

      print_txt_to_box("   ", 30, 76, sel_player, VGA_BLACK);
      print_int_to_box(sel_unit->resource_amount, 30, 76, sel_player, VGA_BLACK);
    }  
  
  if(resource_type == 'G')
    sel_unit->gold += resource_amount;
  else if(resource_type == 'W')
    sel_unit->wood += resource_amount;
  else if(resource_type == 'F')
    sel_unit->food += resource_amount;
}

void Move_Cursor(hashtable *ht)
{
  int JoyVert = analogRead(VERT);
  int JoyHoriz = analogRead(HORIZ);

  if(abs(JoyVert - JoyCenterY) > OFFSET || abs(JoyHoriz - JoyCenterX) > OFFSET)
    {
      // Moves CursorY up or down according to JoyVert
      if(abs(JoyVert - JoyCenterY) > OFFSET)
	{
	  CursorY += signof(JoyVert - JoyCenterY);
	  CursorY = constrain(CursorY, 0, tile_height - 1);
	}
  
      // Moves CursorX left or right according to JoyHoriz
      if(abs(JoyHoriz - JoyCenterX) > OFFSET)
	{
	  CursorX += signof(JoyHoriz - JoyCenterX);
	  CursorX = constrain(CursorX, 0, tile_width -1);
	}

      // Corners of base
      if(prev_CursorX == green.gate_x && prev_CursorY == green.gate_y) 
	{
	  if(CursorX == green.gate_x - 1 && (CursorY == green.gate_y || CursorY == green.gate_y + 1))
	    CursorX ++;
	  if((CursorX == green.gate_x - 1 || CursorX == green.gate_x) && CursorY == green.gate_y + 1)
	    CursorY --;
	}
      else if(prev_CursorX == red.gate_x && prev_CursorY == red.gate_y)
	{
	  if(CursorX == red.gate_x + 1 && (CursorY == red.gate_y || CursorY == red.gate_y + 1))
	    CursorX --;
	  if((CursorX == red.gate_x || CursorX == red.gate_x + 1) && CursorY == red.gate_y + 1)
	    CursorY --;
	}
      else if(CursorX < 3 && CursorY > 12 || CursorX > 16 && CursorY > 12)
	{
	  if(CursorX == 2)
	    CursorX ++;
	  else if(CursorX == 17)
	    CursorX --;	
	  
	  if(CursorY == 13)
	    CursorY --;
	}
      else if(CursorX < 4 && CursorY > 13 || CursorX > 15 && CursorY > 13)
	{
	  if(CursorX == 3)
	    CursorX ++;
	  else if(CursorX == 16)
	    CursorX --;	
	  
	  if(CursorY == 14)
	    CursorY --;
	}

      if(prev_CursorX != CursorX || prev_CursorY != CursorY)
	{
	  // Erases previous known position of Cursor
	  draw_tile(ht, prev_CursorX, prev_CursorY);
	  

	  tile *pt = tile_lookup(ht, prev_CursorX, prev_CursorY);
	  tile *t = tile_lookup(ht, CursorX, CursorY);

	  if(((pt->resource_type_1 != t->resource_type_1 || pt->resource_amount_1 != t->resource_amount_1) ||
	      (pt->resource_type_2 != t->resource_type_2 || pt->resource_amount_2 != t->resource_amount_2)) &&
	     (pt->resource_amount_1 > 0 || t->resource_amount_1 > 0 || pt->resource_amount_2 > 0 || t->resource_amount_2 > 0))
	    update_cursor_assets(t->resource_type_1, t->resource_amount_1, t->resource_type_2, t->resource_amount_2);

	  for(int u = 0; u < 20; u++)
	    {
	      unit *sel_unit; 
	      if(u<10)
		sel_unit = &green.units[u];
	      else
		sel_unit = &red.units[(u-10)];
		
	      if(sel_unit->active == true && prev_CursorX == sel_unit->x_pos && prev_CursorY == sel_unit->y_pos)
		if(sel_unit->gathering == true)
		  draw_unit(sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'B');
		else
		  draw_unit(sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'F');
	    }

	  // Draws new position of Cursor
	  draw_cursor(CursorX, CursorY);
	  prev_CursorX = CursorX;
	  prev_CursorY = CursorY;
	}
    }
}

void draw_cursor(int x_pos, int y_pos)
{
  if(x_pos < tile_width/2 && y_pos < tile_height/2)
    {
      x_pos *= tile_x_size;
      y_pos *= tile_y_size;
      myGLCD.setColor(VGA_WHITE);
      myGLCD.drawRect(x_pos + 15, y_pos + 4, x_pos + 16, y_pos + 27);
      myGLCD.drawRect(x_pos + 5, y_pos + 13, x_pos + 27, y_pos + 14);
    }
  else if(x_pos >= tile_width/2 && y_pos < tile_height/2)
    {
      x_pos = (x_pos - tile_width/2)*tile_x_size;
      y_pos *= tile_y_size;
      myGLCD2.setColor(VGA_WHITE);
      myGLCD2.drawRect(x_pos + 15, y_pos + 4, x_pos + 16, y_pos + 27);
      myGLCD2.drawRect(x_pos + 5, y_pos + 13, x_pos + 27, y_pos + 14);
    }
  else if(x_pos < tile_width/2 && y_pos >= tile_height/2)
    {
      x_pos *= tile_x_size;
      y_pos = (y_pos- tile_height/2)*tile_y_size;
      myGLCD3.setColor(VGA_WHITE);
      myGLCD3.drawRect(x_pos + 15, y_pos + 4, x_pos + 16, y_pos + 27);
      myGLCD3.drawRect(x_pos + 5, y_pos + 13, x_pos + 27, y_pos + 14);
    }
  else if(x_pos >= tile_width/2 && y_pos >= tile_height/2)
    {
      x_pos = (x_pos - tile_width/2)*tile_x_size;
      y_pos = (y_pos- tile_height/2)*tile_y_size;
      myGLCD4.setColor(VGA_WHITE);
      myGLCD4.drawRect(x_pos + 15, y_pos + 4, x_pos + 16, y_pos + 27);
      myGLCD4.drawRect(x_pos + 5, y_pos + 13, x_pos + 27, y_pos + 14);
    }
}

void check_button_press(hashtable *ht)
{
  int select = digitalRead(SEL);
  
  if(select == LOW)
    {
      if(current_unit->moving == false && current_unit->gathering == false)
	{
	  tile *t = tile_lookup(ht, CursorX, CursorY);

	  if((CursorX == current_player->gate_x && CursorY == current_player->gate_y && current_unit->resource_amount > 0) || 
	     ((t->resource_type_1 != NULL || t->resource_type_2 != NULL) && 
	      (t->resource_amount_1 > 0 || t->resource_amount_2 > 0) && current_unit->resource_amount < 200 &&
	      (current_unit->resource_type == t->resource_type_1 || current_unit->resource_type == t->resource_type_2 || current_unit->resource_type == NULL)))
	    {
	      if(t->resource_type_1 != NULL)
		{
		  current_unit->resource_type = t->resource_type_1;
		}
	      else if(t->resource_type_2 != NULL)
		{
		  current_unit->resource_type = t->resource_type_2;
		}

	      current_unit->moving = true;
	      current_unit->x_dest = CursorX;
	      current_unit->y_dest = CursorY;
	      current_unit->move_speed = (current_unit->resource_amount*5) + get_speed_info(ht, current_unit->x_pos, current_unit->y_pos);
	      current_unit->depart_time = millis();
	    }
	}
    }
}

void draw_unit(int x_pos, int y_pos, byte sprite, char front_back)
{
  prog_uint16_t *Sprite;
  
  int new_x_pos = x_pos * tile_x_size + 4;
  int new_y_pos = y_pos * tile_y_size;

  int sprite_width;
  int sprite_height = 28;

  if(front_back == 'F')
    {
      sprite_width = 24;

      if(sprite == 0) // 0 through 2 are the female sprites, 3 through 5 are the male
	Sprite = Female_1_F;
      else if(sprite == 1)
	Sprite = Female_2_F;
      else if(sprite == 2)
	Sprite = Female_3_F;
      else if(sprite == 3)
	Sprite = Male_1_F;
      else if(sprite == 4)
	Sprite = Male_2_F;
      else if(sprite == 5)
	Sprite = Male_3_F;
    }
  else if(front_back == 'B')
    {
      sprite_width = 20;
      new_x_pos += 2;

      if(sprite == 0) // 0 through 2 are the female sprites, 3 through 5 are the male
	Sprite = Female_1_B;
      else if(sprite == 1)
	Sprite = Female_2_B;
      else if(sprite == 2)
	Sprite = Female_3_B;
      else if(sprite == 3)
	Sprite = Male_1_B;
      else if(sprite == 4)
	Sprite = Male_2_B;
      else if(sprite == 5)
	Sprite = Male_3_B;
    }


  if(x_pos < tile_width/2 && y_pos < tile_height/2)
      myGLCD.drawBitmap(new_x_pos, new_y_pos, sprite_width, sprite_height, Sprite);
  else if(x_pos >= tile_width/2 && y_pos < tile_height/2)
      myGLCD2.drawBitmap(new_x_pos - (tile_width/2)*tile_x_size, new_y_pos, sprite_width, sprite_height, Sprite);
  else if(x_pos < tile_width/2 && y_pos >= tile_height/2)
    myGLCD3.drawBitmap(new_x_pos, new_y_pos - (tile_height/2)*tile_y_size, sprite_width, sprite_height, Sprite);
  else if(x_pos >= tile_width/2 && y_pos >= tile_height/2)
      myGLCD4.drawBitmap(new_x_pos - (tile_width/2)*tile_x_size, new_y_pos - (tile_height/2)*tile_y_size, sprite_width, sprite_height, Sprite);
}

void move_units(hashtable *ht, player *sel_player)
{
  for(int u = 0; u < 10; u++)
    {
      unit *sel_unit = &sel_player->units[u];
      if(sel_unit->active == true && sel_unit->moving == true)
	{
	  if(sel_unit->x_pos != sel_unit->x_dest || sel_unit->y_pos != sel_unit->y_dest)
	    {
	      if(millis() - sel_unit->depart_time > sel_unit->move_speed)
		{
		  draw_tile(ht, sel_unit->x_pos, sel_unit->y_pos);

		  if(abs(sel_unit->x_dest - sel_unit->x_pos) > abs(sel_unit->y_dest - sel_unit->y_pos))
		    sel_unit->x_pos += signof(sel_unit->x_dest - sel_unit->x_pos);
		  else
		    sel_unit->y_pos += signof(sel_unit->y_dest - sel_unit->y_pos);

		  draw_unit(sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'F');

		  sel_unit->move_speed = (sel_unit->resource_amount*5) + get_speed_info(ht, sel_unit->x_pos, sel_unit->y_pos);
		  sel_unit->depart_time = millis();
		}
	    }
	  else
	    {
	      if(sel_unit->x_pos == green.gate_x && sel_unit->y_pos == green.gate_y)
		{
		  Serial.println(sel_unit->x_pos);
		  Serial.println(sel_unit->y_pos);
		  Serial.println(sel_unit->x_dest);
		  Serial.println(sel_unit->y_dest);
		  Serial.println(sel_unit->gathering);
		  Serial.println(sel_unit->moving);
		  Serial.println(sel_unit->active);
		}
	      sel_unit->moving = false;
	      sel_unit->gathering = true;
	      sel_unit->gather_time = millis();
	      draw_unit(sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'B');
	      Serial.println("YUP");
	    }
	}
    }
}

void transfer_resources(hashtable *ht, player *sel_player)
{
  for(int u = 0; u < 10; u++)
    {
      unit *sel_unit = &sel_player->units[u];
      if(sel_unit->active == true && sel_unit->gathering == true && 
	 sel_unit->x_dest == sel_player->gate_x && sel_unit->y_dest == sel_player->gate_y)
	{
	  Serial.println("First!");
	  if(sel_unit->resource_amount > 0)
	    {
	      Serial.println("2nd!");
	      if(millis() - sel_unit->gather_time > tile_gather_time)
		{
		  byte resource_move = 5;

		  if(sel_unit->resource_amount - resource_move < 0)
		    resource_move = sel_unit->resource_amount;
		      
		  Serial.println("Tansfering yo!");
		  update_assets(sel_unit->resource_type, resource_move, 'P', sel_player);
		  
		  update_unit_resources(sel_unit->resource_type, (resource_move * -1), sel_unit, sel_player);
		}
	    }
	  else
	    {
	      sel_unit->gathering = false;
	      draw_unit(sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'F');
	    }
	}
    }
}

void gather_resources(hashtable *ht, player *sel_player)
{
  for(int u = 0; u < 10; u++)
    {
      unit *sel_unit = &sel_player->units[u];
      if(sel_unit->active == true && sel_unit->gathering == true)
	{
	  tile *t = tile_lookup(ht, sel_unit->x_pos, sel_unit->y_pos);
	    
	  if(((sel_unit->resource_type == t->resource_type_1 && t->resource_amount_1 > 0) || 
	      (sel_unit->resource_type == t->resource_type_2 && t->resource_amount_2 > 0)) &&
	     (sel_unit->x_dest != sel_player->gate_x || sel_unit->y_dest != sel_player->gate_y))
	    {
	      if(millis() - sel_unit->gather_time > tile_gather_time)
		{
		  byte resource_gain = 5;
		  if(sel_unit->resource_type == t->resource_type_1)
		    {
		      if(t->resource_amount_1 - resource_gain < 0)
			resource_gain = t->resource_amount_1;
		      
		      t->resource_amount_1 -= resource_gain;
		    }
		  else if(sel_unit->resource_type == t->resource_type_2)
		    {
		      if(t->resource_amount_2 - resource_gain < 0)
			resource_gain = t->resource_amount_2;
		      
		      t->resource_amount_2 -= resource_gain;
		    }
		  if(sel_unit->x_pos == CursorX && sel_unit->y_pos == CursorY)
		    update_cursor_assets(t->resource_type_1, t->resource_amount_1, t->resource_type_2, t->resource_amount_2);
		  
		  update_unit_resources(sel_unit->resource_type, resource_gain, sel_unit, sel_player);
		}
	    }
	  else
	    {
	      sel_unit->gathering = false;
	      draw_unit(sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'F');

	      if(sel_unit->resource_type == t->resource_type_1)
		{
		  t->resource_type_1 = NULL;
		  t->resource_amount_1 = 0;
		}
	      else if(sel_unit->resource_type == t->resource_type_2)
		{
		  t->resource_type_2 = NULL;
		  t->resource_amount_2 = 0;
		}
	    }
	}
    }
}

void draw_bases()
{
  // This function's purpose is to draw the base. Checkout the .psd or .jpeg mockup in the /Assets folder to see
  // what it looks like complete! A lot of drawing, and it would've been easier to just upload the mockup, but:
  // A) The image would be too big and need to be uploaded in 3 parts
  // B) The upload time would take approximately 5-6 seconds more.
  for(int t = 0; t < 12; t++)
    {
      myGLCD3.drawBitmap(green.resource_box_x+(t%4)*tile_x_size, green.resource_box_y+int(t/4)*tile_y_size, tile_x_size, tile_y_size, Water);
      myGLCD4.drawBitmap(red.resource_box_x+(t%4)*tile_x_size, red.resource_box_y+int(t/4)*tile_y_size, tile_x_size, tile_y_size, Water);
    }

  myGLCD3.setColor(VGA_BLACK);
  myGLCD3.fillRect(green.resource_box_x, green.resource_box_y + 17, green.resource_box_x+4*tile_x_size - 17, green.resource_box_y+3*tile_y_size - 1);

  myGLCD4.setColor(VGA_BLACK);
  myGLCD4.fillRect(red.resource_box_x + 17, red.resource_box_y + 17, red.resource_box_x+4*tile_x_size - 1, red.resource_box_y+3*tile_y_size - 1);

  // Drawing walls
  for(int w = 0; w<8; w++)
    {
      myGLCD3.drawBitmap(green.resource_box_x + 14*w, green.resource_box_y + 6, 14, 11, Green_Wall_X);
      myGLCD4.drawBitmap(red.resource_box_x + 16 + 14*w, red.resource_box_y + 6, 14, 11, Red_Wall_X);
    }

  for(int w = 0; w<6; w++)
    {
      myGLCD3.drawBitmap(green.resource_box_x + 111, green.resource_box_y + 6 + 14*w, 11, 14, Green_Wall_Y);
      myGLCD4.drawBitmap(red.resource_box_x + 6, red.resource_box_y + 6 + 14*w, 11, 14, Red_Wall_Y);
    }

  draw_base_corner('G');
  draw_base_corner('R');

  // Drawing the resource board
  myGLCD3.drawBitmap(green.resource_box_x + 5, green.resource_box_y + 20, 28, 20, Gold_Sprite);
  myGLCD4.drawBitmap(red.resource_box_x + 17 + 17, red.resource_box_y + 20, 28, 20, Gold_Sprite);
  myGLCD3.drawBitmap(green.resource_box_x + 35, green.resource_box_y + 18, 32, 22, Wood_Sprite);
  myGLCD4.drawBitmap(red.resource_box_x + 47 + 17, red.resource_box_y + 18, 32, 22, Wood_Sprite);
  myGLCD3.drawBitmap(green.resource_box_x + 70, green.resource_box_y + 18, 26, 22, Food_Sprite);
  myGLCD4.drawBitmap(red.resource_box_x + 82 + 17, red.resource_box_y + 18, 26, 22, Food_Sprite);
  myGLCD3.drawBitmap(green.resource_box_x + 2, green.resource_box_y + 41, 96, 24, Resource_Board);
  myGLCD4.drawBitmap(red.resource_box_x + 14 + 17, red.resource_box_y + 41, 96, 24, Resource_Board);

  // And then the unit symbols and resource location shapes
  myGLCD3.drawBitmap(green.resource_box_x + 2, green.resource_box_y + 68, 10, 21, Unit_Sprite);
  myGLCD4.drawBitmap(red.resource_box_x + 2 + 17, red.resource_box_y + 68, 10, 21, Unit_Sprite);
  myGLCD3.drawBitmap(green.resource_box_x + 68, green.resource_box_y + 68, 22, 21, Units_Sprite);
  myGLCD4.drawBitmap(red.resource_box_x + 68 + 17, red.resource_box_y + 68, 22, 21, Units_Sprite);

  myGLCD3.setColor(VGA_WHITE);
  myGLCD3.fillRect(green.resource_box_x + 100, green.resource_box_y + 46, green.resource_box_x + 109, green.resource_box_y + 47);
  myGLCD3.fillRect(green.resource_box_x + 104, green.resource_box_y + 42, green.resource_box_x + 105, green.resource_box_y + 51);

  myGLCD4.setColor(VGA_WHITE);
  myGLCD4.fillRect(red.resource_box_x + 2 + 17, red.resource_box_y + 46, red.resource_box_x + 11 + 17, red.resource_box_y + 47);
  myGLCD4.fillRect(red.resource_box_x + 6 + 17, red.resource_box_y + 42, red.resource_box_x + 7 + 17, red.resource_box_y + 51);

  for(int i = 0; i < 4; i++)
    {
      myGLCD3.drawCircle(green.resource_box_x + 104 + i%2, green.resource_box_y + 58 + i/2, 4);
      myGLCD4.drawCircle(red.resource_box_x + 6 + 17 + i%2, red.resource_box_y + 58 + i/2, 4);
    }

  myGLCD3.setColor(VGA_BLACK);
  myGLCD3.fillRect(green.resource_box_x + 104, green.resource_box_y + 46, green.resource_box_x + 105, green.resource_box_y + 47);
  myGLCD4.setColor(VGA_BLACK);
  myGLCD4.fillRect(red.resource_box_x + 6 + 17, red.resource_box_y + 46, red.resource_box_x + 7 + 17, red.resource_box_y + 47);
}

void draw_base_corner(char team)
{
  if(team == 'G')
    myGLCD3.drawBitmap(green.gate_x * tile_x_size, (green.gate_y * tile_y_size)%ScrYsize, 32, 30, Green_Corner);
  else if(team == 'R')
    myGLCD4.drawBitmap((red.gate_x * tile_x_size)%ScrXsize, (red.gate_y * tile_y_size)%ScrYsize, 32, 30, Red_Corner);
}
