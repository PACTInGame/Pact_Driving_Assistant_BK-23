from shapely.geometry import Point


def calculate_steering(r, l, x, y, prev, prev2):
    steer = 0

    for p in r:
        point = Point(x, y)
        if p[1].contains(point):
            print("r")
            steer = -0.5
        elif p[1].contains(point):
            print("r1")
            steer = -2.25
        elif p[2].contains(point):
            print("r2")
            steer = -2.5
        elif p[3].contains(point):
            print("r3")
            steer = -2.75
        elif p[4].contains(point):
            print("r4")
            steer = -3
        elif p[5].contains(point):
            print("r5")
            steer = -3.5
        elif p[6].contains(point):
            print("r6")
            steer = -5
        elif prev2 <= -3.5 and steer == 0:
            steer = -10

    for p in l:
        point = Point(x, y)
        if p[1].contains(point):
            print("l")
            steer = 0.5
        elif p[1].contains(point):
            print("l1")
            steer = 2.25
        elif p[2].contains(point):
            print("l2")
            steer = 2.5
        elif p[3].contains(point):
            print("l3")
            steer = 2.75
        elif p[4].contains(point):
            print("l4")
            steer = 3
        elif p[5].contains(point):
            print("l5")
            steer = 3.5
        elif p[6].contains(point):
            print("l6")
            steer = 5
        elif prev2 >= 3.5 and steer == 0:
            steer = 10

    actual = steer
    if steer != 0:
        if prev2 > steer > 0 or prev2 < steer < 0:
            steer = steer * -2

    return steer, actual
