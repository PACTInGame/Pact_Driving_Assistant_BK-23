import math


class Vehicle:
    def __init__(self, x, y, z, heading, direction, steer_forces, speed, player_id, distance, dynamic, cname):
        self.x = x
        self.y = y
        self.z = z
        self.heading = heading
        self.direction = direction
        self.steer_forces = steer_forces
        self.speed = speed
        self.player_id = player_id
        self.distance = distance
        self.dynamic = dynamic
        self.cname = cname

    def update_dynamic(self, dynamic):
        self.dynamic = dynamic

    def update_distance(self, own_x, own_y, own_z):
        a = (own_x, own_y, own_z)
        b = (self.x, self.y, self.z)
        self.distance = (math.sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]) + (b[2] - a[2]) * (b[2] - a[2])) / 65536)

    def update_data(self, x, y, z,  heading, direction, steer_forces, speed, player_id):
        self.x = x
        self.y = y
        self.z = z
        self.heading = heading
        self.direction = direction
        self.steer_forces = steer_forces
        self.speed = speed
        self.player_id = player_id

    def update_cname(self, cn):
        self.cname = cn
