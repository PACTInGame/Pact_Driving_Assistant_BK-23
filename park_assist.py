import math
import time
from shapely.geometry.polygon import Polygon
from threading import Thread
import winsound
import helpers


def get_size(cn):
    size_map = {
        b'\x98a\x10': (11.2, 2.75),  # Karobus
        b'\xb6i\xbd': (5.1, 2),  # Luxury sedan
        b'UF1': (3.1, 1.6),
        b'XFG': (3.7, 1.7),
        b'RB4': (4.5, 1.8),
        b'>\x8c\x88': (5.2, 1.9),  # bumer 7
        b'K\xd2c': (5.2, 2.2),  # Uf Pickup
        b'\xa4\xc2\xf3': (7.6, 2.3),  # Line Runner
        b'\xe3\x94\xf4': (13.5, 2.5),  # SCAMA K460
    }

    return size_map.get(cn, (4.6, 2))


def calc_polygon_points(own_x, own_y, length, angle):
    return own_x + length * math.cos(math.radians(angle)), own_y + length * math.sin(math.radians(angle))


def refactor_angle(angle):
    if angle > 360:
        return angle - 360
    else:
        return angle


import math
from shapely.geometry import Polygon


def create_rectangles_for_others(cars):
    rectangles = []
    coeff = 65536

    def calc_polygon_point(x, y, distance, angle):
        x_new = x + distance * math.cos(math.radians(angle))
        y_new = y + distance * math.sin(math.radians(angle))
        return x_new, y_new

    for car in cars:
        angle_of_car = (car[0].heading - 16384) / 182.05
        angle_of_car = abs(angle_of_car)
        length, width = get_size(car[0].cname)

        a1 = math.degrees(math.atan((width / 2) / (length / 2)))
        ang1, ang2, ang3, ang4 = angle_of_car + a1, angle_of_car + (180 - a1), angle_of_car + (
                    180 + a1), angle_of_car + (360 - a1)

        diagonal = math.sqrt((length / 2) ** 2 + (width / 2) ** 2) + 0.1
        distance = diagonal * coeff
        corners = [calc_polygon_point(car[0].x, car[0].y, distance, angle) for angle in [ang1, ang2, ang3, ang4]]

        rectangles.append((car[1], Polygon(corners)))

    return rectangles


def sensors(cars, own_x, own_y, own_heading, model, rect_obj):
    sensordata = []
    closest_distance = 4
    angle = 0
    angle_of_car = abs((own_heading - 16384) / 182.05)
    length, width = get_size(model)
    coeff = 65536

    a1 = math.degrees(math.atan((width / 2) / (length / 2)))
    angles = [refactor_angle(angle_of_car + a) for a in [a1, 180 - a1, 180 + a1, 360 - a1]]

    diagonal = math.sqrt((length / 2) ** 2 + (width / 2) ** 2)
    distances = [(diagonal + i) * coeff for i in range(4)]

    polygons = [Polygon([calc_polygon_points(own_x, own_y, d, angle) for angle in angles]) for d in distances]

    rectangles_others = create_rectangles_for_others(cars)
    rectangles_others.extend(rect_obj)

    for rectangle in rectangles_others:
        for i, poly in enumerate(polygons):
            if helpers.polygon_intersect(rectangle[1], poly) and closest_distance > i:
                closest_distance = i
                angle = rectangle[0] if isinstance(rectangle[0], float) else helpers.calculate_angle(own_x,
                                                                                                     rectangle[0][0],
                                                                                                     own_y,
                                                                                                     rectangle[0][1],
                                                                                                     own_heading)

        sensordata.append((closest_distance, angle))

    return sensordata


def makesound(distance, angle):
    if angle < 90 or angle > 270:
        freq = 800
    else:
        freq = 500

    if distance < 4:
        duration = 140 - distance * 20
        thread_beep = Thread(target=winsound.Beep, args=(freq, duration))
        thread_beep.start()
