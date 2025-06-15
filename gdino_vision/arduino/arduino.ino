#include <Servo.h>

Servo eyeServo;
int servoPin = 9;          // Servo connected to pin 9
int currentPosition = 90;   // Current servo position
int targetPosition = 90;    // Target servo position
int lastPosition = 90;      // Last position for smooth movement

// Servo movement parameters for smooth operation
int moveDelay = 5;          // Milliseconds between servo steps (lower = faster)
int stepSize = 2;           // Degrees per step (smaller = smoother)

void setup() {
  Serial.begin(115200);     // Match Python baud rate
  eyeServo.attach(servoPin);
  
  // Initialize servo to center position
  eyeServo.write(90);
  currentPosition = 90;
  targetPosition = 90;
  
  Serial.println("Arduino servo controller ready");
}

void loop() {
  // Check for incoming servo position from Python
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    int newPosition = input.toInt();
    
    // Validate position range
    if (newPosition >= 0 && newPosition <= 180) {
      targetPosition = newPosition;
    }
  }
  
  // Smooth servo movement
  if (currentPosition != targetPosition) {
    if (currentPosition < targetPosition) {
      currentPosition = min(currentPosition + stepSize, targetPosition);
    } else {
      currentPosition = max(currentPosition - stepSize, targetPosition);
    }
    
    eyeServo.write(currentPosition);
    
    // Only add delay if we're still moving (reduces lag)
    if (currentPosition != targetPosition) {
      delay(moveDelay);
    }
  }
  
  // Small delay to prevent overwhelming the serial buffer
  delay(1);
}



