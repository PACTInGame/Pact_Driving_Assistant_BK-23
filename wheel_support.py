try:
    from vjoy import vj, setJoy
except:
    print("ERROR LOADING VJOY. VJOY IS MANDATORY FOR AUTO-BRAKE WITH CONTROLLER.")


def brake():
    vj.open()

    # valueX(brake), valueY(throttle) between -1000 and 1000, 1000 = 0%, -1000 = 100%
    # scale between 0 and 16000

    scale = 16.39
    zPos = 0 + 23
    xPos = -1000
    yPos = 1000
    xPos = xPos + 23
    yPos = yPos + 23
    setJoy(xPos, yPos, zPos, scale)
    vj.close()


def brake_slow():
    vj.open()

    # valueX(brake), valueY(throttle) between -1000 and 1000, 1000 = 0%, -1000 = 100%
    # scale between 0 and 16000

    scale = 16.39
    zPos = 0 + 23
    xPos = 0
    yPos = 1000
    xPos = xPos + 23
    yPos = yPos + 23
    setJoy(xPos, yPos, zPos, scale)
    vj.close()


def brake_slow_steer(steer):
    vj.open()

    # valueX(brake), valueY(throttle) between -1000 and 1000, 1000 = 0%, -1000 = 100%
    # scale between 0 and 16000

    scale = 16.39
    zPos = steer * 5 + 23
    xPos = 0
    yPos = 1000
    xPos = xPos + 23
    yPos = yPos + 23
    setJoy(xPos, yPos, zPos, scale)
    vj.close()


def steer(steer):
    vj.open()

    # valueX(brake), valueY(throttle) between -1000 and 1000, 1000 = 0%, -1000 = 100%
    # scale between 0 and 16000

    scale = 16.39
    zPos = steer * 5 + 23
    xPos = 0
    yPos = 1000
    xPos = xPos + 23
    yPos = yPos + 23
    setJoy(xPos, yPos, zPos, scale)
    vj.close()


def brake_psc_rwd():
    vj.open()

    # valueX(brake), valueY(throttle) between -1000 and 1000, 1000 = 0%, -1000 = 100%
    # scale between 0 and 16000

    scale = 16.39
    zPos = 0 + 23
    xPos = 0
    yPos = 1000
    xPos = xPos + 23
    yPos = yPos + 23
    setJoy(xPos, yPos, zPos, scale)
    vj.close()


def acc_control(acc_br):
    vj.open()
    if acc_br < 0:
        acc_br = acc_br + 50
        acc_br = acc_br * 20
        xPos = acc_br
        yPos = 1000

    else:
        acc_br = acc_br - 50
        acc_br = acc_br * -20
        xPos = 1000
        yPos = acc_br


    # valueX(brake), valueY(throttle) between -1000 and 1000, 1000 = 0%, -1000 = 100%
    # scale between 0 and 16000

    scale = 16.39
    zPos = 0 + 23
    xPos = xPos + 23
    yPos = yPos + 23
    setJoy(xPos, yPos, zPos, scale)
    vj.close()
