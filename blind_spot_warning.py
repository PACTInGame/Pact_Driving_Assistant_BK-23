from shapely.geometry import Polygon

import helpers
import park_assist
from park_assist import calc_polygon_points


def check_blindspots(cars, own_x, own_y, own_heading, own_speed):
    blindspot_r = False
    blindspot_l = False
    angle_of_car = (own_heading + 16384) / 182.05
    if angle_of_car < 0:
        angle_of_car *= -1
    ang1 = angle_of_car + 270
    ang2 = angle_of_car + 182
    ang3 = angle_of_car + 183
    ang4 = angle_of_car + 270
    ang5 = angle_of_car + 90
    ang6 = angle_of_car + 178
    ang7 = angle_of_car + 177
    ang8 = angle_of_car + 90
    # blind spot right checker
    (x1, y1) = calc_polygon_points(own_x, own_y, 4 * 65536, ang1)  # front left
    (x2, y2) = calc_polygon_points(own_x, own_y, 85 * 65536, ang2)  # rear left
    (x3, y3) = calc_polygon_points(own_x, own_y, 85 * 65536, ang3)  # rear right
    (x4, y4) = calc_polygon_points(own_x, own_y, 1 * 65536, ang4)  # front right
    (x5, y5) = calc_polygon_points(own_x, own_y, 4 * 65536, ang5)  # front left
    (x6, y6) = calc_polygon_points(own_x, own_y, 85 * 65536, ang6)  # rear left
    (x7, y7) = calc_polygon_points(own_x, own_y, 85 * 65536, ang7)  # rear right
    (x8, y8) = calc_polygon_points(own_x, own_y, 1 * 65536, ang8)  # front right

    rectangle_right = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    rectangle_left = Polygon([(x5, y5), (x6, y6), (x7, y7), (x8, y8)])
    rectangles_others = helpers.create_rectangles_for_blindspot_warning(cars)

    for i, rectangle in enumerate(rectangles_others):
        ok = False
        edge = False
        if rectangle[3] + 5000 > 65536:
            heading_car_two_big = rectangle[3] - 65536 + 5000
            edge = True
        else:
            heading_car_two_big = rectangle[3] + 5000

        if rectangle[3] - 5000 < 0:
            heading_car_two_small = rectangle[3] + 65536 - 5000
            edge = True
        else:
            heading_car_two_small = rectangle[3] - 5000

        if edge:
            if own_heading > heading_car_two_small or own_heading < heading_car_two_big:
                ok = True
        else:
            if heading_car_two_small < own_heading < heading_car_two_big:
                ok = True
        speed_diff = rectangle[0] - own_speed
        if rectangle[1] < speed_diff * 1.2 and ok:

            if helpers.polygon_intersect(rectangle[2], rectangle_left):
                blindspot_l = True
            if helpers.polygon_intersect(rectangle[2], rectangle_right):
                blindspot_r = True

    return blindspot_r, blindspot_l
