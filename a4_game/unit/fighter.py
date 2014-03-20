from unit.air_unit import AirUnit
import unit, helper, effects
from tiles import Tile
import pygame

class Fighter(AirUnit):
    """
    A fighter jet. Moves fast, but needs to refuel constantly. Good at peppering
    the ground with shots as well as eliminating other air units.
    
    Armour: High
    Speed: Very High
    Range: Medium
    Damage: Medium
    Fuel: Low
    
    Other notes:
    - In order to maintain its high speed, the fighter has fairly low fuel.
      Make well-planned strafing runs and be sure you can get back to a carrier
      in time!
    - When firing at another air unit, this unit does extra damage.
    """
    sprite = pygame.image.load("assets/fighter.png")
    
    def __init__(self, **keywords):
        #load the image for the base class.
        self._base_image = Fighter.sprite

        #load the base class
        super().__init__(**keywords)
        
        #sounds
        self.hit_sound = "MachineGunFire"

        #set unit specific things.
        self.type = "Fighter"
        self.speed = 16
        self.max_atk_range = 4
        self.damage = 5
        self.defense = 3
        self.bonus_damage = 2
        self.max_fuel = 7
        self.set_fuel(self.max_fuel)
        self.min_move_distance = 6
        self.hit_effect = effects.Ricochet
        
    def get_damage(self, target, target_tile):
        """
        Returns the potential attack damage against a given enemy.
        
        This overrides the super class function to allow
        special damage effects.
        """
        # Do bonus damage to other air units
        if isinstance(target, unit.air_unit.AirUnit):
            # Calculate the total damage
            damage = self.damage + self.bonus_damage
            
            # Get the unit's current defense
            defense = target.get_defense(tile = target_tile)
            
            # Don't do negative damage
            if (damage - defense < 0):
                return 0
            
            return damage - defense
        else: return super().get_damage(target, target_tile)

unit.unit_types["Fighter"] = Fighter
