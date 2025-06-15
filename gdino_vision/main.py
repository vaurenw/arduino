import cv2
import mediapipe as mp
import numpy as np
import serial
import time

# Initialize serial connection to Arduino
try:
    arduino = serial.Serial('COM6', 115200)  # Change port as needed
    # arduino = serial.Serial('/dev/ttyUSB0', 115200)  # For Linux
    # arduino = serial.Serial('/dev/tty.usbmodem1411', 115200)  # For Mac
    time.sleep(1)
    print("Arduino connected successfully!")
except:
    print("Failed to connect to Arduino. Check your port.")
    arduino = None

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Right eye landmark indices for MediaPipe (468 face landmarks)
RIGHT_EYE_LANDMARKS = [
    33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246
]

# Key points for eye aspect ratio calculation
RIGHT_EYE_KEY_POINTS = [
    33,  # Right eye left corner
    133,  # Right eye right corner
    160,  # Right eye top
    144,  # Right eye bottom
    158,  # Right eye top-left
    153  # Right eye bottom-left
]


def calculate_eye_aspect_ratio(landmarks, eye_points, img_width, img_height):
    """Calculate Eye Aspect Ratio using MediaPipe landmarks"""
    # Convert normalized coordinates to pixel coordinates
    coords = []
    for point in eye_points:
        x = int(landmarks[point].x * img_width)
        y = int(landmarks[point].y * img_height)
        coords.append([x, y])

    # Calculate distances for EAR
    # Vertical distances
    v1 = np.linalg.norm(np.array(coords[2]) - np.array(coords[3]))  # top - bottom
    v2 = np.linalg.norm(np.array(coords[4]) - np.array(coords[5]))  # top-left - bottom-left

    # Horizontal distance
    h = np.linalg.norm(np.array(coords[0]) - np.array(coords[1]))  # left - right

    # EAR calculation
    if h > 0:
        ear = (v1 + v2) / (2.0 * h)
        return ear
    return 0


def send_servo_position(position):
    """Send servo position to Arduino (0-180 degrees)"""
    if arduino:
        command = f"{position}\n"
        arduino.write(command.encode())


def get_eye_center(landmarks, eye_points, img_width, img_height):
    """Get the center point of the eye for visualization"""
    x_coords = [landmarks[point].x * img_width for point in eye_points]
    y_coords = [landmarks[point].y * img_height for point in eye_points]
    center_x = int(sum(x_coords) / len(x_coords))
    center_y = int(sum(y_coords) / len(y_coords))
    return (center_x, center_y)


# Initialize camera with optimized settings
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# MediaPipe Face Mesh configuration
with mp_face_mesh.FaceMesh(
        max_num_faces=1,  # Track only one face for speed
        refine_landmarks=True,  # More accurate landmarks
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
) as face_mesh:
    print("Starting MediaPipe right eye tracking...")
    print("Your right eye controls the servo! Press 'q' to quit")

    frame_count = 0
    skip_frames = 1  # Process every frame for maximum responsiveness

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_count += 1

        # Skip frames if needed (set to 1 for no skipping)
        if frame_count % skip_frames != 0:
            continue

        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            # Calculate right eye aspect ratio
            right_ear = calculate_eye_aspect_ratio(
                face_landmarks.landmark,
                RIGHT_EYE_KEY_POINTS,
                width,
                height
            )

            # Map EAR to servo position (0-180 degrees)
            # Adjust these values based on your eye's EAR range
            min_ear, max_ear = 0.1, 0.4  # Typical range for closed to wide open

            # Clamp and map to servo range
            normalized_ear = np.clip((right_ear - min_ear) / (max_ear - min_ear), 0, 1)
            servo_pos = int(normalized_ear * 180)

            # Send position to servo immediately
            send_servo_position(servo_pos)

            # Visual feedback - draw right eye landmarks
            eye_center = get_eye_center(face_landmarks.landmark, RIGHT_EYE_LANDMARKS, width, height)
            cv2.circle(frame, eye_center, 5, (0, 255, 0), -1)

            # Draw right eye contour
            eye_points = []
            for point_idx in RIGHT_EYE_LANDMARKS:
                x = int(face_landmarks.landmark[point_idx].x * width)
                y = int(face_landmarks.landmark[point_idx].y * height)
                eye_points.append([x, y])

            eye_points = np.array(eye_points, dtype=np.int32)
            cv2.polylines(frame, [eye_points], True, (0, 255, 0), 1)

            # Display information
            cv2.putText(frame, f"Right Eye EAR: {right_ear:.3f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Servo Position: {servo_pos}°", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show blink detection
            if right_ear < 0.2:  # Adjust threshold as needed
                cv2.putText(frame, "BLINK DETECTED!", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Show frame
        cv2.imshow('MediaPipe Right Eye Servo Control', frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
print("System shutdown complete.")