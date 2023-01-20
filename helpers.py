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


def create_rectangles_for_blindspot_warning(cars):
    rectangles = []

    for car in cars:

        angle_of_car = (car[0].heading - 16384) / 182.05
        if angle_of_car < 0:
            angle_of_car *= -1
        ang1 = angle_of_car + 22
        ang2 = angle_of_car + 158
        ang3 = angle_of_car + 202
        ang4 = angle_of_car + 338
        (x1, y1) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang1)  # front right
        (x2, y2) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang2)  # rear right
        (x3, y3) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang3)  # rear left
        (x4, y4) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang4)  # front left

        rectangles.append(
            (car[0].speed, car[0].distance, Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)]), car[0].heading))
    return rectangles


def create_rectangles_for_collision_warning(cars):
    rectangles = []

    for car in cars:

        angle_of_car = (car[0].heading - 16384) / 182.05
        if angle_of_car < 0:
            angle_of_car *= -1
        ang1 = angle_of_car + 22
        ang2 = angle_of_car + 158
        ang3 = angle_of_car + 202
        ang4 = angle_of_car + 338
        (x1, y1) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang1)  # front right
        (x2, y2) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang2)  # rear right
        (x3, y3) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang3)  # rear left
        (x4, y4) = calc_polygon_points(car[0].x, car[0].y, 2.3 * 65536, ang4)  # front left

        rectangles.append((car, Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])))
    return rectangles


def get_shift_buttons():
    try:
        return kb.is_pressed("shift")
    except:
        return "Error detecting Keyboard inputs"


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


def get_cars_in_front(own_heading, own_x, own_y, cars):
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
    rectangles_others = create_rectangles_for_collision_warning(cars)
    car_in_front = []
    cars_in_front = []
    for i, rectangle in enumerate(rectangles_others):
        if polygon_intersect(rectangle[1], own_rectangle):
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
        if ok:
            cars_in_front.append(car)
    return cars_in_front


def get_vehicle_length(own_car):
    length = 0
    brake = 1.0
    if own_car == b'XFG':
        brake = 1.1
    elif own_car == b'LX4':
        brake = 0.9
    elif own_car == b'LX6':
        brake = 0.9
    elif own_car == b'FXO':
        brake = 0.9
    elif own_car == b'UFR':
        brake = 0.85
    elif own_car == b'XFR':
        brake = 0.85
    elif own_car == b'FXR':
        brake = 0.8
    elif own_car == b'XRR':
        brake = 0.8
    elif own_car == b'FZR':
        brake = 0.8
    elif own_car == b'BF1':
        brake = 0.7
    elif own_car == b'\x98a\x10':  # CAROBUS
        length -= 5
        brake = 1.9
    elif own_car == b'z\xf8p':  # LKW
        length += 3
        brake = 1.3
    elif own_car == b'\xb67G':  # ONIBUS
        length += 3
        brake = 1.4
    elif own_car == b'\xa4\xc2\xf3':  # Line Runner
        length += 3
        brake = 1.3
    elif own_car == b'\xcf\xee\x83':  # BUS 2
        length += 3
        brake = 1.2
    elif own_car == b'\xbc\xe5B':  # Reisebus
        length += 4
        brake = 1.4
    elif own_car == b'x\x0b!':  # Lory GP5
        brake = 1.1
    elif own_car == b'>\x8c\x88':  # Bumer 7
        brake = 1.1
    elif own_car == b'=v{':  # CCF012
        brake = 1.1
    elif own_car == b'\xac\xb1\xb0':  # FAIK TOPO
        brake = 0.95
    elif own_car == b'K\xd2c':  # UF Pickup Truck
        brake = 1
        length += 1
    elif own_car == b'*\x8f-':  # N.400s
        brake = 0.9
        length += 1
    return length, brake


