#include <Arduino.h>
#include <Adafruit_ST7735.h>

// the pins used to connect to the AdaFruit display
const uint8_t sd_cs = 5;
const uint8_t tft_cs = 6;
const uint8_t tft_dc = 7;
const uint8_t tft_rst = 8;    

Adafruit_ST7735 tft = Adafruit_ST7735(tft_cs, tft_dc, tft_rst);
void initialize_screen();
uint16_t serial_readline(char *line, uint16_t line_size);
uint16_t string_read_field(const char *str, uint16_t str_start, 
			   char *field, uint16_t field_size, const char *sep);

void setup()
{
  Serial.begin(9600);
  initialize_screen();

  // TESTING FOR ALLOC TIMES
  /*unsigned long time = micros();
  unsigned long *array;
  array = (unsigned long *) malloc(1000 * sizeof(unsigned long));
  Serial.println(micros() - time);

  time = micros();
  unsigned long *array2;
  array2 = (unsigned long *) calloc(810, sizeof(unsigned long));
  Serial.println(micros() - time);*/

  tft.println("Start!");
}

void loop()
{
  delay(9000);
  Serial.println("-11350000 535022 -11351000 5351000 56789 ");
  //while(Serial.available() == 0) { } // Waits for something to come over the serial port

  char path_size_buffer[5];
  serial_readline(path_size_buffer, 100); // Waits for something to come over the serial port
  //path_size_buffer = (char *) calloc(5, sizeof(char));
  
  //while(Serial.available() == 0) { } 
  
  //Serial.readBytesUntil(' ', path_size_buffer, 100);
  int path_size = atoi(path_size_buffer);

  //char size[] = {Serial.read()};
  //int path_size = atoi(size);
  //tft.print(path_size); // the size of the incoming path
  //tft.print(" ");

  long *path_array;
  path_array = (long *) calloc(path_size, sizeof(long));
  
  //char path_size_buffer[70];
  //serial_readline(path_string, 900);
  //while(Serial.available() == 0) { }

  //string_read_field(const char *str, 0, 
  //		    char *field, 100, ' ')
  for(int i = 0; i < path_size; i++)
    { 
      char serial_data_buffer[20];
      //serial_data_buffer = (char *) calloc(20, sizeof(char));

      Serial.readBytesUntil(' ', serial_data_buffer, 100);
      path_array[i] = atol(serial_data_buffer);
      
      //free(serial_data_buffer);
      }

  for(int i = 0; i < path_size; i++)
    {
      tft.print(path_array[i]);
      tft.print(" ");
    }
  tft.println();
  free(path_array);
  //while(1) {}
}

void initialize_screen() {
  tft.initR(INITR_REDTAB);

  tft.setRotation(2);

  tft.setCursor(0, 0);
  tft.setTextColor(0x0000);
  tft.setTextSize(1);
  tft.fillScreen(ST7735_WHITE);    
}

uint16_t serial_readline(char *line, uint16_t line_size) {
    int bytes_read = 0;    // Number of bytes read from the serial port.

    // Read until we hit the maximum length, or a newline.
    // One less than the maximum length because we want to add a null terminator.
    while (bytes_read < line_size - 1) {
        while (Serial.available() == 0) {
            // There is no data to be read from the serial port.
            // Wait until data is available.
        }

        line[bytes_read] = (char) Serial.read();

        // A newline is given by \r or \n, or some combination of both
        // or the read may have failed and returned 0
        if ( line[bytes_read] == '\r' || line[bytes_read] == '\n' ||
             line[bytes_read] == 0 ) {
                // We ran into a newline character!  Overwrite it with \0
                break;    // Break out of this - we are done reading a line.
        } else {
            bytes_read++;
        }
    }

    // Add null termination to the end of our string.
    line[bytes_read] = '\0';
    return bytes_read;
}

uint16_t string_read_field(const char *str, uint16_t str_start, 
			   char *field, uint16_t field_size, const char *sep) {

    // Want to read from the string until we encounter the separator.

    // Character that we are reading from the string.
    uint16_t str_index = str_start;    

    while (1) {
        if ( str[str_index] == '\0') {
            str_index++;  // signal off end of str
            break;
            }

        if ( field_size <= 1 ) break;

        if (strchr(sep, str[str_index])) {
            // field finished, skip over the separator character.
            str_index++;    
            break;
            }

        // Copy the string character into buffer and move over to next
        *field = str[str_index];    
        field++;
        field_size--;
        // Move on to the next character.
        str_index++;    
        }

    // Make sure to add NULL termination to our new string.
    *field = '\0';

    // Return the index of where the next token begins.
    return str_index;    
}
