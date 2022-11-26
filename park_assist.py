import math
import time
from shapely.geometry.polygon import Polygon
from threading import Thread
import winsound
import helpers


def get_size(cn):
    l = 4.6
    w = 2
    if cn == b'\x98a\x10': #Karobus
        l = 11.2
        w = 2.75
    elif cn == b'\xb6i\xbd': #Luxury sedan
        l = 5.1
    elif cn == b'UF1':
        l = 3.1
        w = 1.6
    elif cn == b'XFG':
        l = 3.7
        w = 1.7
    elif cn == b'RB4':
        l = 4.5
        w = 1.8
    elif cn == b'>\x8c\x88': # bumer 7
        l = 5.2
        w = 1.9
    elif cn == b'K\xd2c': # Uf Pickup
        l = 5.2
        w = 2.2
    elif cn == b'\xa4\xc2\xf3':  # Line Runner
        l = 7.6
        w = 2.3
    elif cn == b'\xe3\x94\xf4':  # SCAMA K460
        l = 13.5
        w = 2.5
    return l, w


def calc_polygon_points(own_x, own_y, length, angle):
    return own_x + length * math.cos(math.radians(angle)), own_y + length * math.sin(math.radians(angle))


def refactor_angle(angle):
    if angle > 360:
        return angle - 360
    else:
        return angle


def create_rectangles_for_others(cars):
    rectangles = []

    for car in cars:
        print(car[0].cname)
        angle_of_car = (car[0].heading - 16384) / 182.05
        length, width = get_size(car[0].cname)
        if angle_of_car < 0:
            angle_of_car *= -1
        a1 = math.atan((width / 2) / (length / 2)) * 180 / math.pi
        ang1 = angle_of_car + a1
        ang2 = angle_of_car + (180 - a1)
        ang3 = angle_of_car + (180 + a1)
        ang4 = angle_of_car + (360 - a1)
        diagonal = (length / 2) ** 2 + (width / 2) ** 2
        diagonal = math.sqrt(diagonal)
        (x1, y1) = calc_polygon_points(car[0].x, car[0].y, (diagonal + 0.1) * 65536, ang1)  # front right
        (x2, y2) = calc_polygon_points(car[0].x, car[0].y, (diagonal + 0.1) * 65536, ang2)  # rear right
        (x3, y3) = calc_polygon_points(car[0].x, car[0].y, (diagonal + 0.1) * 65536, ang3)  # rear left
        (x4, y4) = calc_polygon_points(car[0].x, car[0].y, (diagonal + 0.1) * 65536, ang4)  # front left

        rectangles.append((car[1], Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])))

    return rectangles


def sensors(cars, own_x, own_y, own_heading, model):
    sensordata = []
    closest_distance = 4
    angle = 0
    angle_of_car = (own_heading - 16384) / 182.05
    if angle_of_car < 0:
        angle_of_car *= -1
    length, width = get_size(model)
    a1 = math.atan((width / 2) / (length / 2)) * 180 / math.pi
    ang1 = angle_of_car + a1
    ang2 = angle_of_car + (180 - a1)
    ang3 = angle_of_car + (180 + a1)
    ang4 = angle_of_car + (360 - a1)
    ang1 = refactor_angle(ang1)
    ang2 = refactor_angle(ang2)
    ang3 = refactor_angle(ang3)
    ang4 = refactor_angle(ang4)
    diagonal = (length / 2) ** 2 + (width / 2) ** 2
    diagonal = math.sqrt(diagonal)
    (x1, y1) = calc_polygon_points(own_x, own_y, (diagonal + 0.1) * 65536, ang1)  # front left
    (x2, y2) = calc_polygon_points(own_x, own_y, (diagonal + 0.1) * 65536, ang2)  # rear left
    (x3, y3) = calc_polygon_points(own_x, own_y, (diagonal + 0.1) * 65536, ang3)  # rear right
    (x4, y4) = calc_polygon_points(own_x, own_y, (diagonal + 0.1) * 65536, ang4)  # front right
    (x5, y5) = calc_polygon_points(own_x, own_y, (diagonal + 1) * 65536, ang1)
    (x6, y6) = calc_polygon_points(own_x, own_y, (diagonal + 1) * 65536, ang2)
    (x7, y7) = calc_polygon_points(own_x, own_y, (diagonal + 1) * 65536, ang3)
    (x8, y8) = calc_polygon_points(own_x, own_y, (diagonal + 1) * 65536, ang4)
    (x9, y9) = calc_polygon_points(own_x, own_y, (diagonal + 2) * 65536, ang1)
    (x10, y10) = calc_polygon_points(own_x, own_y, (diagonal + 2) * 65536, ang2)
    (x11, y11) = calc_polygon_points(own_x, own_y, (diagonal + 2) * 65536, ang3)
    (x12, y12) = calc_polygon_points(own_x, own_y, (diagonal + 2) * 65536, ang4)
    (x13, y13) = calc_polygon_points(own_x, own_y, (diagonal + 3) * 65536, ang4)
    (x14, y14) = calc_polygon_points(own_x, own_y, (diagonal + 3) * 65536, ang1)
    (x15, y15) = calc_polygon_points(own_x, own_y, (diagonal + 3) * 65536, ang2)
    (x16, y16) = calc_polygon_points(own_x, own_y, (diagonal + 3) * 65536, ang3)
    rectangle_close = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    rectangle_medium = Polygon([(x5, y5), (x6, y6), (x7, y7), (x8, y8)])
    rectangle_far = Polygon([(x9, y9), (x10, y10), (x11, y11), (x12, y12)])
    rectangle_very_far = Polygon([(x13, y13), (x14, y14), (x15, y15), (x16, y16)])
    rectangles_others = create_rectangles_for_others(cars)

    for rectangle in rectangles_others:
        if helpers.polygon_intersect(rectangle[1], rectangle_close):
            closest_distance = 0
            angle = rectangle[0]
        elif helpers.polygon_intersect(rectangle[1], rectangle_medium) and closest_distance > 0:
            closest_distance = 1
            angle = rectangle[0]
        elif helpers.polygon_intersect(rectangle[1], rectangle_far) and closest_distance > 1:
            closest_distance = 2
            angle = rectangle[0]
        elif helpers.polygon_intersect(rectangle[1], rectangle_very_far) and closest_distance > 2:
            closest_distance = 3
            angle = rectangle[0]

        sensordata.append((closest_distance, angle))

    return sensordata


def makesound(distance, angle):
    if angle < 90 or angle > 270:
        freq = 800
    else:
        freq = 500
    if distance < 4:
        if distance == 3:
            thread_beep = Thread(winsound.Beep(freq, 120))
            thread_beep.start()

        elif distance == 2:
            thread_beep = Thread(winsound.Beep(freq, 100))
            thread_beep.start()

        elif distance == 1:
            thread_beep = Thread(winsound.Beep(freq, 80))
            thread_beep.start()

        elif distance == 0:
            thread_beep = Thread(winsound.Beep(freq, 60))
            thread_beep.start()
