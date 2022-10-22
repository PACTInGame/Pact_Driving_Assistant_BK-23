import pygame
import time

for i in range(500):
    pygame.init()
    joysticks = list()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joysticks.append(joystick)

    pygame.event.pump()

    print (joystick.get_axis(1))
    time.sleep(0.01)
