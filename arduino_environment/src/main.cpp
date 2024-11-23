#include "Arduino.h"

void setup() {
  // Initialize serial communication at 9600 bits per second
  Serial.begin(9600);
}

void loop() {
  // Print "Hello World" to the serial console
  int Vin = analogRead(A0);
  // print out the value you read:
  Serial.println(Vin);
  
  // Wait for 1000 milliseconds (1 second)
  delay(16);
}
