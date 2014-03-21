from unit.base_unit import BaseUnit
from unit.carrier import Carrier
import unit, helper
from tiles import Tile
import pygame

# Layer of air units
AIR_LAYER = 5

# Rectangle for fuel indicator
FUEL_RECT = pygame.Rect(1, 1, 8, 5)

# Percentage of fuel remaining before the indicator changes colour

# Indicator colours
FUEL_BAD_CUTOFF = 1
FUEL_BACK_COLOUR = (0, 0, 0, 255)
FUEL_BACK_COLOUR_BAD = (255, 0, 0, 255)
FUEL_FILL_COLOUR = (0, 180, 0, 255)
FUEL_FILL_COLOUR_HALF = (180, 255, 0, 255)

class AirUnit(BaseUnit):
    """
    The basic air-moving unit.
    
    - Must move a minimum distance every turn unless docked at a carrier
    - Gradually runs out of fuel unless docked at a carrier
    - When fuel reaches 0, the unit will die
    - Only collides with other air units
    - Does not get tile bonuses
    """
    def __init__(self, **keywords):
        #Number of turns worth of remaining fuel.
        self.max_fuel = 1
        self._fuel = self.max_fuel
        
        # Minimum movement distance
        self.min_move_distance = 1
        
        #load the base class
        super().__init__(**keywords)
        
        #All air units have the same movement sound
        self.move_sound = "JetMove"

        #set unit specific things.
        self.type = "Air Unit"
        
    @property
    def fuel(self):
        """
        The unit's remaining fuel.
        """
        return self._fuel
        
    def _update_image(self):
        """
        Redraws the unit's image.
        """
        super()._update_image()
        
        # Determine percent of fuel remaining
        fuel_percent = self.fuel / self.max_fuel
        
        # Get the rectangle for the inside of the indicator
        inner_rect = pygame.Rect(FUEL_RECT.left + 1,
                                 FUEL_RECT.top + 1,
                                 FUEL_RECT.width - 2,
                                 FUEL_RECT.height - 2)
        
        # Shrink it depending on the amount of fuel remaining
        inner_rect.w -= inner_rect.w * (1 - fuel_percent)
        if inner_rect.w < 1: inner_rect.w = 1
        
        # Determine the colours to use
        if self.fuel > FUEL_BAD_CUTOFF:
            back = FUEL_BACK_COLOUR
        else:
            back = FUEL_BACK_COLOUR_BAD
        
        if fuel_percent > 0.5:
            fill = FUEL_FILL_COLOUR
        else:
            fill = FUEL_FILL_COLOUR_HALF
        
        # Draw the indicator
        pygame.gfxdraw.box(self.image, FUEL_RECT, back)
        pygame.gfxdraw.box(self.image, inner_rect, fill)
    
    def is_docked(self, pos):
        """
        Checks if the given position is currently adjacent to a carrier of the
        same team.
        """
        for u in BaseUnit.active_units:
            if (u.team == self.team and
                isinstance(u, Carrier) and
                helper.manhattan_dist((u.tile_x, u.tile_y), pos) <= 1):
                # This is an adjacent carrier! Rejoice!
                return True
        
        # No carriers
        return False
        
    def activate(self):
        """
        Adds this unit to the active roster. Sets it to a higher layer so that
        it draws on top of other units.
        """
        super().activate()
        BaseUnit.active_units.change_layer(self, AIR_LAYER)
        
    def is_stoppable(self, tile, pos):
        """
        Returns whether or not a unit can stop on a certain tile.
        """
        dist = helper.manhattan_dist((self.tile_x, self.tile_y), pos)
        
        # Check if this is too close to stop in
        if (dist < self.min_move_distance and
            (not self.is_docked(pos))):
            return False
            
        return super().is_stoppable(tile, pos)
        
    def get_defense(self, tile = None):
        """
        Returns this unit's defense.
        If a tile is specified the tile's defense bonus is added to
        the return value.
        
        Overrides the superclass method because planes are unaffected
        by terrain bonus defense.
        """
        return self.defense
        
    def set_fuel(self, fuel):
        """
        Changes the fuel amount and updates the graphic.
        """
        self._fuel = fuel
        self._update_image()
        
    def can_turn_end(self):
        """
        Returns whether the player turn can end.
        """
        # We haven't moved, and we aren't docked, so we can't finish the turn
        if (not self.turn_state[0] and
            not self.is_docked(self.tile_pos)):
            return False
        
        # Default to the superclass
        return super().can_turn_end()
        
    def turn_ended(self):
        """
        Called when the turn is ended. Runs the aircraft out of fuel, or refuels
        if there's a carrier nearby.
        """
        super().turn_ended()
        
        # Refuel at carriers
        if self.is_docked(self.tile_pos):
            self.set_fuel(self.max_fuel)
            return True
        
        # Decrease fuel each turn
        self.set_fuel(self.fuel - 1)
        
        # Die if we're out of fuel
        if self.fuel <= 0:
            self.hurt(self.max_health)
            return False
            
        return True
        
    def is_passable(self, tile, pos):
        """
        Returns whether or not this unit can move over a certain tile.
        """
        # Return default
        if not super().is_passable(tile, pos):
            return False
            
        # We can't pass through enemy air units.
        u = BaseUnit.get_unit_at_pos(pos)
        if u and u.team != self.team and isinstance(u, AirUnit):
            return False

        # Air units can pass over everything else
        return True
        
    def is_tile_in_range(self, from_tile, from_pos, to_pos):
        """
        Checks to see if a tile is in attackable range from its current
        position. Takes tile range bonus into account.
        
        Overrides superclass method because planes are unaffected
        by terrain range bonus.
        """
        # Get range
        r = self.max_atk_range
        
        dist = helper.manhattan_dist(from_pos, to_pos)
        if dist <= r:
            return True
        return False
