from unit.water_unit import WaterUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Battleship(WaterUnit):
    """
    An armoured battleship. Basically, the tank of the ocean. Excels at
    attacking other naval units as well as anything along the coast.
    
    Armour: High
    Speed: High
    Range: High
    Damage: High
    
    Other notes:
    - Despite its high stats, this unit is constrained to the water, so its
      uses are fairly specialized.
    """
    sprite = pygame.image.load("assets/battleship.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Battleship.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.hit_sound = "ArtilleryFire"

        #set unit specific things.
        self.type = "Battleship"
        self.speed = 8
        self.max_atk_range = 4
        self.damage = 6
        self.defense = 3
        self.hit_effect = effects.Explosion

unit.unit_types["Battleship"] = Battleship
