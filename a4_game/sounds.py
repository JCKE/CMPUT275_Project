import pygame
from pygame.mixer import Sound

class SoundManager:
    """
    A class to manage sounds. Does not initially load any sound file,
    but instead loads on request the first time
    """
    _sounds = {}
    
    def __init__(self):
        """
        """
        pass
    
    @staticmethod
    def play(sound_name):
        """
        Plays a requested sound. If the sound isn't already loaded then
        the sound is loaded first.
        """
        if not sound_name:
            return
        
        # Load sound if not already loaded
        if sound_name not in SoundManager._sounds:
            
            # Check if the sound load is successful
            if not SoundManager._load(sound_name):
                # Return if it did not load successfully
                return
        
        # Play the sound, no extra args needed, defaults are fine
        SoundManager._sounds[sound_name].play()
    
    @staticmethod
    def _load(name):
        """
        Loads a .wav file as a pygame.mixer.Sound and places it into the 
        dictionary.
        """
        if not name:
            return False

        try:
            # Construct the path
            file_name = "assets/{}.wav".format(name)
            
            # Load from path and save to the dictionary
            SoundManager._sounds[name] = Sound(file = file_name)
            
            # Return success
            return True
        
        # Problem loading the sound
        except pygame.error:
            print("Exception loading sound file \"{}\".".format(name))
            return False
