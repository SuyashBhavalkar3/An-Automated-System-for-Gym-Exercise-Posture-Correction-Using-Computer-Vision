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
    # elif exercise == "lunge":
    #     return generate_lunge_feedback(angles)
    # elif exercise == "deadlift":
    #     return generate_deadlift_feedback(angles)
    # add other exercises similarly
    else:
        return ["Exercise not supported yet."]