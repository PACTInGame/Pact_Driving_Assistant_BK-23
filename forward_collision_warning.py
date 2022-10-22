from shapely.geometry import Polygon

import helpers
from park_assist import calc_polygon_points


def calc_brake_distance(rel_speed, acc, br, dynamic):
    if dynamic > 0:
        dynamic = dynamic * ((rel_speed * 0.05) + 1)
    else:
        dynamic = dynamic * 0.5

    brake_distance = ((
            -2.09284547856357 * 10 ** -8 * rel_speed ** 4 + 1.10548262781578 + 10 ** -5 * rel_speed ** 3 + 1.10058179124046 * 10 ** -3 * rel_speed ** 2 + 0.107662075560879 * rel_speed + 0.69747816828)) + rel_speed * 0.15 + acc * 2 - br * 4 + dynamic
    return brake_distance


def check_warning_needed(cars, own_x, own_y, own_heading, own_speed, accelerator, brake, gear, setting, warn_multi, warn_length):
    collision_warning = 0
    angle_of_car = (own_heading + 16384) / 182.05
    if angle_of_car < 0:
        angle_of_car *= -1
    ang1 = angle_of_car + 1
    ang2 = angle_of_car + 340
    ang3 = angle_of_car + 20
    ang4 = angle_of_car + 359
    (x1, y1) = calc_polygon_points(own_x, own_y, 85 * 65536, ang1)  # front left
    (x2, y2) = calc_polygon_points(own_x, own_y, 2.0 * 65536, ang2)  # rear left
    (x3, y3) = calc_polygon_points(own_x, own_y, 2.0 * 65536, ang3)  # rear right
    (x4, y4) = calc_polygon_points(own_x, own_y, 85 * 65536, ang4)  # front right

    own_rectangle = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    rectangles_others = helpers.create_rectangles_for_collision_warning(cars)
    car_in_front = []
    for i, rectangle in enumerate(rectangles_others):
        if helpers.polygon_intersect(rectangle[1], own_rectangle):
            car_in_front.append(rectangle[0])

    for car in car_in_front:

        ok = False
        edge = False
        if car[0].heading + 5000 > 65536:
            heading_car_two_big = car[0].heading - 65536 + 5000
            edge = True
        else:
            heading_car_two_big = car[0].heading + 5000

        if car[0].heading - 5000 < 0:
            heading_car_two_small = car[0].heading + 65536 - 5000
            edge = True
        else:
            heading_car_two_small = car[0].heading - 5000

        if edge:
            if own_heading > heading_car_two_small or own_heading < heading_car_two_big:
                ok = True
        else:
            if heading_car_two_small < own_heading < heading_car_two_big:
                ok = True
        if setting == "medium":
            multiply = [1.2, 1.4, 2]
        elif setting == "late":
            multiply = [1.2, 1.3, 1.4]
        else:
            multiply = [1.2, 1.7, 2.3]

        for i in range(3):
            multiply[i] = multiply[i]*warn_multi

        if ok and gear > 0 and own_speed > 1 and own_speed - car[0].speed < 130:

            if car[0].distance < calc_brake_distance(own_speed - car[0].speed, accelerator, brake,
                                                     car[0].dynamic) * multiply[0] + warn_length:
                collision_warning = 3
            elif car[0].distance < calc_brake_distance(own_speed - car[0].speed, accelerator, brake,
                                                       car[0].dynamic) * multiply[1] + warn_length and collision_warning != 3:
                collision_warning = 2
            elif car[0].distance < calc_brake_distance(own_speed - car[0].speed, accelerator, brake,
                                                       car[0].dynamic) * multiply[2] + warn_length and collision_warning < 2:
                collision_warning = 1
            elif car[0].distance < (5 + warn_length) + own_speed * 0.05 and collision_warning < 2:
                collision_warning = 1
    return collision_warning
