from unit.base_unit import BaseUnit
import unit, helper
from tiles import Tile
import pygame

class ConstructionUnit(BaseUnit):
    """
    The basic building unit.
    
    - Only collides with other ground units
    - Gains bonuses (and debuffs) from tiles.
    """
    def __init__(self, **keywords):
        #load the base class
        super().__init__(**keywords)

        #set unit specific things.
        self.type = "Construction Unit"
        
 
    def can_hit(self, target_unit):
        """
        Determines whether a unit can hit another unit.
        """
        # If it's an air unit return false
        if isinstance(target_unit, unit.air_unit.AirUnit):
            return True
            
        # Can't hit anything
        return False


    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        # Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        return False

    def is_buildable(self, tile, pos):
        """
        Returns whether or not this unit can build another unit there.
        """
        # Check to see if it's a tile
        if not tile:
            return False

        #This unit can't build on these specific terrains
        if (tile.type == 'mountain' or
            tile.type == 'forest' or tile.type == 'water'):
            return False
        
        #The tile is buildable
        return True


