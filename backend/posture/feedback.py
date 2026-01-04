def generate_squat_feedback(angles):
    """
    Generates human-friendly feedback for squat exercise.
    angles: dict of angles calculated from mediapipe_utils
    Returns: list of feedback strings
    """
    feedback = []

    # Knee angles
    if angles['right_knee'] > 100 or angles['left_knee'] > 100:
        feedback.append("Bend your knees more to reach proper squat depth.")
    if angles['right_knee'] < 60 or angles['left_knee'] < 60:
        feedback.append("You're going too low! Keep knees above 60 degrees.")

    # Hip/back angles
    if angles['right_hip'] < 70 or angles['left_hip'] < 70:
        feedback.append("Keep your back straighter to protect your spine.")

    # If everything is good
    if not feedback:
        feedback.append("Excellent squat! Keep that form.")

    return feedback


def generate_feedback(exercise, angles):
    """
    Generic function to generate feedback based on exercise type.
    You can expand it for other exercises later.
    """
    if exercise == "squat":
        return generate_squat_feedback(angles)
    elif exercise == "lunge":
        return generate_lunge_feedback(angles)
    elif exercise == "deadlift":
        return generate_deadlift_feedback(angles)
    elif exercise == "pushup":
        return generate_pushup_feedback(angles)
    elif exercise == "shoulder_press":
        return generate_shoulder_press_feedback(angles)
    elif exercise == "bicep_curl":
        return generate_bicep_curl_feedback(angles)
    else:
        return ["Exercise not supported yet."]


def generate_lunge_feedback(angles):
    feedback = []
    if not angles:
        return ["Please get fully into the frame."]

    # Knee depth
    if angles.get('right_knee', 180) > 150 and angles.get('left_knee', 180) > 150:
        feedback.append("Bend your front knee more to lower into the lunge.")
    if angles.get('right_knee', 0) < 50 or angles.get('left_knee', 0) < 50:
        feedback.append("Avoid dropping too low; control your depth.")

    # Torso uprightness
    if angles.get('torso_angle', 180) < 70:
        feedback.append("Keep your torso more upright; avoid leaning forward.")

    if not feedback:
        feedback.append("Good lunge form. Keep it controlled.")
    return feedback


def generate_deadlift_feedback(angles):
    feedback = []
    if not angles:
        return ["Please get fully into the frame."]

    # Back straightness: want large back angle (closer to 180)
    if angles.get('right_back', 180) < 140 or angles.get('left_back', 180) < 140:
        feedback.append("Keep your back straighter; hinge at the hips, not the spine.")

    # Hip hinge: hip angle should show hinge but not extreme
    if angles.get('right_hip', 180) < 30 or angles.get('left_hip', 180) < 30:
        feedback.append("Drive the movement with your hips; push them back.")

    # Knee position: avoid excessive knee bend
    if angles.get('right_knee', 0) < 120 or angles.get('left_knee', 0) < 120:
        feedback.append("Don't bend your knees too much; maintain a slight bend.")

    if not feedback:
        feedback.append("Nice deadlift posture — maintain the hip hinge and straight back.")
    return feedback


def generate_pushup_feedback(angles):
    feedback = []
    if not angles:
        return ["Please get fully into the frame."]

    # Body straightness
    if angles.get('body_angle', 180) < 160:
        feedback.append("Keep your body straight from head to heels.")

    # Elbow depth guidance
    if angles.get('right_elbow', 180) > 160 and angles.get('left_elbow', 180) > 160:
        feedback.append("Lower your chest more to increase muscle engagement.")
    if angles.get('right_elbow', 0) < 60 or angles.get('left_elbow', 0) < 60:
        feedback.append("Control the descent; don't drop too quickly.")

    if not feedback:
        feedback.append("Good pushup form — full range and a straight body.")
    return feedback


def generate_shoulder_press_feedback(angles):
    feedback = []
    if not angles:
        return ["Please get fully into the frame."]

    # Elbow lockout
    if angles.get('right_elbow', 0) < 160 or angles.get('left_elbow', 0) < 160:
        feedback.append("Extend your arms fully at the top for full lockout.")

    # Keep shoulder alignment
    if angles.get('right_shoulder_abd', 180) < 60 or angles.get('left_shoulder_abd', 180) < 60:
        feedback.append("Keep your elbows in line and press vertically.")

    if not feedback:
        feedback.append("Good shoulder press — stable torso and full extension.")
    return feedback


def generate_bicep_curl_feedback(angles):
    feedback = []
    if not angles:
        return ["Please get fully into the frame."]

    # Elbow flexion guidance
    if angles.get('right_elbow', 180) > 160 and angles.get('left_elbow', 180) > 160:
        feedback.append("Extend your arms fully to complete the negative.")
    if angles.get('right_elbow', 0) < 40 or angles.get('left_elbow', 0) < 40:
        feedback.append("Squeeze at the top of the curl; control the motion.")

    if not feedback:
        feedback.append("Nice curls — controlled tempo and full range.")
    return feedback