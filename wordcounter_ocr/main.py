import cv2
import numpy as np
import easyocr
import mss
import serial
import time
import matplotlib.pyplot as plt

# Initialize OCR
reader = easyocr.Reader(['en'], gpu=False)

# Setup Serial for Arduino (adjust COM port if needed)
arduino = serial.Serial('COM5', 9600)
time.sleep(2)

# Define screen region to scan
monitor_region = {
    "top": 100,
    "left": 300,
    "width": 800,
    "height": 600
}

last_count = -1

plt.ion()  # Interactive mode for live updating

with mss.mss() as sct:
    while True:
        screenshot = sct.grab(monitor_region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        results = reader.readtext(img)
        words = [text.lower() for (_, text, _) in results]
        count = words.count("ngmi")



# ngmi
        if count != last_count:
            print(f"Detected '{count}' occurrences of 'ngmi'")
            arduino.write(f"{count}\n".encode())
            last_count = count

        # no image display here
