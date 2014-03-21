from unit.base_unit import BaseUnit
import unit, helper
from tiles import Tile
import pygame

class WaterUnit(BaseUnit):
    """
    A unit which moves through water rather than land.
    
    - Only collides with other water units.
    """
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Water Unit"
        
        #All water units have the same movement sound
        self.move_sound = "BoatMove"
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        # Return default
        if not super().is_passable(tile, pos):
            return False
                    
        # We can't pass through enemy units.
        u = BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team and isinstance(u, WaterUnit):
            return False
        
        #ground units can't travel over water.
        if (tile.type != 'water'):
            return False

        return True
