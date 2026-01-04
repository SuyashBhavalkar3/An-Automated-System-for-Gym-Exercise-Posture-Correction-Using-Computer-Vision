from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64

from posture import mediapipe_utils, visualizer, feedback as feedback_module

router = APIRouter()

@router.websocket("/ws/posture")
async def posture_ws(websocket: WebSocket):
    """
    WebSocket endpoint for real-time posture correction.
    Client sends:
        {
            "exercise": "squat",
            "frame": "<base64_image>"
        }
    Server responds:
        {
            "feedback": ["Keep your back straight", ...],
            "skeleton_frame": "<base64_image_with_skeleton>"
        }
    """
    await websocket.accept()

    try:
        while True:
            # Receive JSON from client
            data = await websocket.receive_json()
            exercise = data.get("exercise", "squat")
            frame_b64 = data.get("frame")

            if not frame_b64:
                await websocket.send_json({
                    "feedback": ["No frame received."],
                    "skeleton_frame": None
                })
                continue

            # Convert base64 frame to OpenCV image
            frame_bytes = np.frombuffer(base64.b64decode(frame_b64), dtype=np.uint8)
            frame = cv2.imdecode(frame_bytes, cv2.IMREAD_COLOR)

            # Get pose landmarks using MediaPipe
            pose_landmarks, landmarks_list = mediapipe_utils.get_pose_landmarks(frame)

            # Default feedback
            feedback = ["No person detected. Please make sure you are in frame."]
            skeleton_frame = None

            if pose_landmarks and landmarks_list:
                # Calculate angles for squat safely
                angles = mediapipe_utils.get_squat_angles(landmarks_list)

                if not angles:
                    feedback = ["Please get fully into the frame."]
                else:
                    feedback = feedback_module.generate_feedback(exercise, angles)

                # Draw skeleton regardless of angles availability
                skeleton_frame = visualizer.draw_skeleton(frame, pose_landmarks)

            # Send response back to client
            await websocket.send_json({
                "feedback": feedback,
                "skeleton_frame": skeleton_frame
            })

    except WebSocketDisconnect:
        print("Client disconnected")