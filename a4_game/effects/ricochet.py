import animation

class Ricochet(animation.Animation):
    """
    An animated bullet ricochet effect.
    """
    def __init__(self, pos):
        """
        Initialize the sprite effect.
        """
        animation.Animation.__init__(self,
                                     "assets/ricochet.png",
                                     20,
                                     20,
                                     0.15,
                                     animation.Mode.OneShot)
        self.rect.topleft = pos
