#include <LiquidCrystal.h>
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);
int val = 0; //value for storing moisture value
int soilPin = A1;//Declare a variable for the soil moisture sensor
int soilPower = 0;//Variable for Soil moisture Power

void setup() 
{
  Serial.begin(9600);   // open serial over USB
  pinMode(soilPower, OUTPUT);//Set D0 as an OUTPUT
  digitalWrite(soilPower, LOW);//Set to LOW so no power is flowing through the sensor
  lcd.begin(16, 2);              // start the library
  lcd.setCursor(0,0);
}

void loop() 
{
  if (Serial.available() > 0) {
  // Read the incoming byte
  char receivedChar = Serial.read();

  // Display the received character
  if(receivedChar == '1'){    
  Serial.println(readSoil(A1, 0));
  }
  else if(receivedChar == '2'){    
  Serial.println(readSoil(A2, 1));
  }
    else if(receivedChar == '3'){    
  Serial.println(readSoil(A3, 1));
  }
  else if(receivedChar == 'a'){
    getIP();
  }
  else {
    Serial.println("Did not recognize");
    Serial.println(receivedChar);
  }
  }

  delay(1000);//Read a command every second
}

void getIP(){
  while(true){
    if (Serial.available() > 0) {
      char receivedChar = Serial.read();
      if(receivedChar != 'z'){
      lcd.print(receivedChar);
      }
      else {
        break;
      }
    }
  }

}

int readSoil(int pin, int power)
{
    digitalWrite(power, HIGH);//turn power pin "On"
    delay(10);//wait 10 milliseconds
    val = analogRead(pin);//Read the SIG value form sensor
    digitalWrite(power, LOW);//turn power pin "Off"
    return val;//send current moisture value
}