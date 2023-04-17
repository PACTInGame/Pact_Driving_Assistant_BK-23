from pyinsim import dist

class NaviRoute:
    def __init__(self, route, intersections):
        self.route = route
        self.intersections = intersections
        self.current_index = 0

    def get_next_intersections(self, x, y, z, threshold=10):
        if self.current_index >= len(self.route) - 1:
            last_intersection_name = self.route[self.current_index]
            last_intersection_coords = self.intersections[last_intersection_name]["coords"]
            distance_to_last = dist((x, y, z), last_intersection_coords)

            if distance_to_last <= threshold:
                return None, None, None  # End of the route
            else:
                return last_intersection_name, None, distance_to_last

        current_intersection_name = self.route[self.current_index]
        current_intersection_coords = self.intersections[current_intersection_name]["coords"]
        distance_to_current = dist((x, y, z), current_intersection_coords)

        # Check if the car is close to any other intersection
        for i in range(self.current_index + 1, len(self.route)):
            other_intersection_name = self.route[i]
            other_intersection_coords = self.intersections[other_intersection_name]["coords"]
            distance_to_other = dist((x, y, z), other_intersection_coords)

            if distance_to_other <= threshold:
                self.current_index = i
                break

        if distance_to_current <= threshold:
            self.current_index += 1

        next_intersection_name = self.route[self.current_index]

        if self.current_index < len(self.route) - 1:
            next_next_intersection_name = self.route[self.current_index + 1]
        else:
            next_next_intersection_name = None

        # Calculate the distance to the next intersection
        next_intersection_coords = self.intersections[next_intersection_name]["coords"]
        distance_to_next = dist((x, y, z), next_intersection_coords)

        return next_intersection_name, next_next_intersection_name, distance_to_next