def get_vehicle_redline(c):
    if c == b"UF1":
        r = 6000
    elif c == b"XFG":
        r = 7000
    elif c == b"XRG":
        r = 6000
    elif c == b"LX4":
        r = 8000
    elif c == b"LX6":
        r = 8000
    elif c == b"RB4":
        r = 6500
    elif c == b"FXO":
        r = 6500
    elif c == b"XRT":
        r = 6500
    elif c == b"RAC":
        r = 6000
    elif c == b"FZ5":
        r = 7000
    elif c == b'K\xd2c':  # UF Pick Up
        r = 6000
    elif c == b'\xb4\xdf\xa6':  # Swirl
        r = 6000
    elif c == b'\xedmj':  # TAZ09
        r = 5100
    elif c == b'\x05\xad\xcf':  # Wessex
        r = 9000
    elif c == b'\x81X\x95':  # SLX130
        r = 3200
    elif c == b'\x98a\x10':  # CAROBUS
        r = 1900
    elif c == b'z\xf8p':  # LKW
        r = 3000
    elif c == b'\xb67G':  # ONIBUS
        r = 1900
    elif c == b'\xa4\xc2\xf3':  # Line Runner
        r = 3000
    elif c == b'\x0c\xb9\xfc':  # Bayern 540
        r = 5000
    elif c == b'o\xa1%':  # EDM 540
        r = 6000
    elif c == b'\xf6\x121':  # lemon adieu
        r = 3800
    elif c == b']7\xd8':  # Panther
        r = 6000
    elif c == b'\x13\x80^':  # Pinewood
        r = 6000
    elif c == b'\xbc\xe5B':  # Reisebus
        r = 3000
    elif c == b'*\x8f-':  # N.440S
        r = 6000
    elif c == b'>\x8c\x88':  # Bumer 7
        r = 5000
    else:
        r = 7000
    return r


def get_max_gears(vehicle_model):
    mg = -1
    mr = -1
    if vehicle_model == b"FZ5":
        mg = 6
        mr = 7800
    elif vehicle_model == b'\x98a\x10':  # CAROBUS
        mg = 5
        mr = 2100
    elif vehicle_model == b'\xb6i\xbd':  # Luxury Sedan
        mg = 7
        mr = 6300
    elif vehicle_model == b'K\xd2c':  # UF Pickup Truck
        mg = 6
        mr = 6700
    elif vehicle_model == b'\xac\xb1\xb0':  # Faik Topo
        mg = 6
        mr = 5150
    elif vehicle_model == b'*\x8f-':  # N.440S
        mg = 6
        mr = 6700
    elif vehicle_model == b'>\x8c\x88':  # Bumer 7
        mg = 5
        mr = 5600
    return mg, mr


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
    if speed > 1:
        mom = ((last_fuel - now_fuel) * 5 * own_capa) / (speed / 3.6) * 1000 * 100
    else:
        mom = 99
    if dist > 1:
        avg = ((start_capa - now_fuel) * own_capa) / ((dist / 1000) / 100)

    else:
        avg = 99
    if avg == 0:
        avg = 5
    if dist > 300:
        own_range = (now_fuel * own_capa / avg) * 100
    else:
        own_range = -1

    if avg > 99:
        avg = 99
    if mom > 99:
        mom = 99
    return avg, mom, own_range


def get_fuel_capa(car):
    print(car)
    if car == b'UF1':
        capa = 35
    elif car == b'XFG':
        capa = 45
    elif car == b'XRG':
        capa = 65
    elif car == b'LX4':
        capa = 40
    elif car == b'LX6':
        capa = 40
    elif car == b'RB4' or car == b'FXO' or car == b'XRT':
        capa = 75
    elif car == b'RAC':
        capa = 42
    elif car == b'FZ5':
        capa = 90
    elif car == b'UFR':
        capa = 60
    elif car == b'XFR':
        capa = 70
    elif car == b'FXR' or car == b'XRR' or car == b'FZR':
        capa = 100
    elif car == b'\x98a\x10':  # CAROBUS
        capa = 240
    elif car == b'\xb6i\xbd':  # Luxury Sedan
        capa = 66
    elif car == b'K\xd2c':  # UF Pickup Truck
        capa = 137
    elif car == b'\xac\xb1\xb0':  # Faik Topo
        capa = 50
    elif car == b'*\x8f-':  # N.440S
        capa = 71
    elif car == b'>\x8c\x88':  # Bumer 7
        capa = 95
    elif car == b'\xbe\xa1e':  # XFG E
        capa = 48
    else:
        capa = -1

    return capa
