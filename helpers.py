import math
import subprocess
from pygame import mixer
from pyinsim import strmanip
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import winsound
import keyboard as kb
from park_assist import calc_polygon_points

mixer.init()


def closest_cars(cars, own_player_id, own_x, own_y):
    distances = []

    for i, j in enumerate(cars):
        a = own_x, own_y
        b = (j.x, j.y)
        distances.append([i, math.sqrt(
            (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])) / 65536])
    return distances


def current_brake_distance(own_speed):
    return (
                   -2.09284547856357 * 10 ** -8 * own_speed ** 4 + 1.10548262781578 + 10 ** -5 * own_speed ** 3 + 1.10058179124046 * 10 ** -3 * own_speed ** 2 + 0.107662075560879 * own_speed + 0.69747816828) * 1.2


def polygon_contains_point(polygon_list, x, y):
    point = Point(x, y)
    polygon = Polygon(polygon_list)
    return polygon.contains(point)


def collisionwarningsound(sound):
    mixer.music.load('data\\warning_' + str(sound) + '.wav')
    mixer.music.play()


def emawarningsound():
    winsound.PlaySound('data\\emawarning.wav', winsound.SND_FILENAME)


def emawarningsound2():
    winsound.PlaySound('data\\emawarning_intense.wav', winsound.SND_FILENAME)


def yield_sound():
    winsound.PlaySound('data\\yield_warn.wav', winsound.SND_FILENAME)


def polygon_intersect(p1, p2):
    return p1.intersects(p2)


def from_unicode(ustr, default='L'):
    """Convert a unicode string to a LFS encoded string."""
    return strmanip.fromUnicode(ustr, default)


def calculate_angle(x1, x2, y1, y2, own_heading):
    ang = (math.atan2((x2 / 65536 - x1 / 65536),
                      (y2 / 65536 - y1 / 65536)) * 180.0) / 3.1415926535897931
    if ang < 0.0:
        ang = 360.0 + ang
    consider_dir = ang + own_heading / 182
    if consider_dir > 360.0:
        consider_dir -= 360.0
    angle = consider_dir
    return angle


# Index 20-30 Cones
# Index 49-51 Small Tyres, 53-55 Big Tyres
# Index 64-91, 160, 161, 168, 169 Markers
# Index 96 Armco1,
# Index 97 Armco2,
# Index 98 Armco3
# Index 104 Barrier Long
# Index 105, 106 Barrier Short
# Index 112, 113 Banners
# Index 136-139 Posts
# Index 144 Bale
# Index 148 Railing
# Index 149 Start Lights
# Index 174 Concrete Wall
# Index 175 Pillar
# Index 176 Slab Wall
# Index 177 Ramp Wall
# Index 178 Short Slab Wall

def get_size_of_object(index):
    size_dict = {
        96: (3.7, 0.4),
        97: (10.2, 0.4),
        98: (16.6, 0.4),
        104: (8.5, 0.6),
        105: (1.5, 0.5),
        106: (1.5, 0.5),
        112: (1, 6),
        113: (1, 6),
        144: (0.9, 1.7),
        148: (0.6, 2.5),
        149: (0.7, 0.5),
    }
    if 20 <= index <= 30 or 49 <= index <= 51 or 53 <= index <= 55 or 136 <= index <= 139:
        return 0.8, 0.8
    elif index in size_dict:
        return size_dict[index]
    else:
        return 0, 0


def create_rectangles_for_objects(objects, own_x, own_y, own_heading):
    rectangles = []

    for obj in objects:
        angle_of_car = (obj.Heading * 1.412 + 90) % 360
        length, width = get_size_of_object(obj.Index)
        if length == 0:
            continue

        a1 = math.degrees(math.atan(width / length))
        angle_offsets = [a1, 180 - a1, 180 + a1, 360 - a1]
        diagonal = math.hypot(length / 2, width / 2) * 65536
        objx, objy = obj.X * 4096, obj.Y * 4096

        corners = [calc_polygon_points(objx, objy, diagonal + 0.1, angle_of_car + offset) for offset in angle_offsets]
        rectangles.append(([objx, objy], Polygon(corners)))

    return rectangles


