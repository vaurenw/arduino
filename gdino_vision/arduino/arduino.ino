#include <Servo.h>

Servo eyeServo;
int servoPin = 9;          // Servo connected to pin 9
int currentPosition = 0;   // Current servo position (starts at 0)
int targetPosition = 0;    // Target servo position
int lastPosition = 0;      // Last position for smooth movement


int moveDelay = 5;          
int stepSize = 2;           

void setup() {
  Serial.begin(115200);     
  eyeServo.attach(servoPin);
  
  
  eyeServo.write(0);
  currentPosition = 0;
  targetPosition = 0;
  
  Serial.println("Arduino servo controller ready - Range: 0-45 degrees");
}

void loop() {
  
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    int newPosition = input.toInt();
    
    if (newPosition >= 0 && newPosition <= 45) {
      targetPosition = newPosition;
    }
  }
  
  if (currentPosition != targetPosition) {
    if (currentPosition < targetPosition) {
      currentPosition = min(currentPosition + stepSize, targetPosition);
    } else {
      currentPosition = max(currentPosition - stepSize, targetPosition);
    }
    
    eyeServo.write(currentPosition);
    
    if (currentPosition != targetPosition) {
      delay(moveDelay);
    }
  }
  
  delay(1);
}