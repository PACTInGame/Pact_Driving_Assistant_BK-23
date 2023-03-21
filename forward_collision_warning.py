from shapely.geometry import Polygon

import helpers
from park_assist import calc_polygon_points
from park_assist import get_size


def calc_brake_distance(rel_speed, acc, br, dynamic, cname):
    l, w = get_size(cname)
    if dynamic > 0:
        dynamic = dynamic * ((rel_speed * 0.05) + 1)
    else:
        dynamic = dynamic * 0.5
    rel_speed2 = rel_speed * rel_speed
    rel_speed3 = rel_speed2 * rel_speed
    rel_speed4 = rel_speed3 * rel_speed
    if rel_speed > 0:
        new_brake_distance = 0.0000003303 * rel_speed4 - 0.00002877 * rel_speed3 + 0.003215 * rel_speed2 + 0.07473 * rel_speed - 0.6175 + rel_speed * 0.05 + acc * 2 - br * 4 + dynamic + l / 2 + 2
    else:
        new_brake_distance = 0
    # brake_distance = ((
    #        -2.09284547856357 * 10 ** -8 * rel_speed ** 4 + 1.10548262781578 + 10 ** -5 * rel_speed ** 3 +
    #        1.10058179124046 * 10 ** -3 * rel_speed ** 2 + 0.107662075560879 * rel_speed + 0.69747816828)) +
    #        rel_speed * 0.15 + acc * 2 - br * 4 + dynamic + l / 2 - 2

    return new_brake_distance

 # Already optimized
def check_warning_needed(cars, own_x, own_y, own_heading, own_speed, accelerator, brake, gear, setting, warn_multi,
                         warn_length, own_speed_mci, accactive):
    speed = own_speed_mci if own_speed_mci - own_speed > 2 else own_speed
    angle_of_car = abs((own_heading + 16384) / 182.05)
    ang1, ang2, ang3, ang4 = angle_of_car + 1, angle_of_car + 340, angle_of_car + 20, angle_of_car + 359

    (x1, y1) = calc_polygon_points(own_x, own_y, 85 * 65536, ang1)
    (x2, y2) = calc_polygon_points(own_x, own_y, 2.0 * 65536, ang2)
    (x3, y3) = calc_polygon_points(own_x, own_y, 2.0 * 65536, ang3)
    (x4, y4) = calc_polygon_points(own_x, own_y, 85 * 65536, ang4)

    own_rectangle = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    rectangles_others = helpers.create_rectangles_for_collision_warning(cars)

    car_in_front = [rectangle[0] for rectangle in rectangles_others
                    if helpers.polygon_intersect(rectangle[1], own_rectangle)]

    collision_warning = 0

    setting_multiplier = {
        "medium": [1.2, 1.4, 2],
        "late": [1.2, 1.3, 1.4],
        "default": [1.2, 1.7, 2.3]
    }

    multiply = [x * warn_multi for x in setting_multiplier.get(setting, setting_multiplier["default"])]

    for car in car_in_front:
        ok = check_heading_within_bounds(car[0].heading, own_heading)
        speed_diff = speed - car[0].speed

        if ok and gear > 0 and speed > 1 and speed_diff < 130:
            brake_distance = calc_brake_distance(speed_diff, accelerator, brake, car[0].dynamic, car[0].cname)
            car_distance = car[0].distance

            if car_distance < brake_distance * multiply[0] + warn_length:
                collision_warning = max(collision_warning, 3)
            elif car_distance < brake_distance * multiply[1] + warn_length:
                collision_warning = max(collision_warning, 2)
            elif car_distance < brake_distance * multiply[2] + warn_length or car_distance < (5 + warn_length) + speed * 0.05:
                collision_warning = max(collision_warning, 1)

    if 1 < speed < 12 and not accactive:
        collision_warning = 3

    return collision_warning


def check_heading_within_bounds(heading, own_heading):
    heading_car_two_big = (heading + 5000) % 65536
    heading_car_two_small = (heading - 5000) % 65536

    if heading_car_two_small < heading_car_two_big:
        return heading_car_two_small < own_heading < heading_car_two_big
    else:
        return own_heading > heading_car_two_small or own_heading < heading_car_two_big