from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Tank(GroundUnit):
    """
    A tank. Heavily armed, heavily armoured, and equipped with powerful
    treads.
    Armour: High
    Speed: Medium
    Range: Low
    Damage: High
    
    Other notes:
    - Too big to fit through a forest and too wide to fit through narrow
      mountain passes.
    - Its treads allow for a constant rate of movement over any terrain
      that it can pass.
    - Can't hit air units.
    """
    sprite = pygame.image.load("assets/tank.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Tank.sprite

        #load the base class
        super().__init__(**keywords)

        #sounds
        self.move_sound = "TankMove"
        self.hit_sound = "TankFire"

        #set unit specific things.
        self.type = "Tank"
        self.speed = 5
        self.max_atk_range = 2
        self.damage = 6
        self.defense = 3
        self.hit_effect = effects.Explosion
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        #Check superclass to see if it's passable first
        if not super().is_passable(tile, pos):
            return False

        #This unit can't pass these specific terrains
        if (tile.type == 'mountain' or
            tile.type == 'forest'):
            return False
        
        #The tile is passable
        return True
                                     
    def can_hit(self, target_unit):
        """
        Determines whether a unit can hit another unit.
        
        Overrides because tanks can't hit planes.
        """
        # If it's an air unit return false
        if isinstance(target_unit, unit.air_unit.AirUnit):
            return False
            
        # Not an air unit, return true
        return True

unit.unit_types["Tank"] = Tank
