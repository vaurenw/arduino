import cv2
import mediapipe as mp
import numpy as np

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Load video
cap = cv2.VideoCapture("sprinter_start.mp4")
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Output video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output_sprint_feedback.mp4", fourcc, fps, (width, height))

# Angle calculation
def get_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine, -1.0, 1.0))
    return np.degrees(angle)

# Drawing + Feedback
def draw_and_evaluate(frame, label, p1, p2, p3, ideal_range, feedback, landmarks, w, h):
    if landmarks[p1].visibility < 0.5 or landmarks[p2].visibility < 0.5 or landmarks[p3].visibility < 0.5:
        return
    a = [landmarks[p1].x, landmarks[p1].y]
    b = [landmarks[p2].x, landmarks[p2].y]
    c = [landmarks[p3].x, landmarks[p3].y]
    angle = get_angle(a, b, c)
    min_ideal, max_ideal = ideal_range
    color = (0, 255, 0) if min_ideal <= angle <= max_ideal else (0, 0, 255)
    pos = tuple(np.multiply(b, [w, h]).astype(int))
    cv2.putText(frame, f"{label}: {int(angle)}°", pos, cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    if not (min_ideal <= angle <= max_ideal):
        y_offset = 90 + 85 * draw_and_evaluate.error_count
        cv2.putText(frame, f"{feedback}", (30, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
        draw_and_evaluate.error_count += 1

draw_and_evaluate.error_count = 0

# Frame-by-frame analysis
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        draw_and_evaluate.error_count = 0  # Reset feedback counter

        # Detailed biomechanical feedback
        draw_and_evaluate(frame, "Front Knee", mp_pose.PoseLandmark.LEFT_HIP.value,
                          mp_pose.PoseLandmark.LEFT_KNEE.value, mp_pose.PoseLandmark.LEFT_ANKLE.value,
                          (85, 110), "Front knee should bend ~90 to load force.", landmarks, width, height)

        draw_and_evaluate(frame, "Rear Knee", mp_pose.PoseLandmark.RIGHT_HIP.value,
                          mp_pose.PoseLandmark.RIGHT_KNEE.value, mp_pose.PoseLandmark.RIGHT_ANKLE.value,
                          (115, 135), "Rear knee needs more extension for push-off.", landmarks, width, height)

        draw_and_evaluate(frame, "Left Elbow", mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                          mp_pose.PoseLandmark.LEFT_ELBOW.value, mp_pose.PoseLandmark.LEFT_WRIST.value,
                          (80, 105), "Left arm should be bent ~90 and swing vertically.", landmarks, width, height)

        draw_and_evaluate(frame, "Right Elbow", mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                          mp_pose.PoseLandmark.RIGHT_ELBOW.value, mp_pose.PoseLandmark.RIGHT_WRIST.value,
                          (80, 105), "Right elbow should stay close to 90 bend.", landmarks, width, height)

        draw_and_evaluate(frame, "Torso Lean", mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                          mp_pose.PoseLandmark.LEFT_HIP.value, mp_pose.PoseLandmark.LEFT_KNEE.value,
                          (145, 170), "Torso should lean slightly forward, not collapse.", landmarks, width, height)

        draw_and_evaluate(frame, "Neck Alignment", mp_pose.PoseLandmark.NOSE.value,
                          mp_pose.PoseLandmark.LEFT_SHOULDER.value, mp_pose.PoseLandmark.LEFT_HIP.value,
                          (145, 170), "Keep neck in line with spine, avoid looking up/down.", landmarks, width, height)

        draw_and_evaluate(frame, "Ankle Extension", mp_pose.PoseLandmark.RIGHT_KNEE.value,
                          mp_pose.PoseLandmark.RIGHT_ANKLE.value, mp_pose.PoseLandmark.RIGHT_HEEL.value,
                          (155, 180), "Full ankle extension for explosive push-off.", landmarks, width, height)

        draw_and_evaluate(frame, "Hip Extension", mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                          mp_pose.PoseLandmark.RIGHT_HIP.value, mp_pose.PoseLandmark.RIGHT_KNEE.value,
                          (160, 180), "Push-off hip must extend fully for max propulsion.", landmarks, width, height)

    # Display and write output
    cv2.imshow("Sprint Form Analyzer", frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
