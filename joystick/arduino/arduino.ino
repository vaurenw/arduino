void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP); // SW button
}

void loop() {
  int x = analogRead(A0);
  int y = analogRead(A1);
  bool sw = digitalRead(2) == LOW;

  String direction = "";

  if (x < 400) direction += "L";
  else if (x > 600) direction += "R";

  if (y < 400) direction += "U";
  else if (y > 600) direction += "D";

  if (sw) direction += "P"; // P for press

  if (direction != "") {
    Serial.println(direction);
    delay(100); // adjust for smoother control
  }
}