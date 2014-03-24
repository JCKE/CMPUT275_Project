from unit.base_unit import BaseUnit
from unit.ground_unit import GroundUnit
import unit, helper
from tiles import Tile
import pygame

class ImmobileUnit(BaseUnit):
    """
    The basic immovable unit.
    
    - Collides with everything and cannot pass over
      any tile and is therefore unable to move.
    - Not allowed to place units beyond certain radius
      of "base" unit.
    """
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Immobile Unit"
        
    def is_passable(self, tile, pos):
        """
        Returns that unit cannot move over any tiles or nothing can move through it.
        """
        # Return default
        if not super().is_passable(tile, pos):
            return False
            
        # We can't pass through enemy units.
        u = BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team and isinstance(u, GroundUnit):
            return False
        
        #ground units can't travel over water or through walls

        return False
