from unit.ground_unit import GroundUnit
import unit, helper, effects
from tiles import Tile
import pygame

class AntiArmour(GroundUnit):
    """
    An infantry unit armed with an anti-armour missile launcher. Very 
    effective against tanks and battleships, but otherwise not especially
    powerful.
    
    Armour: None
    Speed: Low
    Range: Medium
    Damage: Medium (High against armoured vehicles)
    
    Other notes:
    - Slightly slowed by forests and sand.
    - Slowed somewhat more by mountains.
    - Can move through any land terrain.
    - Can't hit air units.
    """
    sprite = pygame.image.load("assets/anti_armour.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = AntiArmour.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.move_sound = "FeetMove"
        self.hit_sound = "RocketLaunch"

        #set unit specific things.
        self.type = "Anti-Armour"
        self.speed = 4
        self.max_atk_range = 3
        self.damage = 4
        self.bonus_damage = 4
        self.defense = 0
        self.hit_effect = effects.Explosion
        
        self._move_costs = {'mountain': 2,
                             'forest': 1.5,
                             'sand': 1.5}
                             
    def can_hit(self, target_unit):
        """
        Determines whether a unit can hit another unit.
        
        Overrides because anti-armour can't hit planes.
        """
        # If it's an air unit return false
        if isinstance(target_unit, unit.air_unit.AirUnit):
            return False
            
        # Not an air unit, return true
        return True
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        
        This overrides the super class function for special damage
        and because anti-armour can't hit air units.
        """        
        # Do bonus damage to armored vehicles
        if target.type == "Tank" or target.type == "Battleship":
            # Calculate the total damage
            damage = self.damage + self.bonus_damage
            
            # Calculate the unit's defense
            defense = target.get_defense(tile = target_tile)
            
            # Don't do negative damage
            if (damage - defense < 0):
                return 0
            
            return damage - defense
            
        else:
            return super().get_damage(target, target_tile)

unit.unit_types["Anti-Armour"] = AntiArmour
