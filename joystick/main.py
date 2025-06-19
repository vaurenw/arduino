import serial
from pynput.keyboard import Controller, Key
import time

ser = serial.Serial('COM6', 9600)  
keyboard = Controller()

def press_keys(keys):
    for k in keys:
        keyboard.press(k)
    time.sleep(0.1)
    for k in keys:
        keyboard.release(k)

while True:
    line = ser.readline().decode().strip()

    keys = []
    if "U" in line:
        keys.append('w')  
    if "D" in line:
        keys.append('s')  
    if "L" in line:
        keys.append('a')  
    if "R" in line:
        keys.append('d')  
    if "P" in line:
        keys.append(Key.enter)  

    if keys:
        press_keys(keys)
