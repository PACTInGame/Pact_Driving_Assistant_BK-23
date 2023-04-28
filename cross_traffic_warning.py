import math
import numpy as np

from helpers import calculate_angle


def cross_traffic_warning(car_position, car_heading, car_speed, own_position, own_heading, own_speed, own_speed_limit):
    car_x, car_y, car_z = car_position
    own_x, own_y, own_z = own_position

    # Calculate the angle between the two cars
    angle = calculate_angle(own_x, car_x, own_y, car_y, own_heading)

    # Check if the other car is coming from the side (either from right or left)
    if 30 <= angle <= 130 or 230 <= angle <= 330:
        heading_diff = (car_heading - own_heading) % 65536

        # Check if the car has the correct relative heading
        if (0 <= heading_diff <= 32768 and 0 <= angle <= 180) or (32768 < heading_diff <= 65536 and 180 < angle <= 360):
            own_speed_mps = own_speed / 3.6
            car_speed_mps = car_speed / 3.6

            # Convert headings to radians
            own_heading_rad = math.radians(own_heading / 182)
            car_heading_rad = math.radians(car_heading / 182)

            # Calculate unit direction vectors for each car
            own_dir = np.array([math.sin(own_heading_rad), math.cos(own_heading_rad)])
            car_dir = np.array([math.sin(car_heading_rad), math.cos(car_heading_rad)])

            # Calculate the intersection point using vector algebra
            w0 = np.array([own_x, own_y]) - np.array([car_x, car_y])
            a = np.dot(own_dir, own_dir)
            b = np.dot(own_dir, car_dir)
            c = np.dot(car_dir, car_dir)
            d = np.dot(own_dir, w0)
            e = np.dot(car_dir, w0)

            denom = a * c - b * b
            if denom != 0:
                s = (b * e - c * d) / denom
                t = (a * e - b * d) / denom
            else:
                return float('inf'), angle

            intersection_own = np.array([own_x, own_y]) + s * own_dir
            intersection_car = np.array([car_x, car_y]) + t * car_dir

            # Calculate the distances from each car to the intersection point
            distance_own = np.linalg.norm(intersection_own - np.array([own_x, own_y])) / 65536
            distance_car = np.linalg.norm(intersection_car - np.array([car_x, car_y])) / 65536

            # Calculate time it takes for both cars to reach the intersection point
            time_to_intersection_own = distance_own / own_speed_mps if own_speed_mps != 0 else float('inf')
            time_to_intersection_car = distance_car / car_speed_mps if car_speed_mps != 0 else float('inf')

            # Check if both cars will reach the intersection point within the 5-meter offset
            if not (math.isinf(time_to_intersection_own) or math.isinf(time_to_intersection_car)):
                time_difference = abs(time_to_intersection_own - time_to_intersection_car)
                distance_difference = time_difference * own_speed_mps
                if distance_difference <= 6:  # 5 meters offset
                    time_to_collision = (distance_own + distance_car) / (own_speed_mps + car_speed_mps)
                    return time_to_collision, angle
                else:
                    return float('inf'), angle
            else:
                return float('inf'), angle
        else:
            return float('inf'), angle
    else:
        return float('inf'), angle