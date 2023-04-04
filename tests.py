import math

import helpers
import pyinsim
from park_assist import calc_polygon_points
from shapely.geometry import Polygon
import hud_window

def get_size_of_object(index):
    if index == 96:
        length = 3.7
        width = 0.4
    else:
        length = 1
        width = 1
    return length, width


def create_rectangles_for_objects(objects):
    rectangles = []

    for obj in objects:
        angle_of_car = (obj.Heading - 16384) / 182.05
        length, width = get_size_of_object(obj.Index)
        if angle_of_car < 0:
            angle_of_car *= -1
        a1 = math.atan((width / 2) / (length / 2)) * 180 / math.pi
        ang1 = angle_of_car + a1
        ang2 = angle_of_car + (180 - a1)
        ang3 = angle_of_car + (180 + a1)
        ang4 = angle_of_car + (360 - a1)
        diagonal = (length / 2) ** 2 + (width / 2) ** 2
        diagonal = math.sqrt(diagonal)
        (x1, y1) = calc_polygon_points(obj.X, obj.Y, (diagonal + 0.1) * 65536, ang1)  # front right
        (x2, y2) = calc_polygon_points(obj.X, obj.Y, (diagonal + 0.1) * 65536, ang2)  # rear right
        (x3, y3) = calc_polygon_points(obj.X, obj.Y, (diagonal + 0.1) * 65536, ang3)  # rear left
        (x4, y4) = calc_polygon_points(obj.X, obj.Y, (diagonal + 0.1) * 65536, ang4)  # front left
        angle = helpers.calculate_angle(-80*65536, -19*65536, obj.X, obj.Y, 17000)
        rectangles.append((angle, Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])))

    return rectangles


def message_out(insim, axm):
    for layoutO in axm.Info:
        print(layoutO.Flags, "Flags")
        print(layoutO.Index, "Index")



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
# Index 112, 113 Banners
# Index 144 Bale
# Index 148 Railing
# Index 149 Start Lights
# Index 174 Concrete Wall
# Index 175 Pillar
# Index 176 Slab Wall
# Index 177 Ramp Wall
# Index 178 Short Slab Wall


def insim_state(insim, sta):
    print(b"Currently driving on Track: " + sta.Track)
    insim.send(pyinsim.ISP_BTN,
               ReqI=255,
               ClickID=1,
               BStyle=40,
               T=5,
               L=5,
               W=90,
               H=119,
               Text=b"text.encode()")
    insim.send(pyinsim.ISP_TINY, ReqI=255, SubT=pyinsim.TINY_AXM)


# Init new InSim object.
insim = pyinsim.insim(b'127.0.0.1', 29999, Admin=b'')

# Bind ISP_MSO packet to message out method.
insim.bind(pyinsim.ISP_AXM, message_out)
# Bind ISP_STA packet to insim state method.
insim.bind(pyinsim.ISP_STA, insim_state)

# Start pyinsim.
pyinsim.run()
