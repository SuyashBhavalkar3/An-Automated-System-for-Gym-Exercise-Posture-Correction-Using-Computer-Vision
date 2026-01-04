from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
import json
import time
import os
import logging
import traceback

from posture import mediapipe_utils, visualizer, feedback as feedback_module

router = APIRouter()

logger = logging.getLogger("posture.websocket")
VERBOSE = os.getenv("VERBOSE_LOGGING", "false").lower() in ("1", "true", "yes")
if VERBOSE:
    logging.basicConfig(level=logging.DEBUG)

# Throttle / resize defaults (tunable via env)
WS_TARGET_FPS = float(os.getenv("WS_TARGET_FPS", "18"))
FRAME_MAX_WIDTH = int(os.getenv("FRAME_MAX_WIDTH", "640"))
ENABLE_SKELETON = os.getenv("ENABLE_SKELETON", "true").lower() in ("1", "true", "yes")


def _resize_for_processing(frame, max_width=FRAME_MAX_WIDTH):
    if frame is None:
        return None
    h, w = frame.shape[:2]
    if w <= max_width:
        return frame
    scale = max_width / float(w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(frame, (new_w, new_h))


@router.websocket("/ws/posture")
async def posture_ws(websocket: WebSocket):
    """WebSocket endpoint for posture testing with binary support and throttling.

    Protocol (backwards compatible):
      - Client may send JSON messages with base64 frames (old).
      - Client can send a JSON 'meta' message to set `exercise` or toggles.
      - Client can send raw binary JPEG frames (preferred) which reduces base64 overhead.

    Server behavior:
      - Reuses MediaPipe processor for performance
      - Throttles processing to ~WS_TARGET_FPS
      - Sends feedback JSON and, when the client sent binary frames, a subsequent binary skeleton JPEG
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    # Reuse a pose processor instance created in mediapipe_utils
    pose_processor = getattr(mediapipe_utils, "DEFAULT_POSE_PROCESSOR", None)
    if pose_processor is None:
        pose_processor = mediapipe_utils.PoseProcessor()

    exercise = None
    last_processed = 0.0
    last_feedback = ["No frames processed yet."]
    last_skeleton = None
    client_prefers_binary = False
    skeleton_enabled = ENABLE_SKELETON

    try:
        while True:
            msg = await websocket.receive()

            # Determine whether the client sent text (JSON) or binary
            frame = None
            received_binary = False

            if "text" in msg and msg.get("text"):
                try:
                    data = json.loads(msg.get("text"))
                except Exception:
                    logger.exception("Invalid JSON received on websocket")
                    await websocket.send_json({"error": "invalid json"})
                    continue
                # If message contains exercise, update current exercise for this session
                if 'exercise' in data:
                    prev = exercise
                    exercise = data.get("exercise", exercise)
                    if exercise != prev:
                        logger.info(f"Exercise changed for session: {prev} -> {exercise}")

                # meta control message (explicit)
                if data.get("type") == "meta":
                    # type meta may also include exercise and toggles
                    exercise = data.get("exercise", exercise)
                    skeleton_enabled = data.get("skeleton", skeleton_enabled)
                    if data.get("verbose") is not None:
                        # allow client to enable verbose logging for debugging
                        v = data.get("verbose")
                        if v:
                            logger.setLevel(logging.DEBUG)
                    logger.info(f"Meta updated: exercise={exercise}, skeleton={skeleton_enabled}")
                    await websocket.send_json({"meta_ack": True})
                    continue

                frame_b64 = data.get("frame")
                if frame_b64:
                    try:
                        frame_bytes = base64.b64decode(frame_b64)
                        frame_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
                        frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)
                        logger.debug(f"Received base64 frame for exercise={exercise}")
                    except Exception:
                        logger.exception("Error decoding base64 frame")
                        await websocket.send_json({"error": "frame decode error"})
                        continue

            elif "bytes" in msg and msg.get("bytes"):
                # Raw JPEG bytes received (preferred path)
                received_binary = True
                client_prefers_binary = True
                try:
                    frame_arr = np.frombuffer(msg.get("bytes"), dtype=np.uint8)
                    frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)
                    logger.debug(f"Received binary frame for exercise={exercise}")
                except Exception:
                    logger.exception("Error decoding binary frame")
                    await websocket.send_json({"error": "frame decode error"})
                    continue
            else:
                # Unknown or empty message
                logger.debug("Empty or unsupported websocket message received")
                continue

            # Resize for performance before sending to MediaPipe
            proc_frame = _resize_for_processing(frame)

            now = time.time()
            elapsed = now - last_processed
            min_interval = 1.0 / float(WS_TARGET_FPS) if WS_TARGET_FPS > 0 else 0

            if elapsed < min_interval:
                # Throttled: return last cached results (keeps client responsive)
                logger.debug(f"Throttling frame; elapsed={elapsed:.4f}s, min={min_interval:.4f}s")
                # send cached feedback + skeleton (if available)
                if client_prefers_binary and last_skeleton is not None:
                    # send feedback JSON then binary skeleton
                    await websocket.send_json({"feedback": last_feedback, "skeleton_binary": True})
                    await websocket.send_bytes(last_skeleton)
                else:
                    # base64 encode skeleton if present
                    sk_b64 = None
                    if last_skeleton is not None:
                        sk_b64 = visualizer.bytes_to_base64_jpeg(last_skeleton)
                    await websocket.send_json({"feedback": last_feedback, "skeleton_frame": sk_b64, "throttled": True})
                continue

            # Process with MediaPipe
            try:
                start_proc = time.time()
                pose_landmarks, landmarks_list = pose_processor.process(proc_frame)
                proc_time = time.time() - start_proc
                logger.debug(f"MediaPipe processed frame in {proc_time:.3f}s; landmarks={'yes' if landmarks_list else 'no'})")
            except Exception:
                logger.exception("MediaPipe processing error")
                pose_landmarks, landmarks_list = None, None

            # Default responses
            feedback = ["No person detected. Please make sure you are in frame."]
            skeleton_bytes = None

            if pose_landmarks and landmarks_list:
                # Count visible landmarks for debug
                try:
                    vis_count = sum(1 for lm in landmarks_list if getattr(lm, 'visibility', 1.0) > 0.2)
                except Exception:
                    vis_count = len(landmarks_list)
                logger.debug(f"Landmarks visible: {vis_count}/{len(landmarks_list)}")

                # Calculate angles for requested exercise via mediapipe_utils
                if not exercise:
                    feedback = ["No exercise selected. Please choose an exercise in the UI."]
                    logger.debug("No exercise selected for session")
                else:
                    angles = mediapipe_utils.get_angles_for_exercise(exercise, landmarks_list)
                    logger.debug(f"Angles for {exercise}: {angles}")

                    if not angles:
                        feedback = ["Please get fully into the frame."]
                        logger.debug("Angles missing or incomplete; can't compute full feedback")
                    else:
                        feedback = feedback_module.generate_feedback(exercise, angles)
                        logger.debug(f"Generated feedback: {feedback}")

            # Draw skeleton unconditionally if enabled (defensive)
            try:
                skeleton_bytes = visualizer.draw_skeleton_bytes(proc_frame, pose_landmarks=pose_landmarks, landmarks_list=landmarks_list, draw=skeleton_enabled)
            except Exception:
                logger.exception("Error drawing skeleton")
                skeleton_bytes = visualizer.draw_skeleton_bytes(proc_frame, draw=False)

            # Cache results and update timestamp
            last_processed = now
            last_feedback = feedback
            last_skeleton = skeleton_bytes

            # Send response back to client: prefer binary skeleton if client sent binary
            try:
                if client_prefers_binary:
                    # send feedback JSON then skeleton as binary
                    await websocket.send_json({"feedback": feedback, "skeleton_binary": True})
                    if skeleton_bytes is not None:
                        await websocket.send_bytes(skeleton_bytes)
                else:
                    sk_b64 = None
                    if skeleton_bytes is not None:
                        sk_b64 = visualizer.bytes_to_base64_jpeg(skeleton_bytes)
                    await websocket.send_json({"feedback": feedback, "skeleton_frame": sk_b64})
                logger.info("Sent feedback and skeleton to client")
            except Exception:
                logger.exception("Error sending websocket response")

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception:
        logger.exception("Unhandled error in websocket loop")