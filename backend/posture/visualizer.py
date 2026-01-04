import mediapipe as mp
import cv2
import logging
import os

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

logger = logging.getLogger("posture.visualizer")


def draw_skeleton_bytes(frame, pose_landmarks=None, landmarks_list=None, draw=True):
    """Draw skeleton onto frame and return JPEG bytes.

    - `pose_landmarks`: MediaPipe pose_landmarks object (preferred)
    - `landmarks_list`: list of landmarks (fallback if pose_landmarks not available)
    - `draw`: allow disabling drawing via connection meta or env var

    Returns raw JPEG bytes (not base64). Caller may encode to base64 if needed.
    This function is defensive: partial or missing landmarks won't crash it.
    """
    if not draw or frame is None:
        # encode original frame
        _, buf = cv2.imencode('.jpg', frame)
        return buf.tobytes()

    annotated = frame.copy()
    try:
        if pose_landmarks is not None:
            # Safe draw; MediaPipe drawing handles visibility flags.
            mp_drawing.draw_landmarks(
                annotated,
                pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )
            _, buf = cv2.imencode('.jpg', annotated)
            return buf.tobytes()

        # Fallback: draw individual landmarks if given a list
        if landmarks_list:
            h, w = annotated.shape[:2]
            for i, lm in enumerate(landmarks_list):
                try:
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    cv2.circle(annotated, (x, y), 3, (0, 255, 0), -1)
                except Exception:
                    # ignore malformed landmark
                    continue

            # draw simple connections
            for a, b in mp_pose.POSE_CONNECTIONS:
                try:
                    a_lm = landmarks_list[a]
                    b_lm = landmarks_list[b]
                    ax = int(a_lm.x * w)
                    ay = int(a_lm.y * h)
                    bx = int(b_lm.x * w)
                    by = int(b_lm.y * h)
                    cv2.line(annotated, (ax, ay), (bx, by), (0, 200, 255), 2)
                except Exception:
                    continue

        _, buf = cv2.imencode('.jpg', annotated)
        return buf.tobytes()
    except Exception:
        logger.exception("Error drawing skeleton; returning original frame bytes")
        _, buf = cv2.imencode('.jpg', frame)
        return buf.tobytes()


def bytes_to_base64_jpeg(jpeg_bytes):
    import base64
    return base64.b64encode(jpeg_bytes).decode('utf-8')