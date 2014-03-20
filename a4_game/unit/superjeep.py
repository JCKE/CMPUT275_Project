from unit.jeep import Jeep
import unit, helper, effects
from tiles import Tile
import pygame

class SuperJeep(Jeep):
    """
    A jeep with at least four different nitrous engines. Engineers said it
    couldn't be done; the Healthy and Safety council said it shouldn't be done;
    the military's economist said it couldn't be afforded. The last two were
    probably right, and yet here we are with a jeep that moves at a a thousand
    miles per hour.
    
    Armour: Low
    Speed: Ridiculously High
    Range: Low
    Damage: Medium
    
    Other notes:
    - Used for testing pathfinding.
    """
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Incredibly Fast Jeep"
        self.speed = 100

unit.unit_types["SuperJeep"] = SuperJeep
