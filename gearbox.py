import pyautogui
from threading import Thread

pyautogui.FAILSAFE = False

keys = ["s", "x", "i"]
try:
    with open("controls.txt") as fp:
        for i, line in enumerate(fp):
            if 1 <= i <= 3:
                line = line.split()
                keys[i - 1] = line[0]

except:
    pass


def get_gear(acceleration, brake, gear, rpm, redline, max_gears, vehicle_model):
    if vehicle_model == b"FZ5":
        if acceleration < 0.2:
            rpm_set = 2000
        elif acceleration < 0.4:
            rpm_set = 2400
        elif acceleration < 0.6:
            rpm_set = 2800
        elif acceleration < 0.7:
            rpm_set = 3200
        elif acceleration < 0.8:
            rpm_set = 3700
        elif acceleration < 0.9:
            rpm_set = 4500
        elif acceleration < 0.95:
            rpm_set = 5000
        elif acceleration > 0.94:
            rpm_set = 6200
        else:
            rpm_set = 2000
        if brake > 0.95:
            rpm_set = rpm_set + 3500

        elif brake > 0.8:
            rpm_set = rpm_set + 2000

        elif brake > 0.5:
            rpm_set = rpm_set + 1000

        if rpm_set > 6200:
            rpm_set = 6200

        if rpm < rpm_set - 3000:
            gear_to_be = gear - 3
        elif rpm < rpm_set - 2000:
            gear_to_be = gear - 2
        elif rpm < rpm_set - 1000:
            gear_to_be = gear - 1
        elif rpm > rpm_set + 1600:
            gear_to_be = gear + 1
        else:
            gear_to_be = gear
    elif vehicle_model == b'\x98a\x10':
        if acceleration < 0.2:
            rpm_set = 1000
        elif acceleration < 0.4:
            rpm_set = 1300
        elif acceleration < 0.6:
            rpm_set = 1400
        elif acceleration < 0.7:
            rpm_set = 1600
        elif acceleration < 0.8:
            rpm_set = 1800
        elif acceleration < 0.9:
            rpm_set = 1900
        elif acceleration < 0.95:
            rpm_set = 2000
        elif acceleration > 0.94:
            rpm_set = 2150
        else:
            rpm_set = 2000
        if brake > 0.95:
            rpm_set = rpm_set + 700

        elif brake > 0.8:
            rpm_set = rpm_set + 600

        elif brake > 0.5:
            rpm_set = rpm_set + 400

        if rpm_set > 2150:
            rpm_set = 2150
        if acceleration > 0.1:
            if rpm < rpm_set - 800:
                gear_to_be = gear - 1
            elif rpm > rpm_set + 50:
                gear_to_be = gear + 1
            else:
                gear_to_be = gear
        else:
            if rpm < rpm_set - 100:
                gear_to_be = gear - 1
            elif rpm > rpm_set + 50:
                gear_to_be = gear + 1
            else:
                gear_to_be = gear

    if gear_to_be < 2:
        gear_to_be = 2
    if gear_to_be > max_gears + 1:
        gear_to_be = max_gears + 1

    return gear_to_be


def shift_up():
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])
    pyautogui.keyDown(keys[0])
    pyautogui.keyUp(keys[0])
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])


def shift_down():
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])
    pyautogui.keyDown(keys[1])
    pyautogui.keyUp(keys[1])
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])


def shift_down2():
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])
    pyautogui.keyDown(keys[1])
    pyautogui.keyUp(keys[1])
    pyautogui.keyDown(keys[1])
    pyautogui.keyUp(keys[1])
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])


def shift_down3():
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])
    pyautogui.keyDown(keys[1])
    pyautogui.keyUp(keys[1])
    pyautogui.keyDown(keys[1])
    pyautogui.keyUp(keys[1])
    pyautogui.keyDown(keys[1])
    pyautogui.keyUp(keys[1])
    pyautogui.keyDown(keys[2])
    pyautogui.keyUp(keys[2])


def shift(gear, own_gear, acc, steer):
    if own_gear > gear + 2:
        thread_shiftd = Thread(target=shift_down3)
        thread_shiftd.start()
    elif own_gear > gear + 1:
        thread_shiftd = Thread(target=shift_down2)
        thread_shiftd.start()
    elif own_gear > gear:
        thread_shiftd = Thread(target=shift_down)
        thread_shiftd.start()
    elif own_gear < gear and acc > 0 and -800 <= steer <= 800:
        thread_shiftd = Thread(target=shift_up)
        thread_shiftd.start()
