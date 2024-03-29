#include "tile.h"
#include "project.h"


void setup()
{
  Serial.begin(9600);

  /* Initialization */ 
  randomSeed(analogRead(7));

  pinMode(SEL,INPUT);
  digitalWrite(SEL,HIGH);
  pinMode(SEL_2,INPUT);
  digitalWrite(SEL_2,HIGH);
  pinMode(SEL_3,INPUT);
  digitalWrite(SEL_3,HIGH);
  pinMode(SEL_4,INPUT);
  digitalWrite(SEL_4,HIGH);

  JoyCenterY = analogRead(VERT);
  JoyCenterX = analogRead(HORIZ);
  JoyCenterY_2 = analogRead(VERT_2);
  JoyCenterX_2 = analogRead(HORIZ_2);
  
  current_JoyCenterX = JoyCenterX;
  current_JoyCenterY = JoyCenterY;

  tile_data = ht_new(tile_height);
  initialize_LCD();
  load_map(tile_data);
}

void loop()
{
  if(Serial.available() > 0) // When the python side sends something, initiate a turn change
    change_turns(tile_data);

  Move_Cursor(tile_data);
  check_button_press(tile_data);
  move_units(tile_data);
  gather_resources(tile_data);
  transfer_resources(tile_data);
}

void assign_names()
{  
  // Takes the name list, shuffles them around as a temporary copy of that list, and assigns
  // them to players as well as providing random sprites depending on their gender.
  

  // Preset list of names for units. It's ordered female then male since the random sprite assignment is depending on this order
  char unit_names[20][6] = {"Leah", "Sarah", "Tracy", "Julia", "Ava", "Alice", "Jill", "Megan", "Kyla", "Casey", // Ladies first
			    "Mike", "Walt", "Zack", "Jack", "Tyler", "Mack", "Smith", "Alex", "Jared", "Dan"};

  char temp_names[20][6];
  for(int i = 0; i < 20; i++)
    strcpy(temp_names[i], unit_names[i]);

  for(int i = 0; i < 600; i++) // Shuffle by doing random swaps a bunch of times
    {
      int swap_pos_1 = random(20);
      int swap_pos_2 = random(20);
      char temp_name[6];
      strcpy(temp_name, temp_names[swap_pos_1]);
      strcpy(temp_names[swap_pos_1], temp_names[swap_pos_2]);
      strcpy(temp_names[swap_pos_2], temp_name);
    }

  // Load names
  for(int i = 0; i < 20; i++)
    {
      unit temp_unit = { false, false, false, NULL, 0, 0, 0, 0, NULL, 0, 0 }; // Default info

      strcpy(temp_unit.name, temp_names[i]);
      for(int n = 0; n < 10; n++)
	{
	  if(!strcmp(temp_unit.name, unit_names[n]))
	    {
	      temp_unit.sprite = random(3); // Female
	      break;
	    }
	  else
	    temp_unit.sprite = random(3, 6); // Male
	}

      
      if(i<10)
	{
	  green.units[i] = temp_unit;
	  green.units[i].x_pos = green.gate_x; // Start off in the base
	  green.units[i].y_pos = green.gate_y;
	}
      else
	{
	  red.units[i-10] = temp_unit;
	  red.units[i-10].x_pos = red.gate_x;
	  red.units[i-10].y_pos = red.gate_y;
	}
    }
}

