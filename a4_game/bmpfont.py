import pygame

class BitmapFont:
    """
    A class which provides basic bitmap font drawing.
    """

    def __init__(self, filename, char_w, char_h, start_char = 0):
        """
        Initializes the bitmap font.
        The font is loaded from filename, and the character size will be w x h.
        start_char is the ASCII value at which the font starts.
        """
        self._image = pygame.image.load(filename)
        self._char_w = char_w
        self._char_h = char_h
        self._start_char = start_char
        
    def get_char_width(self):
        """
        Returns the pixel width of one character.
        
        >>> font = BitmapFont("assets/healthfont.png", 6, 7)
        >>> font.get_char_width()
        6
        """
        return self._char_w
        
    def get_char_height(self):
        """
        Returns the pixel height of one character.
        
        >>> font = BitmapFont("assets/healthfont.png", 6, 7)
        >>> font.get_char_height()
        7
        """
        return self._char_h
        
    def get_char_size(self):
        """
        Returns a tuple of the pixel width and height of a single character
        rendered in this font
        
        >>> font = BitmapFont("assets/healthfont.png", 6, 7)
        >>> font.get_char_size()
        (6, 7)
        """
        return (self.get_char_width(),
                 self.get_char_height())
        
    def get_str_width(self, string):
        """
        Returns the pixel width of the given string rendered with this font.
        
        >>> font = BitmapFont("assets/healthfont.png", 6, 7)
        >>> font.get_str_width("103")
        18
        """
        return self._char_w * len(string)
        
    def get_str_height(self, string):
        """
        Returns the pixel height of the given string rendered with this font.
        
        >>> font = BitmapFont("assets/healthfont.png", 6, 7)
        >>> font.get_str_width("103")
        7
        """
        return self._char_h
        
    def get_str_size(self, string):
        """
        Returns a tuple of the pixel width and height of the given string
        rendered in this font
        
        >>> font = BitmapFont("assets/healthfont.png", 6, 7)
        >>> font.get_str_size("103")
        (18, 7)
        """
        return (self.get_str_width(string),
                 self.get_str_height(string))
        
    def render(self, string):
        """
        Returns a new surface with the given string drawn onto it in this
        bitmap font.
        """
        # Create the empty surface
        str_size = self.get_str_size(string)
        surface = pygame.Surface(str_size, flags=pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        
        # Draw each character on
        char_rect = pygame.Rect((0, 0), self.get_char_size())
        index = 0
        for c in string:
            # Determine which index in the font represents this character
            font_index = ord(c) - self._start_char
            
            # Draw the character
            surface.blit(self._image,
                         # The destination is relative to the index
                         char_rect.move(index * char_rect.w, 0),
                         # This is the subrectangle to draw, i.e. the character
                         char_rect.move(font_index * char_rect.w, 0))
                         
            # Move to the next space on the surface
            index += 1
            
        return surface
