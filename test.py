import pygame
import time


def write_settings():
    file_string = "Important: DO NOT CHANGE THIS FILE MANUALLY. PLEASE USE SETUP_CRUISE_CONTROL.exe\n" \
                  "{} Throttle Axis\n" \
                  "{} Brake Axis\n" \
                  "{} Joystick".format(throttle_axis, brake_axis, num_joystick)

    try:
        with open('acc_settings.txt', 'w') as file:
            file.write(file_string)
        print("Settings saved successfully")
    except:
        print("An Error has occurred during saving. Make sure acc_settings.txt exists and you have enough rights.")


print("Hello")
print("This setup will guide you through setting up the PACT Driving Assistant Cruise Control")
time.sleep(1)
print("Please DO NOT touch your racing wheel or pedals until instructed to do so!")
time.sleep(2)
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
time.sleep(2)
if len(joysticks) > 0:
    print("I've detected the following controllers: ")
    for joystick in joysticks:
        print(joystick.get_name() + " ")
else:
    print("Error, no game-pads/wheels/controllers detected. \n Please make sure your wheel is turned on and retry!")

pygame.init()
time.sleep(4)
print("please press your THROTTLE axis now.")
brake_axis = -1
throttle_axis = -1
num_joystick = -1
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            throttle_axis = event.axis
            num_joystick = event.joy
    if throttle_axis != -1:
        break
print("I have detected your throttle axis! It is axis " + str(throttle_axis) + ".")
time.sleep(4)
print("please press your BRAKE axis now.")
loops = 5
while True:
    for event in pygame.event.get():
        if loops < 0:
            if event.type == pygame.JOYAXISMOTION:
                brake_axis = event.axis
    loops -= 1
    if brake_axis != -1:
        break

print("I have detected your brake axis! It is axis " + str(brake_axis) + ".")
time.sleep(2)
print("Your settings will be saved. If you want to retry the setup, just restart this file!")
write_settings()
time.sleep(5)
print("Closing Setup now")
time.sleep(2)
