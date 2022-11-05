from shapely.geometry import Point, Polygon

#todo when other track was selected, no autosteer avail
def load_r(lane):
    with open("data\\lanes\\" + lane + ".txt") as fp:
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
        polygon1 = Polygon(new_arr)

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
        polygon2 = Polygon(new_arr2)

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
        polygon3 = Polygon(new_arr3)

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
        polygon4 = Polygon(new_arr4)

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
        polygon5 = Polygon(new_arr5)

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
        polygon6 = Polygon(new_arr6)

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
        polygon7 = Polygon(new_arr7)
        return [polygon1, polygon2, polygon3, polygon4, polygon5, polygon6, polygon7]


def load_l(lane):
    with open("data\\lanes\\" + lane + ".txt") as fp:
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
        polygon1l = Polygon(new_arr)

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
        polygon2l = Polygon(new_arr2)

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
        polygon3l = Polygon(new_arr3)

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
        polygon4l = Polygon(new_arr4)

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
        polygon5l = Polygon(new_arr5)

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
        polygon6l = Polygon(new_arr6)

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
        polygon7l = Polygon(new_arr7)
        return [polygon1l, polygon2l, polygon3l, polygon4l, polygon5l, polygon6l, polygon7l]


polygons_r = []
polygons_l = []


def load(track):
    if track == "WE":
        roads = ["western_hw_s", "western_hw_n", "paddock_n", "paddock_s", "north_entry_s", "north_entry_n",
                 "scavier_road_s", "scavier_road_n", "blackwood_main_n", "blackwood_main_s"]
        roadsl = ["western_hw_sl", "western_hw_nl", "paddock_nl", "paddock_sl", "north_entry_sl", "north_entry_nl",
                  "scavier_road_sl", "scavier_road_nl", "blackwood_main_nl", "blackwood_main_sl"]
    elif track == "BL":
        roads = ["blackwood_main_n", "blackwood_main_s", "bl_loop_n", "bl_loop_s"]
        roadsl = ["blackwood_main_nl", "blackwood_main_sl", "bl_loop_nl", "bl_loop_sl"]
    else:
        print("Error while loading tracks or track not yet supported")
    for lane in roads:
        polygons = load_r(lane)
        polygons_r.append(polygons)

    for lane in roadsl:
        polygons = load_l(lane)
        polygons_l.append(polygons)

    return polygons_r, polygons_l
