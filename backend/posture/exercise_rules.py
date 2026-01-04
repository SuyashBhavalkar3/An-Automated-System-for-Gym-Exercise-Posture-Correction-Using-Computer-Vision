def check_squat_rules(angles):
    """
    Rules for squat:
        - Knee angle should be ~90° at bottom
        - Hip angle should be >70° (back straight)
    """
    feedback = []

    if angles['right_knee'] > 100 or angles['left_knee'] > 100:
        feedback.append("Bend your knees more")
    if angles['right_knee'] < 60 or angles['left_knee'] < 60:
        feedback.append("Don't go too low")
    
    if angles['right_hip'] < 70 or angles['left_hip'] < 70:
        feedback.append("Keep your back straighter")
    
    if not feedback:
        feedback.append("Good squat form!")
    return feedback