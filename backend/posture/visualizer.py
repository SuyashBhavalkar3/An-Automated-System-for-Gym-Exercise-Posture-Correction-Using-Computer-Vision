import mediapipe as mp
import cv2
import base64

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def draw_skeleton(frame, pose_landmarks):
    """
    Draw skeleton and return base64 encoded frame
    pose_landmarks: full object from MediaPipe (not just list)
    """
    annotated_frame = frame.copy()
    mp_drawing.draw_landmarks(
        annotated_frame,
        pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    encoded_frame = base64.b64encode(buffer).decode('utf-8')
    return encoded_frame