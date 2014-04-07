CMPUT275_Project
================

Our final project for CMPUT 275.

Tactics 2
For our final project we propose working on a heavily modified version of the Tactics game from Assignment 4.
This version will employ the original code and concepts, but build off of it significantly in many different ways. 

Our version will be 4-players, with 2 teams of 2. One player on each team opperates from the Arduino side, and the other 2 players opperate from the PyGame side. The idea is that the PyGame players will fight as per usual, but only start with a small number of units. To make more, they must use resources; this is where the Arduino side comes into play. The Arduino players will do the resource collecting on a separate map. What makes this concept interesting is that while it is one team's turn on the PyGame side, it is the opposite team's turn on the Arduino side. Once a PyGame player ends their turn, whatever resources were collected by the opposing player will be sent to that player's team mate. This means the PyGame player must finish his moves as fast as possible and hit 'End Turn' before his opponent on the Arduino side can collect a lot of resources. To keep it from getting stale, the players could swap roles with their team mate every once in a while.

Changes on the PyGame side include:
- Adding a 'create units' side panel
- Making a 'home base' where the units created will spawn
- Communication to the Arduino client and a resource exchange system between turns
- Create two other home base types: one builds water units and the other air units while the home base will build land units
- If time permits, make turret style base defenses and other unit types

To accomplish our project, we would need to borrow a larger LCD screen like one of the touch screens for the Arduino players to play on. We may end up using touch functionality too depending on how far we get.


Milestones:

Mouse shortcuts on pc side, click on tile to move, on enemy to attack
Create units via resources instead of prespawned ones
Add farmable resources, new unit types
balance

Milestones:

1. Arduino side players will be able to move around a map on the LCD screen and play the resource side-game
2. On the python side, make changes to Tactics so that it can interact with the Arduino. Eg: add resources to the game, etc.
3. Work on balancing the game and making sure that the Arduino and Tactics properly transfer data and work together.
