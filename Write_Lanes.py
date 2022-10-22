import pyinsim
import math
import time
from shapely.geometry import Point, Polygon

previousx = 0
previousy = 0

insim = pyinsim.insim(b'127.0.0.1', 29999, Admin=b'', Prefix=b"$", Flags=pyinsim.ISF_MCI | pyinsim.ISF_LOCAL,
                      Interval=500)


def outgauge_packet(outgauge, packet):
    global PLID
    PLID = packet.PLID


outgauge = pyinsim.outgauge(b'127.0.0.1', 30000, outgauge_packet, 30.0)


def refactor_angle(angle):
    if angle > 360:
        return angle - 360
    else:
        return angle


def calc_polygon_points(own_x, own_y, length, angle):
    return own_x + length * math.cos(math.radians(angle)), own_y + length * math.sin(math.radians(angle))


point1 = [[], []]
point1l = [[], []]
point2 = [[], []]
point2l = [[], []]
point3 = [[], []]
point3l = [[], []]
point4 = [[], []]
point4l = [[], []]
point5 = [[], []]
point5l = [[], []]
point7 = [[], []]
point7l = [[], []]
onepoint3 = [[], []]
onepoint3l = [[], []]

insim.send(pyinsim.ISP_BTN,
           ReqI=255,
           ClickID=1,
           BStyle=pyinsim.ISB_DARK | pyinsim.ISB_CLICK | 3,
           T=181,
           L=5,
           W=20,
           H=7,
           Text=b'START')
game = False


def buttonclick(insim, btc):
    global game
    print("clicked")
    if btc.ClickID == 1:
        game = not game
        print("clicked")


own_x = 0
own_y = 0


