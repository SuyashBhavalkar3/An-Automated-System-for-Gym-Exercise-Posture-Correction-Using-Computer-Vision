import mediapipe as mp
import math
import cv2
import logging
import os

mp_pose = mp.solutions.pose

logger = logging.getLogger("posture.mediapipe_utils")


class PoseProcessor:
    """Persistent MediaPipe Pose processor to avoid re-allocating the model each frame.

    Usage:
        processor = PoseProcessor(min_detection_confidence=0.5)
        pose_landmarks, landmarks = processor.process(frame)
    """

    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.min_detection_confidence = float(os.getenv("MP_MIN_DET_CONF", min_detection_confidence))
        self.min_tracking_confidence = float(os.getenv("MP_MIN_TRACK_CONF", min_tracking_confidence))
        self.pose = mp_pose.Pose(static_image_mode=False,
                                 min_detection_confidence=self.min_detection_confidence,
                                 min_tracking_confidence=self.min_tracking_confidence)

    def process(self, frame):
        """Process an OpenCV BGR frame and return (pose_landmarks, landmarks_list).
        Both may be None if no person detected. This method is safe and efficient for
        repeated calls from a websocket loop.
        """
        if frame is None:
            return None, None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        if results.pose_landmarks:
            return results.pose_landmarks, results.pose_landmarks.landmark
        return None, None


def _safe_angle(a, b, c):
    """Calculate angle between three normalized landmarks safely.

    Returns None on invalid inputs to avoid raising exceptions from zero-length vectors.
    """
    try:
        ax, ay = a.x, a.y
        bx, by = b.x, b.y
        cx, cy = c.x, c.y

        ba_x = ax - bx
        ba_y = ay - by
        bc_x = cx - bx
        bc_y = cy - by

        denom = math.hypot(ba_x, ba_y) * math.hypot(bc_x, bc_y)
        if denom == 0:
            return None
        cosine_angle = (ba_x * bc_x + ba_y * bc_y) / denom
        cosine_angle = max(min(cosine_angle, 1.0), -1.0)
        return math.degrees(math.acos(cosine_angle))
    except Exception:
        logger.exception("Error calculating angle")
        return None

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
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    if val is not None:
        angles['right_knee'] = val
    # Left knee
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    if val is not None:
        angles['left_knee'] = val
    # Right hip
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    )
    if val is not None:
        angles['right_hip'] = val
    # Left hip
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    )
    if val is not None:
        angles['left_hip'] = val
    return angles


def _has_enough_landmarks(landmarks):
    return bool(landmarks) and len(landmarks) >= 33


def get_lunge_angles(landmarks):
    """
    Returns angles relevant to lunges:
        - front_knee (angle at knee of the forward leg)
        - back_knee (angle at knee of the back leg)
        - front_hip (hip angle on forward leg)
        - torso_angle (shoulder-hip-ankle) average of sides for torso lean
    """
    angles = {}
    if not _has_enough_landmarks(landmarks):
        return angles

    # Right leg as front
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    if val is not None:
        angles['right_knee'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    if val is not None:
        angles['left_knee'] = val

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    )
    if val is not None:
        angles['right_hip'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    )
    if val is not None:
        angles['left_hip'] = val

    # Torso lean: angle between shoulder-hip-ankle for both sides averaged
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    right_torso = val if val is not None else 180.0
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    left_torso = val if val is not None else 180.0
    angles['torso_angle'] = (right_torso + left_torso) / 2.0
    return angles


def get_deadlift_angles(landmarks):
    """
    Returns angles relevant to deadlifts:
        - hip_angle (shoulder-hip-knee)
        - back_angle (shoulder-hip-ankle)
        - knee_angle (hip-knee-ankle)
    """
    angles = {}
    if not _has_enough_landmarks(landmarks):
        return angles

    # Both sides
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    )
    if val is not None:
        angles['right_hip'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    )
    if val is not None:
        angles['left_hip'] = val

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    if val is not None:
        angles['right_back'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    if val is not None:
        angles['left_back'] = val

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    if val is not None:
        angles['right_knee'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    if val is not None:
        angles['left_knee'] = val
    return angles


def get_pushup_angles(landmarks):
    """
    Returns angles for pushups:
        - left_elbow, right_elbow (shoulder-elbow-wrist)
        - body_angle (shoulder-hip-ankle average) to check straightness
    """
    angles = {}
    if not _has_enough_landmarks(landmarks):
        return angles

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    )
    if val is not None:
        angles['right_elbow'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    )
    if val is not None:
        angles['left_elbow'] = val

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    right_body = val if val is not None else 180.0
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    left_body = val if val is not None else 180.0
    angles['body_angle'] = (right_body + left_body) / 2.0
    return angles


def get_shoulder_press_angles(landmarks):
    """
    Returns angles for shoulder press:
        - left_shoulder_elbow (elbow angle)
        - right_shoulder_elbow
        - shoulder_abduction_estimate (shoulder-hip-elbow)
    """
    angles = {}
    if not _has_enough_landmarks(landmarks):
        return angles

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    )
    if val is not None:
        angles['right_elbow'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    )
    if val is not None:
        angles['left_elbow'] = val

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    )
    if val is not None:
        angles['right_shoulder_abd'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    )
    if val is not None:
        angles['left_shoulder_abd'] = val
    return angles


def get_bicep_curl_angles(landmarks):
    """
    Returns angles for bicep curls:
        - left_elbow, right_elbow (shoulder-elbow-wrist)
        - left_shoulder_to_wrist (shoulder-elbow-wrist oriented)
    """
    angles = {}
    if not _has_enough_landmarks(landmarks):
        return angles

    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    )
    if val is not None:
        angles['right_elbow'] = val
    val = _safe_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    )
    if val is not None:
        angles['left_elbow'] = val
    return angles


# Mapping for dynamic dispatch from websocket
ANGLE_FUNCTIONS = {
    'squat': get_squat_angles,
    'lunge': get_lunge_angles,
    'deadlift': get_deadlift_angles,
    'pushup': get_pushup_angles,
    'shoulder_press': get_shoulder_press_angles,
    'bicep_curl': get_bicep_curl_angles,
}


def get_angles_for_exercise(exercise, landmarks):
    """Return angles dict for the given exercise using mapping above.
    If exercise not found or landmarks missing, return empty dict.
    """
    fn = ANGLE_FUNCTIONS.get(exercise)
    if not fn:
        return {}
    return fn(landmarks)


# Create a default processor instance to be reused by the websocket handler.
DEFAULT_POSE_PROCESSOR = PoseProcessor()