from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Jeep(GroundUnit):
    """
    A jeep. Lightly armored and armed, but fast.
    
    Armour: Low
    Speed: High
    Range: Low
    Damage: Medium
    
    Other notes:
    - Can move through any land terrain.
    - The jeep's wheels are designed for travel on a road, so moving through any
      other terrain type will decrease its speed. Forests and mountains are
      especially difficult to traverse.
    """
    sprite = pygame.image.load("assets/jeep.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Jeep.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.move_sound = "JeepMove"
        self.hit_sound = "MachineGunFire"

        #set unit specific things.
        self.type = "Jeep"
        self.speed = 10
        self.max_atk_range = 2
        self.damage = 5
        self.defense = 1
        self.hit_effect = effects.Ricochet
        
        self._move_costs = {'plains': 2,
                             'sand': 3,
                             'forest': 3,
                             'road': 1,
                             'mountain': 4}

unit.unit_types["Jeep"] = Jeep
