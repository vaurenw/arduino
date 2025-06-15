int segments[] = {2, 3, 4, 5, 6, 7, 8};
byte digits[6][7] = {
  {1,1,1,1,1,1,0}, // 0
  {0,1,1,0,0,0,0}, // 1
  {1,1,0,1,1,0,1}, // 2
  {1,1,1,1,0,0,1}, // 3
  {0,1,1,0,0,1,1}, // 4
  {1,0,1,1,0,1,1}  // 5
};

void setup() {
  for (int i = 0; i < 7; i++) {
    pinMode(segments[i], OUTPUT);
  }
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    int num = Serial.read() - '0';
    if (num >= 0 && num <= 5) {
      for (int i = 0; i < 7; i++) {
        digitalWrite(segments[i], digits[num][i]);
      }
    }
  }
}