def create_rectangles_for_blindspot_warning(cars):
    rectangles = []
    factor = 2.3 * 65536
    heading_offset = 16384
    heading_divisor = 182.05
    angle_offsets = [22, 158, 202, 338]

    for car in cars:
        x, y, heading = car[0].x, car[0].y, car[0].heading
        angle_of_car = abs((heading - heading_offset) / heading_divisor)
        polygon_points = [calc_polygon_points(x, y, factor, angle_of_car + offset) for offset in angle_offsets]
        rectangles.append((car[0].speed, car[0].distance, Polygon(polygon_points), heading))

    return rectangles


def create_rectangles_for_collision_warning(cars):
    rectangles = []
    conversion_factor = 65536
    offset_angle = 16384
    angle_divisor = 182.05
    distance = 2.3 * conversion_factor

    angles = [22, 158, 202, 338]

    for car in cars:
        car_heading = car[0].heading
        angle_of_car = abs((car_heading - offset_angle) / angle_divisor)

        car_x, car_y = car[0].x, car[0].y
        polygon_points = [
            calc_polygon_points(car_x, car_y, distance, angle_of_car + angle)
            for angle in angles
        ]

        rectangles.append((car, Polygon(polygon_points)))

    return rectangles


def get_shift_buttons():
    try:
        return kb.is_pressed("shift")
    except:
        return "Error detecting Keyboard inputs"


