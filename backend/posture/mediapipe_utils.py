import mediapipe as mp
import math
import cv2

mp_pose = mp.solutions.pose

def get_pose_landmarks(frame):
    """
    Returns the full pose_landmarks object for visualization
    and a list of landmarks for angle calculation.
    """
    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5) as pose:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        if results.pose_landmarks:
            return results.pose_landmarks, results.pose_landmarks.landmark
        return None, None

def calculate_angle(a, b, c):
    """Calculate angle between three points a,b,c"""
    a = [a.x, a.y]
    b = [b.x, b.y]
    c = [c.x, c.y]

    ba = [a[0]-b[0], a[1]-b[1]]
    bc = [c[0]-b[0], c[1]-b[1]]

    cosine_angle = (ba[0]*bc[0] + ba[1]*bc[1]) / (math.sqrt(ba[0]**2 + ba[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2))
    angle = math.degrees(math.acos(max(min(cosine_angle,1),-1)))
    return angle

def get_squat_angles(landmarks):
    """
    Returns important angles for squat: knees and hips
    landmarks: list of landmarks (pose_landmarks.landmark)
    """
    angles = {}

    # Check if landmarks list is valid
    if not landmarks or len(landmarks) < 33:  # MediaPipe Pose has 33 landmarks
        return angles  # empty dict if not enough landmarks

    # Right knee
    angles['right_knee'] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    # Left knee
    angles['left_knee'] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    # Right hip
    angles['right_hip'] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    )
    # Left hip
    angles['left_hip'] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    )
    return angles