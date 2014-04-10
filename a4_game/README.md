Tactics 2
=======

The original tactics game is a tactics game battle system along the lines of 
Advance Wars or Fire Emblem. Programmed Elliot Colp and Braedy Kuzma.

Tactics 2 extends their original work to add an extra demension to the 
gameplay to include the Arduino and three other players.
Tactics 2 is programmed by Jesse Emery and Steven Cherfan.

Installing/Running
------------------

This engine is built in Python 3 using Pygame. To install Pygame for Python 3
(assuming you're using Ubuntu), see these instructions:
http://www.pygame.org/wiki/CompileUbuntu

To use the Ardunio side of the game PySerial is required to be installed.
Documentation at: http://pyserial.sourceforge.net/

To run the game, do

    python3 main.py -s <serial_port>
    or
    python3 main.py -d # to debug
    or
    python3 main.py -m <map> -s <serial_port>

where _map_ is the name of one of the maps in the maps directory (minus 
the ".lvl" extension).

Gameplay
--------

By default, there are two team: red and green. The goal of the game is 
destroy all of the other team's units.


The game starts out with two starting flags, one for each team. At the start
of your turn you left click on your team's start flag in which case it will be
highlighted in yellow. On the left hand side of the screen the **FACTORY** button
will be highlighted, you are then entering **BUILD** mode. The yellow radius of 
squares surounding your start flag are all the eligible squares you can build your
Factory, choose your spot wisely. The turn will not end until you have built your 
Factory. The mechanic of clicking a button and a yellow radii of squares surrounding
your base also applys for building other units, see below.

Once you have a unit built, left click on a unit to select it and
enter **MOVE** mode, also clicking the **MOVE** button will have you enter this
mode. It will be highlighted in yellow and all reachable tiles will glow blue.
Left click on one of these tiles, and the selected unit will move to it. 
To cancel movement, left click on either the **MOVE** button or your selected unit.

If you right click on  your unit or left click on the **ATTACK** button, 
all tiles in range will glow red. As well, any units which are available 
to attack will be marked with a blinking targeting reticle.
Left click on any such unit and your selected unit will attack it. 
To cancel your attack, click again on either the **ATTACK** button or 
click either mouse button on your selected unit.

Each turn, you may move each of your units once and attack with each of your 
units once. You can also choose to build units and bases at the cost of 
resources during your turn. Pressing the **d** button will allow you to
sell a unit and recieve half of the original price. 
When you are done, press the **END TURN** button or press enter/return
to let the other team take its turn. In some cases, such as with air units, 
the unit must be moved before you can end your turn. In this case, 
pressing the **END TURN** button will automatically select the unit if 
it has not yet been moved.


Every unit type has different uses. See the documentation strings in the 
units directory for more information.

The GUI
-------

On the bottom-right of each unit's tile, its health is displayed. When this 
reaches 0, it will explode. For aircraft, a bar indicating its remaining 
fuel is also displayed in the top-left of its tile. Similarly, when this 
reaches 0, the unit will crash.

The panel on the right side of the screen also displays useful information 
about the selected unit, the unit your mouse is hovering over, and/or the 
tile your mouse is hovering over, depending on which are applicable.

Note that all distances are measured in Manhattan distance using units of 
tiles.

The following stats are displayed for units:

- **Type**: the name of the unit type
- **Speed**: the maximum distance that the unit can move in one turn, assuming
  the cost of every tile is minimal
- **Range**: the maximum range of the unit's attack
- **Attack**: the maximum damage the unit can do to an enemy unit, assuming the
  other unit has no defense
- **Defense**: the amount of damage this unit can block
- **Fuel**: for aircraft, the number of turns worth of fuel remaining
- **Has Moved**: if the unit is on the current player's team, this displays
  whether the unit has been moved this turn
- **Has Attacked**: if the unit is on the current player's team, this displays
  whether the unit has attacked this turn
- **Potential Damage**: if the unit is not on the current player's team and
  there is currently a selected unit, this displays how much damage the selected
  unit could do to the other unit taking into account its defense and tile
  defense bonus

The following stats are displayed for tiles:

- **Type**: the type of terrain in the tile
- **Coordinates**: (x, y) coordinates of the tile, in units of tiles
- **Defense**: the bonus to defense provided by this tile to any unit sitting on
  it
- **Range**: the bonus to range provided by this tile to any unit sitting on it
- **Passable**: if a unit is selected, this displays whether or not the selected
  unit can pass through this tile
- **Movement Cost**: if a unit is selected and the unit can pass through this
  tile, this is how much movement it takes for the unit to cross the tile. For
  instance, if the tile's cost is 2 and the unit's speed is 8, it can only cross
  through 4 such tiles.

**NOTE**: tile bonuses do not apply to aircraft!

On the left are buttons for building units and displays resource information.

In the top, left corner:
- **RESOURCES**: your team's total gold, wood and food resources
- **COST**: when hovering over an appropriate unit it shows how many resources
  it requires to build it

The buttons will be activated only when the approperiate base is selected. 
Left clicking the highlighted buttons after a certain base is selected will allow 
you to build provided you have resources.
The bases are:
- Factory: main base where you can build ground units and other bases from it. No cost.
- Airstrip: allows you to build and refuel air units. Not free to build.
- Shipyard: allows you to build water units. Not free to build. Must be built on a sand tile.
- Unit buttons: The rest of the buttons are for building the various units

Sound Credits
-------------
All sounds are from FreeSound.org, released under public domain/Creative Commons
licenses. As such, they are free to use in this project assuming credit is
provided.

**Tank fire**
http://www.freesound.org/people/Cyberkineticfilms/sounds/127845/

**Tank engine**
http://www.freesound.org/people/Sempoo/sounds/125213/

**Engine start**
http://www.freesound.org/people/snakebarney/sounds/138099/

**Jeep engine**
http://www.freesound.org/people/qubodup/sounds/160357/

**Machine gun**
http://www.freesound.org/people/CGEffex/sounds/101961/

**Anti-armour launch**
http://www.freesound.org/people/qubodup/sounds/182794/

**Generic explosion**
http://www.freesound.org/people/sarge4267/sounds/102734/

**Airplane move**
http://www.freesound.org/people/FreqMan/sounds/135495/

**Anti-armour move**
http://www.freesound.org/people/mattbronka/sounds/48048/

**Boat move**
http://www.freesound.org/people/inchadney/sounds/111395/

**Artillery fire**
http://www.freesound.org/people/qubodup/sounds/184365/

**Bomb drop**
http://www.freesound.org/people/club%20sound/sounds/104551/