def car_info(insim, MCI):
    global point1, point2, point3, point4, point5, point7, onepoint3, own_x, own_y
    global point1l, point2l, point3l, point4l, point5l, point7l, onepoint3l
    if game:
        head = MCI.Info[0].Heading - 16384
        if head < 0:
            head = head + 65536
        angle_of_car = head / 182.05
        own_x = MCI.Info[0].X
        own_y = MCI.Info[0].Y
        if angle_of_car < 0:
            angle_of_car *= -1
        ang1 = angle_of_car + 90
        ang2 = angle_of_car + 270

        ang1 = refactor_angle(ang1)
        ang2 = refactor_angle(ang2)

        x = calc_polygon_points(own_x, own_y, 0.1 * 65536, ang1)  # right
        y = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang2)  # left
        point1[0].append(x)
        point1[1].append(y)
        x = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang1)  # right
        y = calc_polygon_points(own_x, own_y, 0.1 * 65536, ang2)  # left
        point1l[0].append(x)
        point1l[1].append(y)

        x = calc_polygon_points(own_x, own_y, 0.2 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang2)
        point2[0].append(x)
        point2[1].append(y)
        x = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.2 * 65536, ang2)
        point2l[0].append(x)
        point2l[1].append(y)

        x = calc_polygon_points(own_x, own_y, 0.3 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang2)
        point3[0].append(x)
        point3[1].append(y)
        x = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.3 * 65536, ang2)
        point3l[0].append(x)
        point3l[1].append(y)

        x = calc_polygon_points(own_x, own_y, 0.4 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang2)
        point4[0].append(x)
        point4[1].append(y)
        x = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.4 * 65536, ang2)
        point4l[0].append(x)
        point4l[1].append(y)

        x = calc_polygon_points(own_x, own_y, 0.5 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang2)
        point5[0].append(x)
        point5[1].append(y)
        x = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.5 * 65536, ang2)
        point5l[0].append(x)
        point5l[1].append(y)

        x = calc_polygon_points(own_x, own_y, 0.7 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang2)
        point7[0].append(x)
        point7[1].append(y)
        x = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.7 * 65536, ang2)
        point7l[0].append(x)
        point7l[1].append(y)

        x = calc_polygon_points(own_x, own_y, 1.3 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang2)
        onepoint3[0].append(x)
        onepoint3[1].append(y)
        x = calc_polygon_points(own_x, own_y, 0.0 * 65536, ang1)
        y = calc_polygon_points(own_x, own_y, 1.3 * 65536, ang2)
        onepoint3l[0].append(x)
        onepoint3l[1].append(y)

    else:
        own_x = MCI.Info[0].X
        own_y = MCI.Info[0].Y

        if len(point1[0]) > 0:
            with open('point_one.txt', 'w') as file:
                x = reversed(point1[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point1[1] = rev_arr
                string = str(point1)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point1 = [[], []]

            with open('point_two.txt', 'w') as file:
                x = reversed(point2[1])

                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point2[1] = rev_arr
                string = str(point2)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point2 = [[], []]

            with open('point_three.txt', 'w') as file:
                x = reversed(point3[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point3[1] = rev_arr
                string = str(point3)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point3 = [[], []]

            with open('point_four.txt', 'w') as file:
                x = reversed(point4[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point4[1] = rev_arr
                string = str(point4)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point4 = [[], []]

            with open('point_five.txt', 'w') as file:
                x = reversed(point5[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point5[1] = rev_arr
                string = str(point5)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point5 = [[], []]
            with open('point_seven.txt', 'w') as file:
                x = reversed(point7[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point7[1] = rev_arr
                string = str(point7)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point7 = [[], []]
            with open('onepoint3.txt', 'w') as file:
                x = reversed(onepoint3[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                onepoint3[1] = rev_arr
                string = str(onepoint3)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                onepoint3 = [[], []]

            # left-side -------------------------------------------------
            # -----------------------------------------------------------
            with open('point_onel.txt', 'w') as file:
                x = reversed(point1l[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point1l[1] = rev_arr
                string = str(point1l)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point1l = [[], []]

            with open('point_twol.txt', 'w') as file:
                x = reversed(point2l[1])

                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point2l[1] = rev_arr
                string = str(point2l)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point2l = [[], []]

            with open('point_threel.txt', 'w') as file:
                x = reversed(point3l[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point3l[1] = rev_arr
                string = str(point3l)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point3l = [[], []]

            with open('point_fourl.txt', 'w') as file:
                x = reversed(point4l[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point4l[1] = rev_arr
                string = str(point4l)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point4l = [[], []]

            with open('point_fivel.txt', 'w') as file:
                x = reversed(point5l[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point5l[1] = rev_arr
                string = str(point5l)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point5l = [[], []]

            with open('point_sevenl.txt', 'w') as file:
                x = reversed(point7l[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                point7l[1] = rev_arr
                string = str(point7l)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                point7l = [[], []]

            with open('onepoint3l.txt', 'w') as file:
                x = reversed(onepoint3l[1])
                rev_arr = []
                for item in x:
                    rev_arr.append(item)
                onepoint3l[1] = rev_arr
                string = str(onepoint3l)
                string = string.replace("[", "")
                string = string.replace("]", "")
                file.write(string)
                onepoint3l = [[], []]
            print("Settings saved successfully")
        try:
            if I_in_rectangle():
                print("1")
            elif I_in_rectanglel():
                print("1 left")
            elif I_in_rectangle2():
                print("2")
            elif I_in_rectangle2l():
                print("2 left")
            elif I_in_rectangle3():
                print("3")
            elif I_in_rectangle3l():
                print("3 left")
            elif I_in_rectangle4():
                print("4")
            elif I_in_rectangle4l():
                print("4 left")
            elif I_in_rectangle5():
                print("5")
            elif I_in_rectangle5l():
                print("5 left")
            elif I_in_rectangle6():
                print("6")
            elif I_in_rectangle6l():
                print("6 left")
            elif I_in_rectangle7():
                print("7")
            elif I_in_rectangle7l():
                print("7 left")
        except:
            pass
    print(MCI.Info[0].Heading)


def load():
    global rectangle, polygon_we_wh1, polygon_we_wh2, polygon_we_wh3, polygon_we_wh4, polygon_we_wh5, polygon_we_wh6, polygon_we_wh7
    try:
        with open("western_hw_n.txt") as fp:
            filedata = fp.read()
            filearr = filedata.split("!")

            string = filearr[0]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr = []
            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")

                new_arr.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh1 = Polygon(new_arr)

            string = filearr[1]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr2 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")

                new_arr2.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh2 = Polygon(new_arr2)

            string = filearr[2]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr3 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr3.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh3 = Polygon(new_arr3)

            string = filearr[3]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr4 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr4.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh4 = Polygon(new_arr4)

            string = filearr[4]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr5 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr5.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh5 = Polygon(new_arr5)

            string = filearr[5]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr6 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr6.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh6 = Polygon(new_arr6)

            string = filearr[6]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr7 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr7.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh7 = Polygon(new_arr7)
    except:
        pass


def load_l():
    global polygon_we_wh1l, polygon_we_wh2l, polygon_we_wh3l, polygon_we_wh4l, polygon_we_wh5l, polygon_we_wh6l, polygon_we_wh7l
    try:
        with open("western_hw_nl.txt") as fp:
            filedata = fp.read()
            filearr = filedata.split("!")

            string = filearr[0]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr = []
            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")

                new_arr.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh1l = Polygon(new_arr)

            string = filearr[1]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr2 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")

                new_arr2.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh2l = Polygon(new_arr2)

            string = filearr[2]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr3 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr3.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh3l = Polygon(new_arr3)

            string = filearr[3]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr4 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr4.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh4l = Polygon(new_arr4)

            string = filearr[4]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr5 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr5.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh5l = Polygon(new_arr5)

            string = filearr[5]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr6 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr6.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh6l = Polygon(new_arr6)

            string = filearr[6]
            string = string.replace("(", "")
            string = string.replace(" ", "")
            arr = string.split("),")
            new_arr7 = []

            for item in arr:
                splitted = item.split(",")
                splitted[0] = splitted[0].replace(")", "")
                splitted[1] = splitted[1].replace(")", "")
                new_arr7.append((float(splitted[0]), float(splitted[1])))
            polygon_we_wh7l = Polygon(new_arr7)
    except:
        pass


load()
load_l()


def I_in_rectangle():
    point = Point(own_x, own_y)

    return polygon_we_wh1.contains(point)


def I_in_rectangle2():
    point = Point(own_x, own_y)

    return polygon_we_wh2.contains(point)


def I_in_rectangle3():
    point = Point(own_x, own_y)

    return polygon_we_wh3.contains(point)


def I_in_rectangle4():
    point = Point(own_x, own_y)
    return polygon_we_wh4.contains(point)


def I_in_rectangle5():
    point = Point(own_x, own_y)
    return polygon_we_wh5.contains(point)


def I_in_rectangle6():
    point = Point(own_x, own_y)

    return polygon_we_wh6.contains(point)


def I_in_rectangle7():
    point = Point(own_x, own_y)

    return polygon_we_wh7.contains(point)


def I_in_rectanglel():
    point = Point(own_x, own_y)

    return polygon_we_wh1l.contains(point)


def I_in_rectangle2l():
    point = Point(own_x, own_y)

    return polygon_we_wh2l.contains(point)


def I_in_rectangle3l():
    point = Point(own_x, own_y)

    return polygon_we_wh3l.contains(point)


def I_in_rectangle4l():
    point = Point(own_x, own_y)
    return polygon_we_wh4l.contains(point)


def I_in_rectangle5l():
    point = Point(own_x, own_y)
    return polygon_we_wh5l.contains(point)


def I_in_rectangle6l():
    point = Point(own_x, own_y)

    return polygon_we_wh6l.contains(point)


def I_in_rectangle7l():
    point = Point(own_x, own_y)

    return polygon_we_wh7l.contains(point)


insim.bind(pyinsim.ISP_MCI, car_info)
insim.bind(pyinsim.ISP_BTC, buttonclick)
pyinsim.run()
