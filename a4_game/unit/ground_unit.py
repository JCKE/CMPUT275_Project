from unit.base_unit import BaseUnit
import unit, helper
from tiles import Tile
import pygame

class GroundUnit(BaseUnit):
    """
    The basic ground-moving unit.
    
    - Only collides with other ground units
    - Gains bonuses (and debuffs) from tiles.
    """
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Ground Unit"
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        # Return default
        if not super().is_passable(tile, pos):
            return False
            
        # We can't pass through enemy units.
        u = BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team and isinstance(u, GroundUnit):
            return False
        
        #ground units can't travel over water or through walls
        if (tile.type == 'water' or tile.type == 'wall'):
            return False

        return True