void draw_tile(hashtable *ht, byte x_pos, byte y_pos)
{ 
  /*
    This handles tile drawing by looking up the tile at x_pos, y_pos,
    and drawing the appropriate tile type. Because this function is
    called everytime something moves, and whenever a unit changes from 
    gathering <=> moving, most of the unit drawing has been replaced by 
    draw_tile().
  */

  if(x_pos == green.gate_x && y_pos == green.gate_y) // Special cases for the base corners
    draw_base_corner('G');
  else if(x_pos == red.gate_x && y_pos == red.gate_y)
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

      if(t->type != 'N')// Don't draw at 'N', aka the magenta tiles in the map convertor and the base.
	if(x_pos < tile_width/2 && y_pos < tile_height/2)
	  myGLCD.drawBitmap(x_pos*tile_x_size, y_pos*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
	else if(x_pos >= tile_width/2 && y_pos < tile_height/2)
	  myGLCD2.drawBitmap((x_pos - tile_width/2)*tile_x_size, y_pos*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
	else if(x_pos < tile_width/2 && y_pos >= tile_height/2)
	  myGLCD3.drawBitmap(x_pos*tile_x_size, (y_pos- tile_height/2)*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
	else if(x_pos >= tile_width/2 && y_pos >= tile_height/2)
	  myGLCD4.drawBitmap((x_pos - tile_width/2)*tile_x_size, (y_pos- tile_height/2)*tile_y_size, tile_x_size, tile_y_size, Sel_Tile);
    }

  for(int u = 0; u < 20; u++) // Check all units if they need to be redrawn
    {
      unit *sel_unit; 
      player *sel_player;

      if(u<10)
	{
	  sel_unit = &green.units[u];
	  sel_player = &green;
	}
      else
	{
	  sel_unit = &red.units[(u-10)];
	  sel_player = &red;
	}
		
      if(sel_unit->active == true && x_pos == sel_unit->x_pos && y_pos == sel_unit->y_pos)
	if(sel_unit->gathering == true)
	  draw_unit(ht, sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'B', sel_unit, sel_player->team);
	else
	  draw_unit(ht, sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'F', sel_unit, sel_player->team);
    }

  if(x_pos == CursorX && y_pos == CursorY) // After drawing the units, finish by checking if the cursor will be erased
    draw_cursor(x_pos, y_pos);
}

void print_txt_to_box(char message[], byte x_shift, byte y_shift, player *sel_player, unsigned long back_color)
{ 
  // Used for printing text to the proper player's box.
  // Both this and print_int_to_box have additional shifting 
  // to accomodate for the green base being a reflection of the red one.
  
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
  /*
    Properly prints integer values to either player's box. The back_color
    checks against gold, wood, and food_color check to see if there's
    a resource being printed to the resource board, and erases the 
    numbers properly to make room for new output.
  */

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
  // Setup the LCDs
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

int signof(int number) // Used in cursor and unit movement
{
  if(number < 0)
    return -1;
  else if(number > 0)
    return 1;
  return 0;
}

void load_map(hashtable *ht)
{
  /*
    Load in the map data into a hashtable and generate resources, draw those
    tiles, then draw the bases. Randomly shuffle and assign units, then draw 
    the starting units are drawn along with the cursor. Pointless information 
    is sent to the python side to let it know we're ready.
  */ 
  fill_tiles(ht, current_map, tile_width, tile_height);

  for(int y = 0; y < tile_height; y++)
    {
      for(int x = 0; x < tile_width; x++)
	{
	  draw_tile(ht, x, y);
	}
    }

  draw_bases();

  print_assets('R', 0, 'P', &red); // Reset player assets
  print_assets('R', 0, 'P', &green);
  draw_cursor(CursorX, CursorY);
  tile *t = tile_lookup(ht, CursorX, CursorY);
  update_cursor_assets(t->resource_type_1, t->resource_amount_1, t->resource_type_2, t->resource_amount_2);

 
  for(int i = 0; i < 3; i++) // Send to let the computer know we're ready to begin
    {
      Serial.print(0);
      Serial.print(" ");
    }
  Serial.print('\n');

  assign_names();

  green.units[0].active = true;
  red.units[0].active = true;

  print_unit_info(&green.units[0], &green);
  print_unit_info(&red.units[0], &red);
  draw_unit(ht, green.units[0].x_pos, green.units[0].y_pos,  green.units[0].sprite, 'F', &green.units[0], green.team);
  draw_unit(ht, red.units[0].x_pos, red.units[0].y_pos, red.units[0].sprite, 'F', &red.units[0], red.team);
}

void print_assets(char asset_type, int asset_amount, char cursor_or_player, player *sel_player)
{
  /*
    Prints a player's asset to their screen in the proper locations. Because the
    green.gate_x and y obtrudes on the regular resource icon location, green must
    move everything to the left and move it's base and cursor icons to the to the
    right hand side (see the .psd mockup in /assets to see what I mean). Also, the
    player'sassets are printed below the cursor assets so a y shift must occur.
  */

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
  else if(asset_type == 'R' && cursor_or_player == 'P') // reset
    {
      print_assets('G', sel_player->gold, cursor_or_player, sel_player);
      print_assets('W', sel_player->wood, cursor_or_player, sel_player);
      print_assets('F', sel_player->food, cursor_or_player, sel_player);
      print_assets('U', sel_player->num_units, cursor_or_player, sel_player);
    }
}

void update_cursor_assets(char asset_type_1, int asset_amount_1, char asset_type_2, int asset_amount_2, player *sel_player)
{
  /*
    Handles proper updating of resources. These checks of whether 
    both primary and secondary resources don't contain a resource type
    allows for proper 'deletion' of the resources that are not present
    when moving around on the map.
  */

  if(asset_type_1 != 'G' && asset_type_2 != 'G')
    print_assets('G', 0, 'C', sel_player);
  if(asset_type_1 != 'W' && asset_type_2 != 'W')
    print_assets('W', 0, 'C', sel_player);
  if(asset_type_1 != 'F' && asset_type_2 != 'F')
    print_assets('F', 0, 'C', sel_player);

  print_assets(asset_type_1, asset_amount_1, 'C', sel_player);
  print_assets(asset_type_2, asset_amount_2, 'C', sel_player);
}


void print_unit_info(unit *sel_unit, player *sel_player)
{
  // Used when switching between units to erase the last name 
  // (with a series of spaces) and print their name. Also, updates
  // the resources
  for(int space = 0; space < 6; space ++)
    print_txt_to_box(" ", 18 + (8*space), 65, sel_player, VGA_BLACK);
  print_txt_to_box(sel_unit->name, 18, 65, sel_player, VGA_BLACK);
  
  update_unit_resources(sel_unit->resource_type, 0, sel_unit, sel_player);
}


void update_unit_resources(char resource_type, int resource_amount, unit *sel_unit, player *sel_player)
{
  /*
    Update's a unit's resource amount.

    There are also variables being updated that currently have no use; the unit's gold, wood, and food total.
    These were supposed to factor into profficiency, but never got implemented. Nevertheless, there's no harm
    in updating them since that feature will inevitably be added.
  */
  sel_unit->resource_amount += resource_amount;

  print_unit_resources(resource_type, resource_amount, sel_unit, sel_player);
  
  if(resource_type == 'G')
    sel_unit->gold += resource_amount;
  else if(resource_type == 'W')
    sel_unit->wood += resource_amount;
  else if(resource_type == 'F')
    sel_unit->food += resource_amount;
}

void print_unit_resources(char resource_type, int resource_amount, unit *sel_unit, player *sel_player)
{
  // Prints the unit resources to the screen only when it's for the current_unit.
  if(sel_unit == current_unit)
    {
      char msg[2];
      
      if(resource_type == 'W')
	strcpy(msg, "W");
      else if(resource_type == 'G')
	strcpy(msg, "G");
      else if(resource_type == 'F')
	strcpy(msg, "F");
      else
	strcpy(msg, " ");

      print_txt_to_box(msg, 18, 76, sel_player, VGA_BLACK);

      print_txt_to_box("   ", 30, 76, sel_player, VGA_BLACK);
      if(sel_unit->resource_amount != 0)
	print_int_to_box(sel_unit->resource_amount, 30, 76, sel_player, VGA_BLACK);
    }  
}

void Move_Cursor(hashtable *ht)
{
  /*
    Detects movement of the current joystick (aka the current player),
    draws it one tile in the direction of movement, and erases the cursor
    from the last spot. draw_tile() handles proper drawing of objects on the
    tile so units done have to be redrawn from here.
  */
  
  int JoyVert = analogRead(current_VERT);
  int JoyHoriz = analogRead(current_HORIZ);

  if((abs(JoyVert - current_JoyCenterY) > OFFSET || abs(JoyHoriz - current_JoyCenterX) > OFFSET) && (millis() - cursor_last_move) > cursor_move_time)
    {
      // Moves CursorY up or down according to JoyVert
      if(abs(JoyVert - current_JoyCenterY) > OFFSET)
	{
	  CursorY += signof(JoyVert - current_JoyCenterY);
	  CursorY = constrain(CursorY, 0, tile_height - 1);
	}
  
      // Moves CursorX left or right according to JoyHoriz
      if(abs(JoyHoriz - current_JoyCenterX) > OFFSET)
	{
	  CursorX += signof(JoyHoriz - current_JoyCenterX);
	  CursorX = constrain(CursorX, 0, tile_width -1);
	}

      // These big detections handle the corners of the bases so a unit doesn't
      // accidentally move through it. Having that corner nook be the resource 
      // drop off area means there's literally quite a few different corner cases.
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

	  // Don't update these to the screen if they're just the same, it causes ugly and uneccesary flickering
	  if(((pt->resource_type_1 != t->resource_type_1 || pt->resource_amount_1 != t->resource_amount_1) ||
	      (pt->resource_type_2 != t->resource_type_2 || pt->resource_amount_2 != t->resource_amount_2)) &&
	     (pt->resource_amount_1 > 0 || t->resource_amount_1 > 0 || pt->resource_amount_2 > 0 || t->resource_amount_2 > 0))
	    update_cursor_assets(t->resource_type_1, t->resource_amount_1, t->resource_type_2, t->resource_amount_2);


	  // Draws new position of Cursor
	  draw_cursor(CursorX, CursorY);
	  prev_CursorX = CursorX;
	  prev_CursorY = CursorY;
	}
      cursor_last_move = millis();
    }
}

void draw_cursor(int x_pos, int y_pos)
{
  // Draws the cursor in a crosshair shape to the appropriate screen

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
  /*
    This checks all three types of button presses in this order:
    -Unit creation  --- select 1 & 2
    -Unit moving    --- select 1
    -Unit switching --- select 2
    
    Unit creation adds a unit to the current team and switches to it.
    By 'add' I mean turn active to 'true' since technically each team 
    already has all their units created from assign_names(). It first 
    looks for the currently selected unit, and then looks for the next 
    available unit from there to 'activate'.
    
    Unit moving looks at the tile the cursor is sitting on, checks if it's
    a valid destination, and sends the unit off if it is. Valid destinations
    include the unit's home-base and tiles with the same resource the unit has
    previously collected (only one resource type at a time). If this type
    is NULL from them already having dropped resources off, they're free to
    go to any tile with resources on it.

    Unit switching just looks for the next unit from current_unit and swaps control.


    Anytime a button is pressed, that button corresponding true/false bool
    gets turned true and prevents any other input reading until it detects
    the button has been released. Once released, the bool is turned false.
    The appropriate food is deducted and the unit is drawn.

    Only for unit swapping, there is a variable, 'last_pressed', that keeps
    track of when a unit was last swapped since there was an issue where
    the joystick select sensor would detect multiple clicks in a row sometimes.
  */

  static bool sel_pressed = false;
  static bool sel_2_pressed = false;
  static unsigned long last_pressed = 0;
  int select = digitalRead(current_SEL);
  int select_2 = digitalRead(current_SEL_2);
  
  if(sel_pressed == true)
    {
      select = digitalRead(current_SEL);
      if(select == HIGH)
	sel_pressed = false;
    }
  
  if(sel_2_pressed == true)
    {
      select_2 = digitalRead(current_SEL_2);
      if(select_2 == HIGH)
	sel_2_pressed = false;
    }
  
  if(select == LOW && select_2 == LOW && current_player->num_units < 10 && current_player->food >= unit_cost && sel_pressed == false && sel_2_pressed == false)
    {
      current_player->num_units ++;
      for(int u = 0; u < 10; u++)
	{
	  unit *sel_unit = &current_player->units[u];
	  if(sel_unit->active == true && sel_unit == current_unit)
	    {
	      for(int nu = 1; nu < 10; nu++) // 1-10 because the current unit need'nt be looked at
		{
		  unit *next_sel_unit = &current_player->units[(u+nu)%10];
		  if(next_sel_unit->active == false)
		    {
		      current_unit = next_sel_unit;
		      draw_tile(ht, sel_unit->x_pos, sel_unit->y_pos);
		      current_unit->active = true;
		      sel_pressed = true;
		      sel_2_pressed = true;
		      break;
		    }
		}
	      break;
	    }
	}
      // Deduct food, show this deduction on the screen, and show the new number of units.
      current_player->food -= unit_cost;
      print_assets('F', current_player->food, 'P');
      print_assets('U', current_player->num_units, 'P');
      draw_unit(ht, current_unit->x_pos, current_unit->y_pos, current_unit->sprite, 'F');
      print_unit_info();
    }

  if(select == LOW && sel_pressed == false)
    {
      if(current_unit->moving == false && current_unit->gathering == false)
	{
	  tile *t = tile_lookup(ht, CursorX, CursorY);

	  if((CursorX == current_player->gate_x && CursorY == current_player->gate_y && current_unit->resource_amount > 0) || 
	     ((t->resource_type_1 != NULL || t->resource_type_2 != NULL) && // Completely avoid tiles that never spawn resources
	      (current_unit->resource_type == t->resource_type_1 && t->resource_amount_1 > 0 || 
	       current_unit->resource_type == t->resource_type_2 && t->resource_amount_2 > 0) && current_unit->resource_amount < unit_resource_cap || 
	      current_unit->resource_type == NULL && (t->resource_amount_1 > 0 || t->resource_amount_2 > 0)))
	    {

	      // This assigns the unit's resource type if they don't have a type,
	      // favoring the primary resource over the secondary one.
	      if(t->resource_amount_1 > 0 && current_unit->resource_type == NULL)
		{
		  current_unit->resource_type = t->resource_type_1;
		}
	      else if(t->resource_amount_2 > 0 && current_unit->resource_type == NULL)
		{
		  current_unit->resource_type = t->resource_type_2;
		}

	      current_unit->moving = true;
	      current_unit->x_dest = CursorX;
	      current_unit->y_dest = CursorY;
	      current_unit->move_speed = (current_unit->resource_amount*2) + get_speed_info(ht, current_unit->x_pos, current_unit->y_pos);
	      current_unit->depart_time = millis();
	      sel_pressed = true;
	    }
	}
    }

  if(select_2 == LOW && current_player->num_units > 1 && sel_2_pressed == false && millis() - last_pressed > 300)
    {
      for(int u = 0; u < 10; u++)
	{
	  unit *sel_unit = &current_player->units[u];
	  if(sel_unit->active == true && sel_unit == current_unit)
	    {
	      for(int nu = 1; nu < 10; nu++)
		{
		  unit *next_sel_unit = &current_player->units[(u+nu)%10];
		  if(next_sel_unit->active == true)
		    {
		      current_unit = next_sel_unit;
		      draw_tile(ht, sel_unit->x_pos, sel_unit->y_pos);
		      draw_tile(ht, current_unit->x_pos, current_unit->y_pos);
		      print_unit_info(); // Print the information of the new unit
		      sel_2_pressed = true;
		      last_pressed = millis();
		      break;
		    }
		}
	      break;
	    }
	}
    }
}

void draw_unit(hashtable *ht, int x_pos, int y_pos, byte sprite, char front_back, unit *sel_unit, char team[])
{
  /*
    Will determine if a unit needs to be drawn forward facing or backwards,
    or if they're on the water. If they need to be drawn as anything other
    than a canoe, it then looks to see which sprite it needs. 

    The width of the image needs to be changed depending on what sprite
    is being used, so sprite_width controls that.
    
    The shadow color draws a rough outline if it's anything other than -2 
    (see the UTFT change). This distinguishes red and green units from 
    one-another, as well as the currently selected unit from others.
    It also makes the sprites easier to see on some tiles.
  */
  prog_uint16_t *Sprite;
  
  int new_x_pos = x_pos * tile_x_size + 4;
  int new_y_pos = y_pos * tile_y_size + 1;

  int sprite_width;
  int sprite_height = 28;

  tile *t = tile_lookup(ht, x_pos, y_pos);
  if(t->type == 'H')
    {
      Sprite = Canoe;
      sprite_width = 20;
    }
  else if(front_back == 'F')
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

  long shadow_color = VGA_WHITE;
  if(sel_unit != current_unit)
    {
      if(!strcmp(team, "GREEN"))
	shadow_color = VGA_LIME;
      else if(!strcmp(team, "RED"))
	shadow_color = VGA_RED;
    }
    
  // Checking which screen to draw to
  if(x_pos < tile_width/2 && y_pos < tile_height/2)
    myGLCD.drawBitmap(new_x_pos, new_y_pos, sprite_width, sprite_height, Sprite, 1, trans_color, shadow_color);
  else if(x_pos >= tile_width/2 && y_pos < tile_height/2)
    myGLCD2.drawBitmap(new_x_pos - (tile_width/2)*tile_x_size, new_y_pos, sprite_width, sprite_height, Sprite, 1, trans_color, shadow_color);
  else if(x_pos < tile_width/2 && y_pos >= tile_height/2)
    myGLCD3.drawBitmap(new_x_pos, new_y_pos - (tile_height/2)*tile_y_size, sprite_width, sprite_height, Sprite, 1, trans_color, shadow_color);
  else if(x_pos >= tile_width/2 && y_pos >= tile_height/2)
    myGLCD4.drawBitmap(new_x_pos - (tile_width/2)*tile_x_size, new_y_pos - (tile_height/2)*tile_y_size, sprite_width, sprite_height, Sprite, 1, trans_color, shadow_color);
  
  if(x_pos == CursorX && y_pos == CursorY)
    draw_cursor(x_pos, y_pos); // Draw the cursor in front of the unit if they occupy the same tile
}

void move_units(hashtable *ht, player *sel_player)
{
  /*
    Looks through all active units on sel_player's team to find out who's active and moving.
    If they are moving, it then moves on to see if they've arrived at their destination and if
    an adequate amount of time has passed since they moved last. Once it's determined they can
    move, it takes note of what their x and y positions are so it knows where to draw their 
    last tile once they move on to a new tile.

    The moving system was supposed to incorporate some sort of Djikstra's graph associated 
    with the time it takes to traverse each tile type, but as stated in 'tile.cpp', the
    times made almost no difference right now because the python side finishes much
    quicker than we had anticipated. So, instead units just moves on angles towards their
    destination until they arrive or get a straight path and need to move along the x or y
    axis only. The move speed is also affected by the amount of resources being carried
    by the unit, naturally slowing them as they have more to carry. Once they arive, 
    it's gathering time so 'gathering' is set to true, and 'moving' is set to false.
    Also, 'draw_tile' makes sure they're turned around to look like they're busy gathering.
  */
  for(int u = 0; u < 10; u++)
    {
      unit *sel_unit = &sel_player->units[u];
      if(sel_unit->active == true && sel_unit->moving == true)
	{
	  if(sel_unit->x_pos != sel_unit->x_dest || sel_unit->y_pos != sel_unit->y_dest)
	    {
	      if(millis() - sel_unit->depart_time > sel_unit->move_speed)
		{
		  int prev_x_pos = sel_unit->x_pos;
		  int prev_y_pos = sel_unit->y_pos;
		  if(!(sel_unit->y_pos == 12 && (sel_unit->x_pos < 2 || sel_unit->x_pos > 17) && signof(sel_unit->y_dest - sel_unit->y_pos) == 1))
		    sel_unit->y_pos += signof(sel_unit->y_dest - sel_unit->y_pos);
		  
		  if(!(sel_unit->y_pos > 13 && ((sel_unit->x_pos == 4 && signof(sel_unit->x_dest - sel_unit->x_pos) == -1) ||
						(sel_unit->x_pos == 15 && signof(sel_unit->x_dest - sel_unit->x_pos) == 1))))
		    sel_unit->x_pos += signof(sel_unit->x_dest - sel_unit->x_pos);

		  draw_tile(ht, prev_x_pos, prev_y_pos);
		  draw_unit(ht, sel_unit->x_pos, sel_unit->y_pos, sel_unit->sprite, 'F', sel_unit);

		  sel_unit->move_speed = (sel_unit->resource_amount*2) + get_speed_info(ht, sel_unit->x_pos, sel_unit->y_pos);
		  sel_unit->depart_time = millis();
		}
	    }
	  else
	    {
	      sel_unit->moving = false;
	      sel_unit->gathering = true;
	      sel_unit->gather_time = millis();
	      draw_tile(ht, sel_unit->x_pos, sel_unit->y_pos);
	    }
	}
    }
}

void gather_resources(hashtable *ht, player *sel_player)
{
  /*
    Looks through all active units on the sel_player's team to see if anybody is gathering resources.
    If they are, it checks that they haven't gone over the allowed limit for resources to carry at once,
    and that they haven't depleted a tile of it's resources. If this is all ok, it will then see if
    the unit hasn't gathered for a while and can gather again.

    There are then checks in place to ensure a tile's resources don't deplete past zero. This would be 
    really problematic because the resource amount is stored as Bytes so a negative value just rolls
    back over to 255 and counts down from there. Also, there are checks to make sure what a unit is gaining 
    doesn't push them past their resource limit. Basically, it syncs it properly so the unit gains what the 
    tile loses. Every time it gathers, the time is updated so it knows not to allow them to gather for a 
    little bit, and updates what they've gotten onto the screen.
    
    If they have finished, the 'gathering' bool is set to false and they are redrawn in a forward facing position.

    The check against the unit's gate makes sure it isn't trying to look at resources while a unit is transfering
    them, since the 'gathering' bool is used in both gathering and transfering.
  */

  for(int u = 0; u < 10; u++)
    {
      unit *sel_unit = &sel_player->units[u];
      if(sel_unit->active == true && sel_unit->gathering == true && (sel_unit->x_dest != sel_player->gate_x || sel_unit->y_dest != sel_player->gate_y))
	{
	  tile *t = tile_lookup(ht, sel_unit->x_pos, sel_unit->y_pos);
	  if(((sel_unit->resource_type == t->resource_type_1 && t->resource_amount_1 > 0) || 
	      (sel_unit->resource_type == t->resource_type_2 && t->resource_amount_2 > 0)) &&
	     sel_unit->resource_amount < unit_resource_cap)
	    {
	      if(millis() - sel_unit->gather_time > tile_gather_time)
		{
		  byte resource_gain = 5;


		  if(sel_unit->resource_type == t->resource_type_1)
		    {
		      if(t->resource_amount_1 - resource_gain < 0)
			resource_gain = t->resource_amount_1;
		      if(sel_unit->resource_amount + resource_gain > unit_resource_cap)
			resource_gain = unit_resource_cap - sel_unit->resource_amount;
		      
		      t->resource_amount_1 -= resource_gain;
		    }
		  else if(sel_unit->resource_type == t->resource_type_2)
		    {
		      if(t->resource_amount_2 - resource_gain < 0)
			resource_gain = t->resource_amount_2;
		      if(sel_unit->resource_amount + resource_gain > unit_resource_cap)
			resource_gain = unit_resource_cap - sel_unit->resource_amount;
		      
		      t->resource_amount_2 -= resource_gain;
		    }

		  // Print the unit's resources as they gather.
		  update_unit_resources(sel_unit->resource_type, resource_gain, sel_unit, sel_player);

		  // If the cursor is looking at the tile being mined, it will also print the tile being depleted
		  if(sel_unit->x_pos == CursorX && sel_unit->y_pos == CursorY)
		    update_cursor_assets(t->resource_type_1, t->resource_amount_1, t->resource_type_2, t->resource_amount_2);		  

		  sel_unit->gather_time = millis();
		}
	    }
	  else
	    {
	      sel_unit->gathering = false;
	      draw_tile(ht, sel_unit->x_pos, sel_unit->y_pos);
	    }
	}
    }
}

void transfer_resources(hashtable *ht, player *sel_player)
{
  /*
    Similar to gather_resources(), but instead of gathering, it transfers this to the total amount gathered so far.
    They drop resources off at the same rate they collect them in gather_resources(). The loop of checking the 
    available active units means multiple units can do drop-offs at the same time. The unit must be on the 'gate' 
    tile to transfer, so this works by just clicking home as if you would send out for a resource.
    The total at the base is updated with every resource drop, and the unit's amount is depleted as well.
    Once all resources have been dropped off, the 'gathering' bool is set to false and their resource type
    is set to NULL so they can go out for whatever they want

    Don't get this confused with the resources being sent at the end of the turn; this is just transfering back to 
    the local base so the unit becomes free to gather a different type of resource (and so that if the turn gets 
    ended on the python end, the player's teammate will recieve resources).
  */

  for(int u = 0; u < 10; u++)
    {
      unit *sel_unit = &sel_player->units[u];

      if(sel_unit->active == true && sel_unit->gathering == true && 
	 sel_unit->x_pos == sel_player->gate_x && sel_unit->y_pos == sel_player->gate_y)
	{
	  if(sel_unit->resource_amount > 0)
	    {
	      if(millis() - sel_unit->gather_time > tile_gather_time)
		{
		  byte resource_move = 5;

		  if(sel_unit->resource_amount - resource_move < 0)
		    resource_move = sel_unit->resource_amount;
		      
		  if(sel_unit->resource_type == 'G')
		    {
		      sel_player->gold += resource_move;
		      print_assets('G', sel_player->gold, 'P', sel_player);
		    }
		  if(sel_unit->resource_type == 'W')
		    {
		      sel_player->wood += resource_move;
		      print_assets('W', sel_player->wood, 'P', sel_player);
		    }
		  if(sel_unit->resource_type == 'F')
		    {
		      sel_player->food += resource_move;
		      print_assets('F', sel_player->food, 'P', sel_player);
		    }


		  update_unit_resources(sel_unit->resource_type, (resource_move * -1), sel_unit, sel_player);
		  sel_unit->gather_time = millis();
		}
	    }
	  else
	    {
	      sel_unit->gathering = false;
	      sel_unit->resource_type = NULL;
	      update_unit_resources(sel_unit->resource_type, 0, sel_unit, sel_player);
	      draw_tile(ht, sel_unit->x_pos, sel_unit->y_pos);
	    }
	}
    }
}

void draw_bases()
{
  // This function's purpose is to draw the base. Checkout the .psd mockup in the /Assets folder to see
  // what it looks like complete! A lot of drawing, but it cuts down on the upload time vs drawing one
  // big image. The water that's drawn right away is just for looks, because it can't spawn resources.

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

  myGLCD3.setColor(VGA_WHITE); // Plus represents crosshairs of the cursor
  myGLCD3.fillRect(green.resource_box_x + 100, green.resource_box_y + 46, green.resource_box_x + 109, green.resource_box_y + 47);
  myGLCD3.fillRect(green.resource_box_x + 104, green.resource_box_y + 42, green.resource_box_x + 105, green.resource_box_y + 51);

  myGLCD4.setColor(VGA_WHITE);
  myGLCD4.fillRect(red.resource_box_x + 2 + 17, red.resource_box_y + 46, red.resource_box_x + 11 + 17, red.resource_box_y + 47);
  myGLCD4.fillRect(red.resource_box_x + 6 + 17, red.resource_box_y + 42, red.resource_box_x + 7 + 17, red.resource_box_y + 51);

  for(int i = 0; i < 4; i++) // Circle represents the total number of resources
    {
      myGLCD3.drawCircle(green.resource_box_x + 104 + i%2, green.resource_box_y + 58 + i/2, 4);
      myGLCD4.drawCircle(red.resource_box_x + 6 + 17 + i%2, red.resource_box_y + 58 + i/2, 4);
    }

  myGLCD3.setColor(VGA_BLACK); // Black center of the crosshairs
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

void change_turns(hashtable *ht, player *sel_player)
{
  // Function handles the convention for switching players and sending resources.

  Serial.read(); // Gets rid of the byte the python end sent

  int a[] = { sel_player->gold, sel_player->wood, sel_player->food };

  for(int i = 0; i < 3; i++)
    {
      Serial.print(a[i]); // Send the python end resources collected
      Serial.print(" ");
    }
  Serial.print('\n'); // '\n' tells the python end I've sent it all

  sel_player->gold = 0; // Reset the arduino player's resources back down to zero
  sel_player->wood = 0;
  sel_player->food = 0;

  print_assets('R', 0, 'P', sel_player); // Now tell the screen the resources have been sent


  char team[10]; // These variables are in place to handle an issue where the color of the selected unit would not change properly
  unit *temp_unit = current_unit;


  if(!strcmp(sel_player->team, "GREEN")) // Was green's turn, now red's
    {
      strcpy(team, "GREEN");
      current_player = &red;
      current_VERT = VERT;
      current_HORIZ = HORIZ;
      current_SEL = SEL;
      current_SEL_2 = SEL_2;
      current_JoyCenterX = JoyCenterX;
      current_JoyCenterY = JoyCenterY;
    }
  else if(!strcmp(sel_player->team, "RED")) // vice-versa
    {
      strcpy(team, "RED");
      current_player = &green;
      current_VERT = VERT_2;
      current_HORIZ = HORIZ_2;
      current_SEL = SEL_3;
      current_SEL_2 = SEL_4;
      current_JoyCenterX = JoyCenterX_2;
      current_JoyCenterY = JoyCenterY_2;
    }

  for(int u = 0; u < 10; u++)
    {
      // Finds the first active unit. Right now, it will always grab the first one, but if
      // units were allowed to be damaged/killed, it might potentially need to find someone else
      unit *sel_unit = &current_player->units[u];
      if(sel_unit->active == true)
	{
	  current_unit = sel_unit;
	  draw_tile(ht, current_unit->x_pos, current_unit->y_pos);

	  if(temp_unit->gathering == true)
	    draw_unit(ht, temp_unit->x_pos, temp_unit->y_pos, temp_unit->sprite, 'B', temp_unit, team);
	  else
	    draw_unit(ht, temp_unit->x_pos, temp_unit->y_pos, temp_unit->sprite, 'F', temp_unit, team);
	  break;
	}
    }
}