# TODO This section still needs improvement, use dictionary
def load_yield_polygons(track):
    list_of_polygons = []
    if track == b"AS":
        polygon = Polygon([(-641, -732), (-630, -725), (-628, -739), (-615, -755), (-622, -766)])
        polygon1 = Polygon([(-619, -770), (-620, -744), (-581, -757)])
        list_of_polygons.append([polygon, polygon1])

        polygon = Polygon([(-600, -785), (-607, -780), (-640, -819), (-633, -828)])
        polygon1 = Polygon([(-608, -780), (-623, -760), (-604, -763)])
        list_of_polygons.append([polygon, polygon1])

        polygon = Polygon([(-334, 663), (-365, 667), (-363, 689), (-325, 675)])
        polygon1 = Polygon([(-369, 659), (-377, 661), (-391, 582), (-384, 581)])
        polygon2 = Polygon([(-359, 777), (-366, 779), (-381, 691), (-373, 689)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        polygon = Polygon([(-117, 463), (-105, 487), (-74, 402), (-84, 398), (-107, 449)])
        polygon1 = Polygon([(-191, 378), (-127, 446), (-134, 457), (-201, 382)])
        polygon2 = Polygon([(-122, 594), (-134, 486), (-120, 484), (-113, 542), (-111, 594)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        polygon = Polygon([(-155, -391), (-144, -341), (-149, -336), (-159, -275), (-167, -276)])
        polygon1 = Polygon([(-144, -378), (-133, -380), (-135, -471), (-150, -473), (-147, -405)])
        polygon2 = Polygon(
            [(-140, -322), (-129, -325), (-120, -304), (-110, -284), (-95, -263), (-102, -258), (-118, -281)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        polygon = Polygon([(-160, -34), (-105, -35), (-107, -19), (-160, -17)])
        polygon1 = Polygon([(-160, -139), (-160, -50), (-170, -50), (-173, -141)])
        polygon2 = Polygon([(-169, -17), (-176, -17), (-190, 6), (-186, 18), (-173, 8), (-170, -1)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        polygon = Polygon([(115, -19), (126, -24), (109, -70), (89, -59)])
        polygon1 = Polygon([(194, -141), (132, -88), (124, -96), (185, -151)])
        list_of_polygons.append([polygon, polygon1])

        # Gas Station
        polygon = Polygon([(-450, -655), (-448, -641), (-438, -620), (-429, -639)])
        polygon1 = Polygon(
            [(-446, -643), (-455, -637), (-472, -669), (-489, -693), (-511, -712), (-493, -713), (-470, -688)])
        list_of_polygons.append([polygon, polygon1])

    elif track == b"BL":
        # Roundabout
        polygon = Polygon([(-399, 123), (-412, 131), (-399, 155), (-391, 150)])
        polygon1 = Polygon([(-434, 137), (-410, 131), (-428, 99), (-451, 116)])
        list_of_polygons.append([polygon, polygon1])

        # Main straight
        polygon = Polygon([(-682, 198), (-669, 193), (-681, 164), (-689, 168)])
        polygon1 = Polygon([(-670, 192), (-668, 199), (-599, 172), (-602, 166)])
        polygon2 = Polygon([(-676, 211), (-680, 204), (-735, 225), (-732, 233)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        polygon = Polygon([(-782, 206), (-789, 209), (-785, 238), (-772, 234)])
        polygon1 = Polygon([(-786, 244), (-816, 256), (-844, 264), (-840, 270), (-784, 254)])
        polygon2 = Polygon([(-701, 212), (-703, 206), (-760, 227), (-757, 234)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        polygon = Polygon([(-749, 278), (-756, 240), (-768, 244), (-756, 281)])
        polygon1 = Polygon([(-786, 244), (-816, 256), (-844, 264), (-840, 270), (-784, 254)])
        polygon2 = Polygon([(-701, 212), (-703, 206), (-760, 227), (-757, 234)])
        list_of_polygons.append([polygon, polygon1, polygon2])

    elif track == b"WE":  # yield, right, left
        # Gas Station
        polygon = Polygon([(-122, 628), (-122, 616), (-129, 614), (-130, 624)])
        polygon1 = Polygon([(-123, 616), (-118, 615), (-118, 556), (-123, 556)])
        polygon2 = Polygon([(-118, 698), (-113, 698), (-113, 631), (-118, 631)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        # Paddock stop
        polygon = Polygon([(-140, 229), (-122, 235), (-122, 221), (-140, 221)])
        polygon1 = Polygon([(-122, 221), (-118, 221), (-118, 130), (-125, 130)])
        polygon2 = Polygon([(-118, 296), (-113, 296), (-113, 235), (-118, 235)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        # Gas station near safe zone
        polygon = Polygon([(-122, 551), (-122, 546), (-133, 546), (-133, 551)])
        polygon1 = Polygon([(-122, 546), (-118, 543), (-118, 476), (-123, 476)])
        polygon2 = Polygon([(-118, 607), (-113, 607), (-113, 555), (-118, 555)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        # Western Highway from paddock
        polygon = Polygon([(157, 171), (159, 165), (140, 155), (127, 149), (123, 154)])
        polygon1 = Polygon([(170, 167), (236, 79), (235, 66), (162, 161)])
        polygon2 = Polygon([(169, 179), (164, 175), (135, 207), (104, 231), (110, 237), (141, 214)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        # Western Highway from Observatory
        polygon = Polygon([(439, -408), (426, -411), (417, -412), (409, -412), (410, -402), (428, -397)])
        polygon1 = Polygon([(446, -416), (484, -469), (505, -499), (525, -533), (515, -532), (443, -419)])
        polygon2 = Polygon([(431, -394), (382, -320), (370, -300), (359, -280), (367, -279), (435, -392)])
        list_of_polygons.append([polygon, polygon1, polygon2])

        # Spawn exit
        polygon = Polygon([(-182, -1055), (-189, -1055), (-191, -1045), (-179, -1045)])
        polygon1 = Polygon([(-189, -1055), (-189, -1059), (-245, -1059), (-145, -1055)])
        polygon2 = Polygon([(-180, -1059), (-181, -1066), (-107, -1065), (-107, -1059)])
        list_of_polygons.append([polygon, polygon1, polygon2])

    return list_of_polygons


def start_exe():
    subprocess.run(["start", "Pact_Driving_Assist.exe"], shell=True)


HEADING_MAX = 65536
HEADING_THRESHOLD = 5000
ANGLE_CORRECTION = 16384
ANGLE_RATIO = 182.05
FRONT_DISTANCE = 85 * 65536
REAR_DISTANCE = 2.0 * 65536


def get_cars_in_front(own_heading, own_x, own_y, cars):
    angle_of_car = (own_heading + ANGLE_CORRECTION) / ANGLE_RATIO

    front_left = angle_of_car + 1
    rear_left = angle_of_car + 340
    rear_right = angle_of_car + 20
    front_right = angle_of_car + 359

    (x1, y1) = calc_polygon_points(own_x, own_y, FRONT_DISTANCE, front_left)
    (x2, y2) = calc_polygon_points(own_x, own_y, REAR_DISTANCE, rear_left)
    (x3, y3) = calc_polygon_points(own_x, own_y, REAR_DISTANCE, rear_right)
    (x4, y4) = calc_polygon_points(own_x, own_y, FRONT_DISTANCE, front_right)

    own_rectangle = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    rectangles_others = create_rectangles_for_collision_warning(cars)
    cars_in_front = []

    for car, rectangle in rectangles_others:
        if polygon_intersect(rectangle, own_rectangle):
            heading_car_big = (car[0].heading + HEADING_THRESHOLD) % HEADING_MAX
            heading_car_small = (car[0].heading - HEADING_THRESHOLD) % HEADING_MAX

            if heading_car_small <= own_heading <= heading_car_big or heading_car_big < heading_car_small <= own_heading or own_heading <= heading_car_big < heading_car_small:
                cars_in_front.append(car)

    return cars_in_front


def get_vehicle_length(own_car):
    vehicle_data = {
        b'XFG': (0, 1.1),
        b'LX4': (0, 0.9),
        b'LX6': (0, 0.9),
        b'FXO': (0, 0.9),
        b'UFR': (0, 0.85),
        b'XFR': (0, 0.85),
        b'FXR': (0, 0.8),
        b'XRR': (0, 0.8),
        b'FZR': (0, 0.8),
        b'BF1': (0, 0.7),
        b'\x98a\x10': (-5, 1.9),  # CAROBUS
        b'z\xf8p': (3, 1.3),  # LKW
        b'\xb67G': (3, 1.4),  # ONIBUS
        b'\xa4\xc2\xf3': (3, 1.3),  # Line Runner
        b'\xcf\xee\x83': (3, 1.2),  # BUS 2
        b'\xbc\xe5B': (4, 1.4),  # Reisebus
        b'x\x0b!': (0, 1.1),  # Lory GP5
        b'>\x8c\x88': (0, 1.1),  # Bumer 7
        b'=v{': (0, 1.1),  # CCF012
        b'\xac\xb1\xb0': (0, 0.95),  # FAIK TOPO
        b'K\xd2c': (1, 1),  # UF Pickup Truck
        b'*\x8f-': (1, 0.9),  # N.400s
        b'Gb\xa7': (2, 1.4)  # Town Bus
    }

    length_adjustment, brake = vehicle_data.get(own_car, (0, 1.0))
    length = 0 + length_adjustment

    return length, brake


def get_vehicle_redline(c):
    redline_dict = {
        b"UF1": 6000,
        b"XFG": 7000,
        b"XRG": 6000,
        b"LX4": 8000,
        b"LX6": 8000,
        b"RB4": 6500,
        b"FXO": 6500,
        b"XRT": 6500,
        b"RAC": 6000,
        b"FZ5": 7000,
        b'K\xd2c': 6000,  # UF Pick Up
        b'\xb4\xdf\xa6': 6000,  # Swirl
        b'\xedmj': 5100,  # TAZ09
        b'\x05\xad\xcf': 9000,  # Wessex
        b'\x81X\x95': 3200,  # SLX130
        b'\x98a\x10': 1900,  # CAROBUS
        b'z\xf8p': 3000,  # LKW
        b'\xb67G': 1900,  # ONIBUS
        b'\xa4\xc2\xf3': 3000,  # Line Runner
        b'\x0c\xb9\xfc': 5000,  # Bayern 540
        b'o\xa1%': 6000,  # EDM 540
        b'\xf6\x121': 3800,  # lemon adieu
        b']7\xd8': 6000,  # Panther
        b'\x13\x80^': 6000,  # Pinewood
        b'\xbc\xe5B': 3000,  # Reisebus
        b'*\x8f-': 6000,  # N.440S
        b'>\x8c\x88': 5000,  # Bumer 7
        b'\xbe\xa1e': 13000,
        b'?!?': 2000,  # TSV8
        b'\xcf\xee\x83': 3000,  # TSV8
        b'Gb\xa7': 2000  # Town Bus
    }

    return redline_dict.get(c, 7000)


def get_max_gears(vehicle_model):
    vehicle_data = {
        b"FZ5": (6, 7800),
        b'\x98a\x10': (5, 2100),  # Carobus
        b'\xb6i\xbd': (7, 6300),  # Luxury Sedan
        b'K\xd2c': (6, 6700),  # UF Pickup Truck
        b'\xac\xb1\xb0': (6, 5150),  # Faik Topo
        b'*\x8f-': (6, 6700),
        b'>\x8c\x88': (5, 5600),
        b'Gb\xa7': (7, 2100)
    }

    return vehicle_data.get(vehicle_model, (-1, -1))


def playsound(sound):
    mixer.music.load('data\\warning_' + str(sound) + '.wav')
    mixer.music.play()


def playsound_indicator_on():
    mixer.music.load('data\\indicatorOn.wav')
    mixer.music.play()


def playsound_indicator_off():
    mixer.music.load('data\\indicatorOff.wav')
    mixer.music.play()


def calculate_fuel(last_fuel, now_fuel, start_capa, own_capa, speed, dist):
    if dist == 0:
        dist = 0.1
    if own_capa == -1:
        return 99, 99, 0

    speed_kph = speed / 3.6
    dist_km = dist / 1000

    mom = 99 if speed_kph <= 1 else ((last_fuel - now_fuel) * 5 * own_capa) / speed_kph * 100_000
    avg = 99 if dist_km <= 1 else ((start_capa - now_fuel) * own_capa) / dist_km * 100

    avg = max(avg, 5)
    own_range = -1 if dist_km <= 1 else (now_fuel * own_capa / avg) * 100

    avg = min(avg, 99)
    mom = min(mom, 99)

    return avg, mom, own_range


def get_fuel_capa(car):
    fuel_capacity_map = {
        b'UF1': 35,
        b'XFG': 45,
        b'XRG': 65,
        b'LX4': 40,
        b'LX6': 40,
        b'RB4': 75,
        b'FXO': 75,
        b'XRT': 75,
        b'RAC': 42,
        b'FZ5': 90,
        b'_\x1d*': 90,
        b'\xeb\xce9': 90,
        b'4\x96\xde': 90,  # FZ5 Lightbar, Safetycar, FZ5 Turbo
        b'UFR': 60,
        b'XFR': 70,
        b'FXR': 100,
        b'XRR': 100,
        b'FZR': 100,
        b'\x98a\x10': 240,  # CAROBUS
        b'\xb6i\xbd': 66,
        b'\xa5\x90\xc6': 66,  # Luxury Sedan, SV
        b'K\xd2c': 137,  # UF Pickup Truck
        b'\xac\xb1\xb0': 50,  # Faik Topo
        b'*\x8f-': 71,  # N.440S
        b'>\x8c\x88': 95,  # Bumer 7
        b'\xbe\xa1e': 48,  # XFG E
        b'\n\xe8\x9e': 78.7,
        b'\xaah\x1a': 78.7,  # FEND BR
        b'\x85\xc4\xa4': 30,  # Chorus Attendanze
        b'\xfa\xae\xe2': 75,  # ETK - K series
        b'\xb7\x83K': 38,  # UF Electric (Note: Duplicate key '\xb7\x83K' removed)
        b'6=j': 50,  # Tiny Cupe
        b'\xce\xd9v': 65,
        b'\x13>\xcb': 65,  # GT V-34, God foot
        b'H1`': 75,
        b'J\x08\xc8': 75,  # Bimmy M46, BZG SUV
        b'\xfa5\xe7': 50,  # XFG YARIS
        b'Z\x1f\x80': 300,  # MUN Firetruck
        b'\xcd\x87U': 73,  # Adda Ar-Eight
        b'\xd6\x11n': 70,  # Frerri F90
        b'R\xea/': 53,  # XR E-GT
        b'?!?': 381.9,  # TSV8
        b'\xcf\xee\x83': 200,  # RTS 6-71
        b'z\xf8p': 100,  # LCT 300
        b'\x89)\xfa': 57,  # E-Challenger
        b'\xdc\xb8\xb7': 40,  # Formula XR-E
        b'BF1': 95,
        b'\xf1\xf13': 59,  # Bavaria A20
        b'Gb\xa7': 295.9  # Town Bus
    }

    return fuel_capacity_map.get(car, -1)
