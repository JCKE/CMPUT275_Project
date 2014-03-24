#include <UTFT.h>

// Declare which fonts we will be using
extern uint8_t SmallFont[];

UTFT myGLCD(ITDB32S,38,39,40,41);   // For the Arduino Mega

void setup()
{
  //Serial.begin(9600);
// Setup the LCD
  myGLCD.InitLCD();
  myGLCD.setFont(SmallFont);
  //Serial.println("It works!");
}

void loop() {}
