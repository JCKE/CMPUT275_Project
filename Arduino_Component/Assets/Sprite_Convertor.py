"""
.pbm Sprite Convertor

This program runs under basically the same principles as map_convertor.py in the /Maps directory,
so you should read that one first as there's not much re-commenting of information already explained there.
I came up with the map_convertor by myself a while a go, but this one was made near the end of the project
to avoid having to always go to the UTFT library creator's website for every single image, and since his
convertor would cut off up to 15 pixels from the bottom right corner of the images.

http://www.henningkarlsen.com/electronics/t_imageconverter565.php

Because of this, I cannot take full credit for originality since I would not have known how to properly
store bitmap info. That being said, this program doesn't contain any code copied from someone else.

This program will take a .pbm image, and store its pixel (x, y) coordinates and colour in a .c
file to be accessed when printing sprites to the screens. This is the major difference between the two convertors,
but this one also takes in multiple sprites at a time if you like since you'll probably be uploading a few at
a time. As such, the image dimensions are stored for each image in dictionaries in main(), and the file_data
dict now stores multiple images. The magenta utilized here serves as a transparency when drawing to the screen,
but you'll have to check out my UTFT edit mentioned in the readme to see what I'm talking about.
any color can be used so long as you update what's being passed into myGLCD.drawBitmap() to be an appropriate
color. Magenta was used because of it's disctinction from most colors used (and because it's the best color ever)

For each image it unpacks the information into these dictionaries and writes them similar to map_convertor.py.
This time, any .h file can be printed to, but most-likely you'll be using 'project.h'. This was really meant to
allow for ease of printing in the future where the sprites definitions might be located elsewhere. Also, the .h file
must be in the same folder to work. To keep from having multiple .c files, you can just tell it to append the
info to the same .c or a pre-existing .c file. The only danger is if you already have the image pre-defined and you're
uploading one with the same name as that, it will complain about multiple definitions.

You would need to move any pre-existing .h and .c files you want to write to into a folder containg sprites, then back again.

Jesse Emery
31/03/2014
"""

import os
import sys
    
def color565(redNumber, greenNumber, blueNumber):
    redNumber = redNumber//8
    greenNumber = greenNumber//4
    blueNumber = blueNumber//8

    redNumber = redNumber << 11
    greenNumber = greenNumber << 5
    
    return (redNumber+greenNumber+blueNumber)
    
def unpack_image(filename):
    current_file = open(filename + '.pbm', 'r')
    
    # This next bit handles first 4 pieces of header information always preceding the pixel info.
    # This information MUST be consistent with the contour file.
    current_file.readline()          # PPM Identifier, not that usefull to us
    width = current_file.readline()  # Width of image in pixels
    height = current_file.readline() # Height of image in pixels
    current_file.readline()          # Colour precision equal to the highest possible colour: 8-bit = 255, 16-bit = 65535 etc.
    
    width = int(width.rstrip('\n'))
    height = int(height.rstrip('\n'))
    info = dict()
    
    # Now we're getting into the actual image.
    for pixel in range(width*height):
        RGB = current_file.read(3)
        new_RGB = color565(ord(RGB[0]), ord(RGB[1]), ord(RGB[2]))

        info[(pixel%width, pixel//width)] = "0x%X"%new_RGB # this notation changes the hex letters to be capitalized
        

    current_file.close()
    
    return info, width, height

def main():
    file_data = {}
    pixels_x = {}
    pixels_y = {}
    
    print('\nEnter .pbm files (without the .pbm):')
    image_files = sys.stdin.readline().rstrip('\n').split()
    
    print('\nEnter .c file to write to (without the .c):')
    write_file = sys.stdin.readline().rstrip('\n')

    print('\nEnter a .h file to write to, or skip.\n(must have //<><>SPRITES<><> to write properly)')
    dot_h = sys.stdin.readline().rstrip('\n')
    print('Processing...')

    for image_file in image_files:
        file_data[image_file], pixels_x[image_file], pixels_y[image_file] = unpack_image(image_file)
    print_to_dot_c(image_files, write_file, file_data, pixels_x, pixels_y, dot_h)
    
def print_to_dot_c(image_names, write_file, file_info, pixel_x, pixel_y, dot_h):
    """
    As mentioned before, this functions similar to map_convertor.py.
    """
    if(dot_h != ''):
        dot_h_file = open(dot_h + '.h', 'r') # open dot.h to read previous info
        info_buffer = dot_h_file.read().split('\n')
        dot_h_file.close()
        os.remove(dot_h + '.h')
    
        dot_h_file = open(dot_h + '.h', 'w') # make dot.h to write to now
        while info_buffer:
            dot_h_file.write(info_buffer[0])
            if len(info_buffer) > 1:
                dot_h_file.write('\n');
            if info_buffer[0].replace(" ", "") == '//<><>SPRITES<><>': # getting rid of the white-space allows room for mess-ups if the spacing is off
                for image_file in image_names:
                    dot_h_file.write('extern prog_uint16_t {}[{}]; // {}x{}\n'.format(image_file, pixel_x[image_file]*pixel_y[image_file], pixel_x[image_file], pixel_y[image_file])) # adding the commented out (pixels_x)x(pixels_y) allows for easy referencing of the image sizes when drawing them
            
            info_buffer.remove(info_buffer[0])
        
        dot_h_file.close()
    
    dot_c_file = open(write_file + '.c', 'a') # create and open a .c file for appending.

    dot_c_file.write('#include <avr/pgmspace.h>\n\n')
    
    for image_file in image_names:
        image_pixel_x = pixel_x[image_file]
        image_pixel_y = pixel_y[image_file]
        dot_c_file.write('prog_uint16_t {}[{}] PROGMEM='.format(image_file, image_pixel_x*image_pixel_y) + '{\n')
        
        for pixel in range(pixel_x[image_file]*pixel_y[image_file]):
        
            dot_c_file.write("{}".format(file_info[image_file][(pixel%image_pixel_x, pixel//image_pixel_x)])) # grabbing the color
        
            if file_info[image_file][(pixel%image_pixel_x, pixel//image_pixel_x)] == '0x0':
                dot_c_file.write("000") # add some extra zeros for the black pixels to make it look better

            if pixel != (image_pixel_x*image_pixel_y)-1:
                if pixel%16 == 15: # split it into rows of 16
                    dot_c_file.write(',\n')
                else:
                    dot_c_file.write(', ')
            else:
                dot_c_file.write('};\n\n')
        
    dot_c_file.close()
    print("Success!")

if __name__ == '__main__':
    main()
