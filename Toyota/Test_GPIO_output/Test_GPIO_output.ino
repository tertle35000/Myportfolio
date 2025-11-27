#include <Wire.h>
#include "TCA9554.h"

#define TCA9554_ADDRESS         0x20                      // TCA9554PWR I2C address
TCA9554 gpioExpander (TCA9554_ADDRESS);
#define I2C_SCL_PIN       41
#define I2C_SDA_PIN       42

void setup()
{
  Wire.begin( I2C_SDA_PIN, I2C_SCL_PIN); 
  Serial.begin(115200);
  while (!Serial);
  delay(1000);
  
  gpioExpander.PinState();
  gpioExpander.PinMode();
  gpioExpander.AllOn();
  delay(2000);
  gpioExpander.AllOff();
}

byte lamps[8];

void loop()
{
  for (int i = 1; i <= 7; i++){
    if (i == 1) {
      memset(lamps, 0, sizeof(lamps));
    }
    lamps[i-1] = 1;
    gpioExpander.SetLamps(lamps);
    delay(1000);
  }

}