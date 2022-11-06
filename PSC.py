def calculateStabilityControl(speed, steering, previous_steering):
    # negative right, positive left
    #steer
    #30 = 3100
    #50 = 1700
    #90 = 1050
    #120 = 850
    #150 = 800
    #190 = 600

    #evade diff
    # from 60
    # 70 1500
    # 95 1400
    # 120 900
    steer_threshold = 5000
    if 90 > speed > 25:
        steer_threshold = ((-22) * speed) + 3400



    if abs(steering) > steer_threshold:
        return True
    else:
        return False