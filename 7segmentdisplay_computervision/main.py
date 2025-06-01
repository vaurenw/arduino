import cv2
import mediapipe as mp
import serial
import time

arduino = serial.Serial('COM5', 9600)  

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

finger_tips = [4, 8, 12, 16, 20]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    finger_count = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark

            if lm[finger_tips[0]].x < lm[finger_tips[0] - 1].x:
                finger_count += 1

            for tip in finger_tips[1:]:
                if lm[tip].y < lm[tip - 2].y:
                    finger_count += 1

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        
        arduino.write(str(finger_count).encode())
        time.sleep(0.1)  

    # Display
    cv2.putText(frame, f'Fingers: {finger_count}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("Finger Counter", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
