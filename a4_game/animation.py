import pygame
from pygame.sprite import Sprite

class Mode:
    Loop, OneShot = range(2)

class Animation(Sprite):
    """
    An animated effect.
    """
    
    def __init__(self, filename, frame_w, frame_h, rate, mode = Mode.Loop):
        """
        Initialize the animation, loading the image from the given filename.
        The animation will be of size frame_w x frame_h.
        Rate is the rate of change of the frames, in frames per tick.
        Mode is the animation mode. Loop mode will loop over the animation,
        while OneShot mode will kill the sprite once it completes the animation.
        """
        Sprite.__init__(self)
        
        # The base spritesheet.
        self._base_image = pygame.image.load(filename)
        
        # Animation data
        self.mode = mode
        self.rate = rate
        self.frame = 0
        
        # Set the pygame-required parameters.
        self.image = None
        self.rect = pygame.Rect(0, 0, frame_w, frame_h)
        self._update_image()

    def get_frame_count(self):
        """
        Returns the number of frames in this animation.
        
        >>> anim = Animation("assets/explosion.png", 20, 20, 1)
        >>> anim.get_frame_count()
        5
        """
        return self._base_image.get_rect().w // self.rect.w
        
    def _update_image(self):
        """
        Sets the image to the correct sprite frame.
        """
        w, h = self.rect.size
        subrect = pygame.Rect(w * int(self.frame), 0, w, h)
        self.image = self._base_image.subsurface(subrect)
        
    def update(self):
        """
        Updates the animation state.
        """
        # Increment the frame
        self.frame += self.rate
        
        if self.mode == Mode.Loop:
            # Loop the animation
            self.frame %= self.get_frame_count()
        elif self.frame >= self.get_frame_count():
            # Kill the animation once it's done
            self.frame = 0
            self.kill()
        
        # Update the actual image
        self._update_image()
        
    def reset(self):
        """
        Resets the animation to its first frame.
        """
        self.frame = 0
