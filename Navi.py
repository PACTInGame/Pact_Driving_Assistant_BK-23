import heapq
import math
import pyinsim
from pygame import mixer

from NaviRoute import NaviRoute

insim = pyinsim.insim(b'127.0.0.1', 29999, Admin=b'', Flags=pyinsim.ISF_MCI | pyinsim.ISF_LOCAL, Interval=500)

PLID = 0

xCoord = 0
yCoord = 0
zCoord = 0
soundtoplay = 0
soundplayed = 0
heading = 0
speed = 0


def outgauge(outgauge, packet):
    global PLID
    PLID = packet.PLID


outgauge = pyinsim.outgauge(b'127.0.0.1', 30000, outgauge, 30.0)


def dist(a=(0, 0, 0), b=(0, 0, 0)):
    return math.sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]) + (b[2] - a[2]) * (b[2] - a[2]))


mixer.init()


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


def playsound():
    global soundplayed, navstarted
    if soundtoplay == "destination.wav":
        navstarted = False
    try:
        if soundtoplay != soundplayed:
            soundplayed = soundtoplay
            mixer.music.load('Navi\\EN-US\\' + str(soundtoplay))
            mixer.music.play()
    except:
        pass


route_follower = None
navstarted = False


def get_direction_and_distance_to_next_intersection(x, y, z, heading, next_intersection_name, intersections):
    current_coords = (x, y, z)
    if next_intersection_name is not None:
        next_intersection_coords = intersections[next_intersection_name]["coords"]
        distance_to_next = dist(current_coords, next_intersection_coords)

        angle = calculate_angle(x, next_intersection_coords[0], y, next_intersection_coords[1], heading)

        # Convert the angle to a direction number between 0 and 7
        direction_number = round(angle / 45) % 8

        return direction_number, distance_to_next
    else:
        return 8, 0


def get_car_data(insim, mci):
    global speed, cars, xCoord, yCoord, zCoord, heading, soundtoplay, navstarted

    for car in mci.Info:
        if car.PLID == PLID:
            heading = car.Heading
            xCoord = car.X / 65536
            yCoord = car.Y / 65536
            zCoord = car.Z / 65536
            speed = car.Speed / 91.02

    if not navstarted:
        startnav()
        navstarted = True
        print("started")
    next_intersection = route_follower.get_next_intersections(xCoord, yCoord, zCoord, threshold=6 + speed / 5)
    arrows = get_direction_and_distance_to_next_intersection(xCoord, yCoord, zCoord, heading, next_intersection[0], points_westhill)
    print(next_intersection[0])
    soundtoplay = get_audio_file(*next_intersection)
    print(soundtoplay)
    if soundtoplay is not None:
        playsound()
    arrow = arrow_strings.get(arrows[0])
    distance_to_intersection = round(arrows[1])
    buttonarrow = arrow  + b"^L %.0f m" % distance_to_intersection
    insim.send(pyinsim.ISP_BTN,
               ReqI=255,
               ClickID=2,
               BStyle=pyinsim.ISB_DARK | 3,
               T=106,
               L=100,
               W=15,
               H=6,
               Text=buttonarrow)
    try:
        text = b'^L^H\xa1\xf7' if soundtoplay.__contains__("right") else b""
        if text == b"":
            text = b'^L^H\xa1\xf6' if soundtoplay.__contains__("left") else b""
        if text == b"":
            text = b'^L^H\xa1\xf4' if soundtoplay.__contains__("straight") else b""

        insim.send(pyinsim.ISP_BTN,
                   ReqI=255,
                   ClickID=1,
                   BStyle=pyinsim.ISB_DARK | 3,
                   T=100,
                   L=100,
                   W=15,
                   H=6,
                   Text=text)


    except:
        pass


def get_audio_file(next_intersection, next_next_intersection, distance_to_next):
    if next_intersection is None and next_next_intersection is None and distance_to_next is None:
        return "destination.wav"

    def get_prefix(distance):
        if distance < 70:
            return "Now"
        elif distance < 110:
            return None
        elif distance < 220:
            return "200"
        else:
            return None

    def get_direction(first_heading, second_heading):
        directions = ["North", "East", "South", "West"]
        first_index = directions.index(first_heading)
        second_index = directions.index(second_heading)

        if (second_index - first_index) % 4 == 1:
            return "left"
        elif (second_index - first_index) % 4 == 3:
            return "right"
        elif (second_index - first_index) % 4 == 2:
            return "straight"
        else:
            return None

    if not next_intersection or not next_next_intersection:
        return None

    next_name_parts = next_intersection.split("_")
    next_next_name_parts = next_next_intersection.split("_")

    if next_name_parts[0] not in ["Intersection", "Roundabout"] or next_next_name_parts[0] not in ["Intersection",
                                                                                                   "Roundabout"]:
        return None

    if next_name_parts[1] != next_next_name_parts[1]:
        return None

    direction = get_direction(next_name_parts[2], next_next_name_parts[2])

    if not direction:
        return None

    prefix = get_prefix(distance_to_next)
    audio_file = f"{prefix}_{next_name_parts[0].lower()}_{direction}.wav"

    return audio_file


def dijkstra_shortest_path(intersections, start, end):
    # Create a dictionary of intersections with their coordinates and neighbors
    intersection_dict = {name: (data["coords"], data["neighbors"]) for name, data in intersections.items()}

    # Initialize the priority queue, visited set, and distance dictionary
    pq = [(0, start, [])]
    visited = set()
    distances = {intersection: float('inf') for intersection in intersection_dict}
    distances[start] = 0

    while pq:
        # Get the intersection with the smallest distance
        distance, current, path = heapq.heappop(pq)

        if current not in visited:
            visited.add(current)
            path = path + [current]

            if current == end:
                return path

            for neighbor in intersection_dict[current][1]:
                new_distance = int(distance + dist(intersection_dict[current][0], intersection_dict[neighbor][0]))

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor, path))

    return None


# Example usage:
intersections_Layout_Square = [["A1", 1000, -1000, 2, ["A2", "A4"]], ["A2", 0, -1000, 2, ["A1", "A5", "A3"]],
                               ["A3", -1000, -1000, 2, ["A2", "A6"]], ["A4", 1000, 0, 2, ["A1", "A7", "A5"]],
                               ["A5", 0, 0, 2, ["A4", "A6", "A2", "A8"]], ["A6", -1000, 0, 2, ["A3", "A5", "A9"]],
                               ["A7", 1000, 1000, 2, ["A4", "A8"]], ["A8", 0, 1000, 2, ["A7", "A9", "A5"]],
                               ["A9", -1000, 1000, 9, ["A6", "A8"]]]
arrow_strings = {
    0: b"^L^H\xa1\xf4",  # up
    1: b"^L^H\xa1\xf9",  # upright
    2: b"^L^H\xa1\xf7",  # right
    3: b"^L^H\xa1\xfb",  # downright
    4: b"^L^H\xa1\xf5",  # down
    5: b"^L^H\xa1\xfa",  # downleft
    6: b"^L^H\xa1\xf6",  # left
    7: b"^L^H\xa1\xf8",  # upleft
    8: b"^L^H\xa1\xf3"   # destination
}
points_westhill = {
    "Roundabout_North_East": {"coords": (-361, 753, 10),
                              "neighbors": ["Roundabout_North_North", "Roundabout_North_West", "Roundabout_North_South",
                                            "Corner_Pit_1"]},
    "Roundabout_North_North": {"coords": (-382, 771, 11),
                               "neighbors": ["Roundabout_North_East", "Roundabout_North_West", "Roundabout_North_South",
                                             "Intersection_NorthIndustry_South"]},
    "Roundabout_North_West": {"coords": (-405, 749, 13),
                              "neighbors": ["Roundabout_North_East", "Roundabout_North_North", "Roundabout_North_South",
                                            "Intersection_North_East"]},
    "Roundabout_North_South": {"coords": (-374, 730, 12),
                               "neighbors": ["Roundabout_North_East", "Roundabout_North_North", "Roundabout_North_West",
                                             "Intersection_ScavierNorth_North"]},

    "Corner_Pit_1": {"coords": (-178, 824, 3), "neighbors": ["Corner_Pit_2", "Roundabout_North_East"]},
    "Corner_Pit_2": {"coords": (-119, 786, 7), "neighbors": ["Corner_Pit_1", "Intersection_Pit_North"]},

    "Intersection_Pit_North": {"coords": (-118, 642, 3),
                               "neighbors": ["Intersection_Pit_West", "Intersection_Pit_South", "Corner_Pit_2"]},
    "Intersection_Pit_West": {"coords": (-136, 609, 3),
                              "neighbors": ["Intersection_Pit_South", "Intersection_Pit_North",
                                            "Intersection_PitLot_North"]},
    "Intersection_Pit_South": {"coords": (-118, 545, 3),
                               "neighbors": ["Intersection_Pit_West", "Intersection_Pit_North",
                                             "Intersection_MidPaddockRace_North"]},

    "Intersection_UpperPit_South": {"coords": (-118, 189, 5),
                                    "neighbors": ["Intersection_Bridge_North", "Intersection_UpperPit_North",
                                                  "Intersection_UpperPit_West"]},
    "Intersection_UpperPit_North": {"coords": (-118, 249, 5),
                                    "neighbors": ["Intersection_MidPaddockRace_South", "Intersection_UpperPit_South",
                                                  "Intersection_UpperPit_West"]},
    "Intersection_UpperPit_West": {"coords": (-135, 222, 5),
                                   "neighbors": ["Intersection_UpperPit_North", "Intersection_UpperPit_South"]},

    "Intersection_Bridge_South": {"coords": (-118, 71, 6),
                                  "neighbors": ["Intersection_Bridge_North", "Intersection_Bridge_East",
                                                "Corner_Medical"]},
    "Intersection_Bridge_North": {"coords": (-118, 135, 6),
                                  "neighbors": ["Intersection_UpperPit_South", "Intersection_Bridge_East",
                                                "Intersection_Bridge_South"]},
    "Intersection_Bridge_East": {"coords": (-101, 104, 6),
                                 "neighbors": ["Intersection_Bridge_North", "Intersection_Bridge_South",
                                               "Intersection_PaddockBridge_West"]},

    "Corner_Medical": {"coords": (-118, -99, 17),
                       "neighbors": ["Intersection_Medical_East", "Intersection_Bridge_South"]},

    "Intersection_Medical_South": {"coords": (-150, -149, 16),
                                   "neighbors": ["Intersection_Medical_North", "Intersection_Medical_East",
                                                 "Intersection_EndOfPaddock_North", "Intersection_Medical_West"]},
    "Intersection_Medical_North": {"coords": (-151, -99, 16),
                                   "neighbors": ["Intersection_Medical_South", "Intersection_Medical_East",
                                                 "Intersection_UpperPit_West", "Intersection_Medical_West"]},
    "Intersection_Medical_East": {"coords": (-134, -125, 16),
                                  "neighbors": ["Intersection_Medical_North", "Intersection_Medical_South",
                                                "Corner_Medical", "Intersection_Medical_West"]},
    "Intersection_Medical_West": {"coords": (-186, -90, 16),
                                  "neighbors": ["Intersection_Medical_South", "Intersection_Medical_North",
                                                "Intersection_Medical_East", "Intersection_RaceEndOfStraight_East"]},

    "Intersection_WesternMiddle_South": {"coords": (176, 158, 11), "neighbors": ["Intersection_WesternMiddle_North",
                                                                                 "Intersection_WesternMiddle_West",
                                                                                 "Corner_Western_Middle"]},
    "Intersection_WesternMiddle_North": {"coords": (158, 182, 11), "neighbors": ["Intersection_WesternMiddle_South",
                                                                                 "Intersection_WesternMiddle_West",
                                                                                 "Intersection_DustinHofmann_West"]},
    "Intersection_WesternMiddle_West": {"coords": (153, 162, 11), "neighbors": ["Intersection_PaddockBridge_East",
                                                                                "Intersection_WesternMiddle_South",
                                                                                "Intersection_WesternMiddle_North"]},

    "Corner_Western_Middle": {"coords": (269, 5, 7),
                              "neighbors": ["Intersection_WesternMiddle_South", "Intersection_WesternPark_North"]},

    "Intersection_WesternPark_South": {"coords": (456, -429, 9),
                                       "neighbors": ["Intersection_WesternPark_North", "Intersection_WesternPark_West",
                                                     "Intersection_WesternEndLot_North"]},
    "Intersection_WesternPark_North": {"coords": (423, -383, 9),
                                       "neighbors": ["Intersection_WesternPark_South", "Intersection_WesternPark_West",
                                                     "Corner_Western_Middle"]},
    "Intersection_WesternPark_West": {"coords": (421, -412, 9),
                                      "neighbors": ["Intersection_WesternPark_North", "Intersection_WesternPark_South",
                                                    "Intersection_ParkBridge_East"]},

    "Intersection_ParkBridge_North": {"coords": (308, -383, 7),
                                      "neighbors": ["Intersection_ParkBridge_West", "Intersection_ParkBridge_East",
                                                    "Intersection_RaceEastPark_West"]},
    "Intersection_ParkBridge_West": {"coords": (302, -409, 8),
                                     "neighbors": ["Intersection_ParkBridge_North", "Intersection_ParkBridge_East",
                                                   "Intersection_ParkBridge2_East"]},
    "Intersection_ParkBridge_East": {"coords": (338, -410, 8),
                                     "neighbors": ["Intersection_ParkBridge_North", "Intersection_ParkBridge_West",
                                                   "Intersection_WesternPark_West"]},

    "Intersection_ParkBridge2_South": {"coords": (286, -425, 8),
                                       "neighbors": ["Intersection_ParkBridge2_West", "Intersection_ParkBridge2_East",
                                                     "Corner_ParkSmallSouth_North"]},
    "Intersection_ParkBridge2_West": {"coords": (233, -410, 12),
                                      "neighbors": ["Intersection_ParkBridge2_South", "Intersection_ParkBridge2_East",
                                                    "Intersection_ParkLoop_East"]},
    "Intersection_ParkBridge2_East": {"coords": (281, -409, 9),
                                      "neighbors": ["Intersection_ParkBridge2_South", "Intersection_ParkBridge2_West",
                                                    "Intersection_ParkBridge_West"]},

    "Intersection_ParkLoop_South": {"coords": (164, -440, 18),
                                    "neighbors": ["Intersection_ParkLoop_West", "Intersection_ParkLoop_East"]},
    "Intersection_ParkLoop_West": {"coords": (131, -422, 20),
                                   "neighbors": ["Intersection_ParkLoop_South", "Intersection_ParkLoop_East",
                                                 "Intersection_ParkMiddle_East"]},
    "Intersection_ParkLoop_East": {"coords": (180, -416, 17),
                                   "neighbors": ["Intersection_ParkLoop_South", "Intersection_ParkLoop_West",
                                                 "Intersection_ParkBridge2_West"]},

    "Intersection_ParkMiddle_South": {"coords": (18, -521, 22),
                                      "neighbors": ["Intersection_ParkMiddle_West", "Intersection_ParkMiddle_East",
                                                    "Intersection_RaceSouthPark2_North"]},
    "Intersection_ParkMiddle_West": {"coords": (-13, -486, 23),
                                     "neighbors": ["Intersection_ParkMiddle_South", "Intersection_ParkMiddle_East",
                                                   "Intersection_RaceNationalPark2_East"]},
    "Intersection_ParkMiddle_East": {"coords": (29, -479, 22),
                                     "neighbors": ["Intersection_ParkMiddle_South", "Intersection_ParkMiddle_West",
                                                   "Intersection_ParkLoop_West"]},

    "Intersection_WesternEndLot_South": {"coords": (652, -743, 10), "neighbors": ["Intersection_WesternEndLot_North",
                                                                                  "Intersection_WesternEndLot_East",
                                                                                  "Intersection_WesternEndLot2_North"]},
    "Intersection_WesternEndLot_North": {"coords": (627, -707, 10), "neighbors": ["Intersection_WesternEndLot_South",
                                                                                  "Intersection_WesternEndLot_East",
                                                                                  "Intersection_WesternPark_South"]},
    "Intersection_WesternEndLot_East": {"coords": (654, -715, 10), "neighbors": ["Intersection_WesternEndLot_South",
                                                                                 "Intersection_WesternEndLot_North",
                                                                                 "Corner_WesternEndLot2_North"]},

    "Intersection_WesternEndLot2_South": {"coords": (735, -889, 13), "neighbors": ["Intersection_WesternEndLot2_North",
                                                                                   "Intersection_WesternEndLot2_East",
                                                                                   "Intersection_WesternEndSmall_North"]},
    "Intersection_WesternEndLot2_North": {"coords": (724, -845, 11), "neighbors": ["Intersection_WesternEndLot2_South",
                                                                                   "Intersection_WesternEndLot2_East",
                                                                                   "Intersection_WesternEndLot_South"]},
    "Intersection_WesternEndLot2_East": {"coords": (751, -853, 12), "neighbors": ["Intersection_WesternEndLot2_South",
                                                                                  "Intersection_WesternEndLot2_North",
                                                                                  "Corner_WesternEndLot2_South"]},

    "Corner_WesternEndLot2_South": {"coords": (781, -789, 13),
                                    "neighbors": ["Corner_WesternEndLot2_North", "Corner_WesternEndLot2_Lot1",
                                                  "Corner_WesternEndLot2_Lot2", "Corner_WesternEndLot2_Lot3",
                                                  "Corner_WesternEndLot2_Lot4", "Intersection_WesternEndLot2_East"]},
    "Corner_WesternEndLot2_North": {"coords": (690, -691, 12),
                                    "neighbors": ["Corner_WesternEndLot2_South", "Corner_WesternEndLot2_Lot1",
                                                  "Corner_WesternEndLot2_Lot2", "Corner_WesternEndLot2_Lot3",
                                                  "Corner_WesternEndLot2_Lot4", "Intersection_WesternEndLot_East"]},
    "Corner_WesternEndLot2_Lot1": {"coords": (749, -842, 12),
                                   "neighbors": ["Corner_WesternEndLot2_South", "Corner_WesternEndLot2_North"]},
    "Corner_WesternEndLot2_Lot2": {"coords": (728, -832, 12),
                                   "neighbors": ["Corner_WesternEndLot2_South", "Corner_WesternEndLot2_North"]},
    "Corner_WesternEndLot2_Lot3": {"coords": (662, -738, 10),
                                   "neighbors": ["Corner_WesternEndLot2_South", "Corner_WesternEndLot2_North"]},
    "Corner_WesternEndLot2_Lot4": {"coords": (664, -725, 11),
                                   "neighbors": ["Corner_WesternEndLot2_South", "Corner_WesternEndLot2_North"]},

    "Intersection_WesternEndSmall_South": {"coords": (623, -1156, 4),
                                           "neighbors": ["Intersection_WesternEndSmall_North",
                                                         "Intersection_WesternEndLot2_West",
                                                         "Corner_WesternEnd_South"]},
    "Intersection_WesternEndSmall_North": {"coords": (669, -1096, 11),
                                           "neighbors": ["Intersection_WesternEndSmall_South",
                                                         "Intersection_WesternEndLot2_West",
                                                         "Intersection_WesternEndLot2_South"]},
    "Intersection_WesternEndLot2_West": {"coords": (651, -1103, 9), "neighbors": ["Intersection_WesternEndSmall_South",
                                                                                  "Intersection_WesternEndSmall_North"]},

    "Corner_WesternEnd_South": {"coords": (492, -1193, 2), "neighbors": ["Intersection_WesternEndSmall_South",
                                                                         "Intersection_WesternCarPark_East"]},

    "Intersection_WesternCarPark_South": {"coords": (143, -1108, 13), "neighbors": ["Intersection_WesternCarPark_North",
                                                                                    "Intersection_WesternCarPark_West",
                                                                                    "Intersection_WesternCarPark_East"]},
    "Intersection_WesternCarPark_North": {"coords": (149, -1079, 14), "neighbors": ["Intersection_WesternCarPark_South",
                                                                                    "Intersection_WesternCarPark_West",
                                                                                    "Intersection_WesternCarPark_East",
                                                                                    "Intersection_ParkEntrySouth2_South"]},
    "Intersection_WesternCarPark_West": {"coords": (130, -1089, 14), "neighbors": ["Intersection_WesternCarPark_South",
                                                                                   "Intersection_WesternCarPark_North",
                                                                                   "Intersection_WesternCarPark_East",
                                                                                   "Corner_CarPark_Middle"]},
    "Intersection_WesternCarPark_East": {"coords": (163, -1095, 13), "neighbors": ["Intersection_WesternCarPark_South",
                                                                                   "Intersection_WesternCarPark_North",
                                                                                   "Intersection_WesternCarPark_West",
                                                                                   "Corner_WesternEnd_South"]},

    "Corner_CarPark_East": {"coords": (476, -1213, 4),
                            "neighbors": ["Intersection_WesternCarPark_South", "Corner_CarPark_West"]},
    "Corner_CarPark_North1": {"coords": (-9, -1107, 18),
                              "neighbors": ["Intersection_WesternCarPark_South", "Corner_CarPark_West"]},
    "Corner_CarPark_North2": {"coords": (-182, -1093, 26),
                              "neighbors": ["Intersection_WesternCarPark_South", "Corner_CarPark_West"]},
    "Corner_CarPark_West": {"coords": (-236, -1163, 26),
                            "neighbors": ["Intersection_WesternCarPark_South", "Intersection_WesternEnd_South"]},

    "Corner_CarPark_Middle": {"coords": (-3, -1067, 17),
                              "neighbors": ["Intersection_WesternCarPark_West", "Intersection_Spawn_East"]},

    "Intersection_Spawn_North": {"coords": (-185, -1047, 25),
                                 "neighbors": ["Intersection_Spawn_East", "Intersection_Spawn_West"]},
    "Intersection_Spawn_East": {"coords": (-172, -1060, 24),
                                "neighbors": ["Intersection_Spawn_North", "Intersection_Spawn_West",
                                              "Corner_CarPark_Middle"]},
    "Intersection_Spawn_West": {"coords": (-198, -1060, 25),
                                "neighbors": ["Intersection_Spawn_North", "Intersection_Spawn_East",
                                              "Intersection_WesternEnd_East"]},

    "Intersection_WesternEnd_North": {"coords": (-270, -1045, 26),
                                      "neighbors": ["Intersection_WesternEnd_East", "Intersection_WesternEnd_South",
                                                    "Intersection_WesternEnd2_South"]},
    "Intersection_WesternEnd_East": {"coords": (-241, -1059, 26),
                                     "neighbors": ["Intersection_WesternEnd_North", "Intersection_WesternEnd_South",
                                                   "Intersection_Spawn_West"]},
    "Intersection_WesternEnd_South": {"coords": (-256, -1074, 26),
                                      "neighbors": ["Intersection_WesternEnd_North", "Intersection_WesternEnd_East",
                                                    "Corner_CarPark_West"]},

    "Intersection_WesternEnd2_North": {"coords": (-299, -992, 26),
                                       "neighbors": ["Intersection_WesternEnd2_East", "Intersection_WesternEnd2_South",
                                                     "Corner_SouthEntry_South"]},
    "Intersection_WesternEnd2_East": {"coords": (-288, -1000, 26),
                                      "neighbors": ["Intersection_WesternEnd2_North", "Intersection_WesternEnd2_South",
                                                    "Intersection_WesternEnd3_West"]},
    "Intersection_WesternEnd2_South": {"coords": (-286, -1016, 26),
                                       "neighbors": ["Intersection_WesternEnd2_North", "Intersection_WesternEnd2_East",
                                                     "Intersection_WesternEnd_North"]},

    "Intersection_WesternEnd3_North": {"coords": (-280, -972, 25),
                                       "neighbors": ["Intersection_WesternEnd3_West", "Intersection_WesternEnd3_East",
                                                     "Corner_SmallSouthEntry_South"]},
    "Intersection_WesternEnd3_West": {"coords": (-276, -994, 25),
                                      "neighbors": ["Intersection_WesternEnd3_North", "Intersection_WesternEnd3_East",
                                                    "Intersection_WesternEnd2_East"]},
    "Intersection_WesternEnd3_East": {"coords": (-258, -983, 25),
                                      "neighbors": ["Intersection_WesternEnd3_North", "Intersection_WesternEnd3_West",
                                                    "Intersection_RaceWesternEnd_West"]},

    "Corner_SouthEntry_South": {"coords": (-683, -642, 40),
                                "neighbors": ["Intersection_WesternEnd2_North", "Corner_SouthEntry_North"]},
    "Corner_SouthEntry_North": {"coords": (-711, -612, 40),
                                "neighbors": ["Corner_SouthEntry_South", "Intersection_SoutEntryDirt_South"]},

    "Intersection_SoutEntryDirt_East": {"coords": (-811, -237, 30), "neighbors": ["Intersection_SoutEntryDirt_North",
                                                                                  "Intersection_SoutEntryDirt_South",
                                                                                  "Intersection_SoutEntryDirt2_West"]},
    "Intersection_SoutEntryDirt_North": {"coords": (-846, -295, 30), "neighbors": ["Intersection_SoutEntryDirt_East",
                                                                                   "Intersection_SoutEntryDirt_South",
                                                                                   "Corner_SouthEntryDirt_West"]},
    "Intersection_SoutEntryDirt_South": {"coords": (-812, -258, 30),
                                         "neighbors": ["Corner_SouthEntry_North", "Intersection_SoutEntryDirt_East",
                                                       "Intersection_SoutEntryDirt_North"]},

    "Intersection_SoutEntryDirt2_East": {"coords": (-786, -212, 29), "neighbors": ["Intersection_SoutEntryDirt2_North",
                                                                                   "Intersection_SoutEntryDirt2_South",
                                                                                   "Intersection_SoutEntryDirt2_West",
                                                                                   "Intersection_PoliceHQ_West"]},
    "Intersection_SoutEntryDirt2_North": {"coords": (-802, -209, 29), "neighbors": ["Intersection_SoutEntryDirt2_East",
                                                                                    "Intersection_SoutEntryDirt2_South",
                                                                                    "Intersection_SoutEntryDirt2_West",
                                                                                    "Corner_SouthEntryDirt_East"]},
    "Intersection_SoutEntryDirt2_South": {"coords": (-788, -234, 29), "neighbors": ["Intersection_SoutEntryDirt2_East",
                                                                                    "Intersection_SoutEntryDirt2_North",
                                                                                    "Intersection_SoutEntryDirt2_West",
                                                                                    "Intersection_BehindPoliceHQ2_North"]},
    "Intersection_SoutEntryDirt2_West": {"coords": (-802, -228, 30), "neighbors": ["Intersection_SoutEntryDirt2_East",
                                                                                   "Intersection_SoutEntryDirt2_North",
                                                                                   "Intersection_SoutEntryDirt2_South",
                                                                                   "Intersection_SoutEntryDirt_East"]},

    "Corner_SouthEntryDirt_West": {"coords": (-854, -79, 30),
                                   "neighbors": ["Intersection_SoutEntryDirt_North", "Corner_SouthEntryDirt_North"]},
    "Corner_SouthEntryDirt_East": {"coords": (-819, -79, 28),
                                   "neighbors": ["Corner_SouthEntryDirt_North", "Intersection_SoutEntryDirt2_North"]},
    "Corner_SouthEntryDirt_North": {"coords": (-834, -67, 28),
                                    "neighbors": ["Corner_SouthEntryDirt_West", "Corner_SouthEntryDirt_East"]},

    "Intersection_PoliceHQ_North": {"coords": (-747, -155, 25),
                                    "neighbors": ["Intersection_PoliceHQ_South", "Intersection_PoliceHQ_East",
                                                  "Intersection_PoliceHQ_West",
                                                  "Intersection_NorthEntryScavier_South"]},
    "Intersection_PoliceHQ_South": {"coords": (-733, -190, 26),
                                    "neighbors": ["Intersection_PoliceHQ_North", "Intersection_PoliceHQ_East",
                                                  "Intersection_PoliceHQ_West", "Intersection_BehindPoliceHQ_North"]},
    "Intersection_PoliceHQ_East": {"coords": (-722, -180, 26),
                                   "neighbors": ["Intersection_PoliceHQ_North", "Intersection_PoliceHQ_South",
                                                 "Intersection_PoliceHQ_West", "Corner_BusBridge_North"]},
    "Intersection_PoliceHQ_West": {"coords": (-753, -179, 26),
                                   "neighbors": ["Intersection_PoliceHQ_North", "Intersection_PoliceHQ_South",
                                                 "Intersection_PoliceHQ_East", "Intersection_SoutEntryDirt2_East"]},

    "Intersection_NorthEntryScavier_North": {"coords": (-774, -40, 26),
                                             "neighbors": ["Intersection_NorthEntryScavier_South",
                                                           "Intersection_NorthEntryScavier_East",
                                                           "Intersection_KartingInternational_South"]},
    "Intersection_NorthEntryScavier_South": {"coords": (-774, -77, 26),
                                             "neighbors": ["Intersection_NorthEntryScavier_North",
                                                           "Intersection_NorthEntryScavier_East",
                                                           "Intersection_PoliceHQ_North"]},
    "Intersection_NorthEntryScavier_East": {"coords": (-756, -59, 25),
                                            "neighbors": ["Intersection_NorthEntryScavier_North",
                                                          "Intersection_NorthEntryScavier_South",
                                                          "Intersection_Westlodge_West"]},

    "Intersection_Westlodge_West": {"coords": (-566, -78, 20),
                                    "neighbors": ["Intersection_Westlodge_South", "Intersection_Westlodge_East",
                                                  "Intersection_NorthEntryScavier_East"]},
    "Intersection_Westlodge_South": {"coords": (-546, -97, 20),
                                     "neighbors": ["Intersection_Westlodge_West", "Intersection_Westlodge_East"]},
    "Intersection_Westlodge_East": {"coords": (-535, -79, 19),
                                    "neighbors": ["Intersection_Westlodge_West", "Intersection_Westlodge_South",
                                                  "Intersection_KartingNational_West"]},

    "Intersection_North_North": {"coords": (-530, 788, 16),
                                 "neighbors": ["Intersection_North_South", "Intersection_North_East",
                                               "Intersection_NorthIndustry_West"]},
    "Intersection_North_South": {"coords": (-538, 769, 16),
                                 "neighbors": ["Intersection_North_North", "Intersection_North_East",
                                               "Corner_NorthEntry_North"]},
    "Intersection_North_East": {"coords": (-517, 772, 16),
                                "neighbors": ["Intersection_North_North", "Intersection_North_South",
                                              "Roundabout_North_West"]},

    "Intersection_NorthIndustry_North": {"coords": (-365, 915, 16), "neighbors": ["Intersection_NorthIndustry_South",
                                                                                  "Intersection_NorthIndustry_West",
                                                                                  "Intersection_NorthIndustry2_South"]},
    "Intersection_NorthIndustry_South": {"coords": (-367, 892, 15), "neighbors": ["Intersection_NorthIndustry_North",
                                                                                  "Intersection_NorthIndustry_West",
                                                                                  "Roundabout_North_North"]},
    "Intersection_NorthIndustry_West": {"coords": (-380, 907, 15), "neighbors": ["Intersection_NorthIndustry_North",
                                                                                 "Intersection_NorthIndustry_South",
                                                                                 "Intersection_North_North"]},

    "Intersection_NorthIndustry2_North": {"coords": (-347, 957, 17), "neighbors": ["Intersection_NorthIndustry2_South",
                                                                                   "Intersection_NorthIndustry2_East",
                                                                                   "Corner_Northest_West"]},
    "Intersection_NorthIndustry2_South": {"coords": (-362, 932, 16), "neighbors": ["Intersection_NorthIndustry2_North",
                                                                                   "Intersection_NorthIndustry2_East",
                                                                                   "Intersection_NorthIndustry_North"]},
    "Intersection_NorthIndustry2_East": {"coords": (-342, 935, 16), "neighbors": ["Intersection_NorthIndustry2_North",
                                                                                  "Intersection_NorthIndustry2_South"]},

    "Corner_Northest_West": {"coords": (-252, 991, 19),
                             "neighbors": ["Intersection_NorthIndustry2_North", "Corner_Northest_North"]},
    "Corner_Northest_North": {"coords": (-69, 1038, 23), "neighbors": ["Corner_Northest_West", "Corner_Northest_East"]},
    "Corner_Northest_East": {"coords": (-23, 1036, 22),
                             "neighbors": ["Corner_Northest_North", "Intersection_NorthEast_West"]},

    "Intersection_NorthEast_North": {"coords": (37, 1000, 21),
                                     "neighbors": ["Intersection_NorthEast_West", "Intersection_NorthEast_South",
                                                   "Corner_NorthestEastLot_North"]},
    "Intersection_NorthEast_West": {"coords": (12, 1004, 21),
                                    "neighbors": ["Intersection_NorthEast_North", "Intersection_NorthEast_South",
                                                  "Corner_Northest_East"]},
    "Intersection_NorthEast_South": {"coords": (18, 976, 21),
                                     "neighbors": ["Intersection_NorthEast_North", "Intersection_NorthEast_West",
                                                   "Intersection_NorthWestern_North"]},

    "Corner_NorthestEastLot_North": {"coords": (128, 1006, 22),
                                     "neighbors": ["Intersection_NorthEast_North", "Corner_NorthestEastLot_South"]},
    "Corner_NorthestEastLot_West": {"coords": (51, 987, 22),
                                    "neighbors": ["Corner_NorthestEastLot_North", "Corner_NorthestEastLot_South"]},
    "Corner_NorthestEastLot_West2": {"coords": (33, 966, 22),
                                     "neighbors": ["Corner_NorthestEastLot_North", "Corner_NorthestEastLot_South"]},
    "Corner_NorthestEastLot_West3": {"coords": (22, 881, 22),
                                     "neighbors": ["Corner_NorthestEastLot_North", "Corner_NorthestEastLot_South"]},
    "Corner_NorthestEastLot_South": {"coords": (50, 869, 22),
                                     "neighbors": ["Corner_NorthestEastLot_North", "Intersection_NorthWestern_East"]},

    "Intersection_NorthWestern_North": {"coords": (3, 864, 21), "neighbors": ["Intersection_NorthWestern_East",
                                                                              "Intersection_NorthWestern_South",
                                                                              "Intersection_NorthEast_South"]},
    "Intersection_NorthWestern_East": {"coords": (12, 850, 21),
                                       "neighbors": ["Corner_NorthestEastLot_South", "Intersection_NorthWestern_North",
                                                     "Intersection_NorthWestern_South"]},
    "Intersection_NorthWestern_South": {"coords": (-2, 832, 21), "neighbors": ["Intersection_NorthWestern_North",
                                                                               "Intersection_NorthWestern_East",
                                                                               "Intersection_NorthWestern2_North"]},

    "Intersection_NorthWestern2_North": {"coords": (-11, 768, 21), "neighbors": ["Intersection_NorthWestern2_West",
                                                                                 "Intersection_NorthWestern2_South",
                                                                                 "Intersection_NorthWestern_South"]},
    "Intersection_NorthWestern2_West": {"coords": (-22, 754, 20), "neighbors": ["Intersection_NorthWestern2_North",
                                                                                "Intersection_NorthWestern2_South",
                                                                                "Intersection_WesternSmall_East"]},
    "Intersection_NorthWestern2_South": {"coords": (-15, 732, 20), "neighbors": ["Intersection_NorthWestern2_North",
                                                                                 "Intersection_NorthWestern2_West",
                                                                                 "Corner_WesternNorth_North"]},

    "Corner_WesternNorth_North": {"coords": (-34, 498, 13),
                                  "neighbors": ["Intersection_NorthWestern2_South", "Corner_WesternNorth_South"]},
    "Corner_WesternNorth_South": {"coords": (-34, 498, 13),
                                  "neighbors": ["Corner_WesternNorth_North", "Intersection_DustinHofmann_North"]},

    "Intersection_DustinHofmann_North": {"coords": (95, 240, 7), "neighbors": ["Intersection_DustinHofmann_South",
                                                                               "Intersection_DustinHofmann_West",
                                                                               "Corner_WesternNorth_South"]},
    "Intersection_DustinHofmann_South": {"coords": (125, 217, 9), "neighbors": ["Intersection_DustinHofmann_North",
                                                                                "Intersection_DustinHofmann_West",
                                                                                "Intersection_WesternMiddle_North"]},
    "Intersection_DustinHofmann_West": {"coords": (98, 221, 8), "neighbors": ["Intersection_DustinHofmann_North",
                                                                              "Intersection_DustinHofmann_South",
                                                                              "Intersection_DustinHofmannLot_East"]},

    "Intersection_EndOfPaddock_North": {"coords": (-150, -300, 19), "neighbors": ["Intersection_EndOfPaddock_West",
                                                                                  "Intersection_EndOfPaddock_East",
                                                                                  "Intersection_Medical_South"]},
    "Intersection_EndOfPaddock_West": {"coords": (-177, -325, 21), "neighbors": ["Intersection_EndOfPaddock_North",
                                                                                 "Intersection_EndOfPaddock_East",
                                                                                 "Intersection_BusStation_East"]},
    "Intersection_EndOfPaddock_East": {"coords": (-147, -338, 19), "neighbors": ["Intersection_EndOfPaddock_North",
                                                                                 "Intersection_EndOfPaddock_West",
                                                                                 "Intersection_RacePaddock_North"]},

    "Intersection_BusStation_North": {"coords": (-301, -296, 21),
                                      "neighbors": ["Intersection_BusStation_West", "Intersection_BusStation_East"]},
    "Intersection_BusStation_West": {"coords": (-313, -304, 21),
                                     "neighbors": ["Intersection_BusStation_North", "Intersection_BusStation_East",
                                                   "Intersection_BusStation2_East"]},
    "Intersection_BusStation_East": {"coords": (-289, -307, 21),
                                     "neighbors": ["Intersection_BusStation_North", "Intersection_BusStation_West",
                                                   "Intersection_EndOfPaddock_West"]},

    "Intersection_BusStation2_West": {"coords": (-376, -309, 22),
                                      "neighbors": ["Intersection_BusStation2_South", "Intersection_BusStation2_East",
                                                    "Corner_BusBridge_East"]},
    "Intersection_BusStation2_South": {"coords": (-364, -315, 22),
                                       "neighbors": ["Intersection_BusStation2_West", "Intersection_BusStation2_East"]},
    "Intersection_BusStation2_East": {"coords": (-356, -308, 22),
                                      "neighbors": ["Intersection_BusStation2_West", "Intersection_BusStation2_South",
                                                    "Intersection_BusStation_West"]},

    "Corner_BusBridge_East": {"coords": (-34, 498, 13),
                              "neighbors": ["Intersection_BusStation2_West", "Corner_BusBridge_North"]},
    "Corner_BusBridge_North": {"coords": (-34, 498, 13),
                               "neighbors": ["Corner_BusBridge_East", "Intersection_PoliceHQ_East"]},

    "Intersection_KartingNational_West": {"coords": (-397, -67, 16), "neighbors": ["Intersection_KartingNational_East",
                                                                                   "Intersection_KartingNational_South",
                                                                                   "Intersection_Westlodge_East"]},
    "Intersection_KartingNational_East": {"coords": (-314, -41, 16), "neighbors": ["Intersection_KartingNational_West",
                                                                                   "Intersection_KartingNational_South",
                                                                                   "Intersection_KartingNational2_South"]},
    "Intersection_KartingNational_South": {"coords": (-330, -71, 15), "neighbors": ["Intersection_KartingNational_West",
                                                                                    "Intersection_KartingNational_East",
                                                                                    "Corner_NextToKartingNational_South"]},

    "Intersection_KartingNational2_North": {"coords": (-300, 37, 15),
                                            "neighbors": ["Intersection_KartingNational2_East",
                                                          "Intersection_KartingNational2_South",
                                                          "Intersection_ScavierLot_South"]},
    "Intersection_KartingNational2_East": {"coords": (-283, 18, 15),
                                           "neighbors": ["Intersection_KartingNational2_North",
                                                         "Intersection_KartingNational2_South",
                                                         "Intersection_NextToRace2_West"]},
    "Intersection_KartingNational2_South": {"coords": (-300, 5, 15),
                                            "neighbors": ["Intersection_KartingNational2_North",
                                                          "Intersection_KartingNational2_East",
                                                          "Intersection_KartingNational_East"]},

    "Intersection_ScavierLot_North": {"coords": (-300, 138, 15),
                                      "neighbors": ["Intersection_ScavierLot_West", "Intersection_ScavierLot_South",
                                                    "Corner_Scavier_South"]},
    "Intersection_ScavierLot_West": {"coords": (-315, 119, 15),
                                     "neighbors": ["Intersection_ScavierLot_North", "Intersection_ScavierLot_South",
                                                   "Corner_ScavierLotEntrance_North"]},
    "Intersection_ScavierLot_South": {"coords": (-300, 105, 15), "neighbors": ["Intersection_KartingNational2_North",
                                                                               "Intersection_ScavierLot_North",
                                                                               "Intersection_ScavierLot_West"]},

    "Corner_ScavierLotEntrance_North": {"coords": (-355, 244, 16), "neighbors": ["Intersection_ScavierLot_West"]},

    "Corner_Scavier_North": {"coords": (-355, 244, 16),
                             "neighbors": ["Corner_Scavier_Middle", "Intersection_ScavierNorth_South"]},
    "Corner_Scavier_Middle": {"coords": (-309, 398, 15), "neighbors": ["Corner_Scavier_South", "Corner_Scavier_North"]},
    "Corner_Scavier_South": {"coords": (-301, 252, 15),
                             "neighbors": ["Intersection_ScavierLot_North", "Corner_Scavier_Middle"]},

    "Intersection_ScavierNorth_North": {"coords": (-358, 707, 12), "neighbors": ["Intersection_ScavierNorth_East",
                                                                                 "Intersection_ScavierNorth_South",
                                                                                 "Roundabout_North_South"]},
    "Intersection_ScavierNorth_East": {"coords": (-341, 705, 13), "neighbors": ["Intersection_ScavierNorth_North",
                                                                                "Intersection_ScavierNorth_South",
                                                                                "Intersection_NextToRace_West"]},
    "Intersection_ScavierNorth_South": {"coords": (-346, 689, 13), "neighbors": ["Intersection_ScavierNorth_North",
                                                                                 "Intersection_ScavierNorth_East",
                                                                                 "Corner_Scavier_North"]},

    "Intersection_KartingInternational_North": {"coords": (-742, 147, 23),
                                                "neighbors": ["Intersection_KartingInternational_East",
                                                              "Intersection_KartingInternational_South",
                                                              "Corner_NorthEntry_South"]},
    "Intersection_KartingInternational_East": {"coords": (-732, 127, 23),
                                               "neighbors": ["Intersection_KartingInternational_North",
                                                             "Intersection_KartingInternational_South"]},
    "Intersection_KartingInternational_South": {"coords": (-749, 106, 24),
                                                "neighbors": ["Intersection_KartingInternational_North",
                                                              "Intersection_KartingInternational_East",
                                                              "Intersection_NorthEntryScavier_North"]},

    "Corner_NorthEntry_North": {"coords": (-600, 633, 19),
                                "neighbors": ["Corner_NorthEntry_South", "Intersection_North_South"]},
    "Corner_NorthEntry_South": {"coords": (-672, 516, 20),
                                "neighbors": ["Corner_NorthEntry_North", "Intersection_KartingInternational_North"]},

    "Intersection_BehindPoliceHQ_North": {"coords": (-640, -247, 26), "neighbors": ["Intersection_PoliceHQ_South",
                                                                                    "Intersection_BehindPoliceHQ_West",
                                                                                    "Intersection_BehindPoliceHQ_East"]},
    "Intersection_BehindPoliceHQ_West": {"coords": (-639, -294, 26), "neighbors": ["Intersection_BehindPoliceHQ_North",
                                                                                   "Intersection_BehindPoliceHQ_East",
                                                                                   "Intersection_BehindPoliceHQ2_East"]},
    "Intersection_BehindPoliceHQ_East": {"coords": (-611, -275, 25), "neighbors": ["Intersection_BehindPoliceHQ_North",
                                                                                   "Intersection_BehindPoliceHQ_West",
                                                                                   "Intersection_RaceKarting_East"]},

    "Intersection_BehindPoliceHQ2_North": {"coords": (-740, -339, 32),
                                           "neighbors": ["Intersection_BehindPoliceHQ2_South",
                                                         "Intersection_BehindPoliceHQ2_East",
                                                         "Intersection_SoutEntryDirt2_South"]},
    "Intersection_BehindPoliceHQ2_South": {"coords": (-705, -386, 32),
                                           "neighbors": ["Intersection_BehindPoliceHQ2_North",
                                                         "Intersection_BehindPoliceHQ2_East",
                                                         "Corner_SmallSouthEntry_North"]},
    "Intersection_BehindPoliceHQ2_East": {"coords": (-693, -337, 30),
                                          "neighbors": ["Intersection_BehindPoliceHQ2_North",
                                                        "Intersection_BehindPoliceHQ2_South",
                                                        "Intersection_BehindPoliceHQ_West"]},

    "Corner_SmallSouthEntry_North": {"coords": (-438, -621, 33), "neighbors": ["Corner_SmallSouthEntry_South",
                                                                               "Intersection_BehindPoliceHQ2_South"]},
    "Corner_SmallSouthEntry_South": {"coords": (-388, -679, 33),
                                     "neighbors": ["Corner_SmallSouthEntry_North", "Intersection_WesternEnd3_North"]},

    "Intersection_RaceWesternEnd_North": {"coords": (-287, -887, 25), "neighbors": ["Intersection_RaceWesternEnd_South",
                                                                                    "Intersection_RaceWesternEnd_West",
                                                                                    "Intersection_RaceNational_South"]},
    "Intersection_RaceWesternEnd_South": {"coords": (-266, -908, 24), "neighbors": ["Intersection_RaceWesternEnd_North",
                                                                                    "Intersection_RaceWesternEnd_West",
                                                                                    "Intersection_ParkEntrySouth_West"]},
    "Intersection_RaceWesternEnd_West": {"coords": (-285, -912, 25), "neighbors": ["Intersection_RaceWesternEnd_North",
                                                                                   "Intersection_RaceWesternEnd_South",
                                                                                   "Intersection_WesternEnd3_East"]},

    "Intersection_ParkEntrySouth_North": {"coords": (74, -756, 11), "neighbors": ["Intersection_ParkEntrySouth_West",
                                                                                  "Intersection_ParkEntrySouth_East",
                                                                                  "Intersection_RaceSouthPark_South"]},
    "Intersection_ParkEntrySouth_West": {"coords": (58, -774, 11), "neighbors": ["Intersection_ParkEntrySouth_North",
                                                                                 "Intersection_ParkEntrySouth_East",
                                                                                 "Intersection_RaceWesternEnd_South"]},
    "Intersection_ParkEntrySouth_East": {"coords": (89, -765, 10), "neighbors": ["Intersection_ParkEntrySouth_North",
                                                                                 "Intersection_ParkEntrySouth_West",
                                                                                 "Intersection_ParkEntrySouth2_West"]},

    "Intersection_ParkEntrySouth2_North": {"coords": (266, -930, 12), "neighbors": ["Intersection_ParkEntrySouth2_West",
                                                                                    "Intersection_ParkEntrySouth2_East",
                                                                                    "Intersection_ParkEntrySouth2_South",
                                                                                    "Intersection_RaceSouthPark2_South"]},
    "Intersection_ParkEntrySouth2_West": {"coords": (257, -938, 11), "neighbors": ["Intersection_ParkEntrySouth2_North",
                                                                                   "Intersection_ParkEntrySouth2_East",
                                                                                   "Intersection_ParkEntrySouth2_South",
                                                                                   "Intersection_ParkEntrySouth_East"]},
    "Intersection_ParkEntrySouth2_East": {"coords": (309, -975, 11), "neighbors": ["Intersection_ParkEntrySouth2_North",
                                                                                   "Intersection_ParkEntrySouth2_West",
                                                                                   "Intersection_ParkEntrySouth2_South",
                                                                                   "Intersection_RaceChicane_West"]},
    "Intersection_ParkEntrySouth2_South": {"coords": (275, -970, 12),
                                           "neighbors": ["Intersection_ParkEntrySouth2_North",
                                                         "Intersection_ParkEntrySouth2_West",
                                                         "Intersection_ParkEntrySouth2_East",
                                                         "Intersection_WesternCarPark_North"]},

    "Intersection_RaceChicane_North": {"coords": (547, -991, 8),
                                       "neighbors": ["Intersection_RaceChicane_West", "Intersection_RaceChicane_East",
                                                     "Corner_ParkSmallSouth_South"]},
    "Intersection_RaceChicane_West": {"coords": (540, -1010, 8),
                                      "neighbors": ["Intersection_RaceChicane_North", "Intersection_RaceChicane_East",
                                                    "Intersection_ParkEntrySouth2_East"]},
    "Intersection_RaceChicane_East": {"coords": (571, -1003, 9),
                                      "neighbors": ["Intersection_RaceChicane_North", "Intersection_RaceChicane_West",
                                                    "Corner_RaceChicane_South"]},

    "Corner_RaceChicane_North": {"coords": (599, -757, 8),
                                 "neighbors": ["Corner_RaceChicane_Middle", "Intersection_RaceEastPark_South"]},
    "Corner_RaceChicane_Middle": {"coords": (610, -810, 7),
                                  "neighbors": ["Corner_RaceChicane_South", "Corner_RaceChicane_North"]},
    "Corner_RaceChicane_South": {"coords": (582, -877, 7),
                                 "neighbors": ["Corner_RaceChicane_Middle", "Intersection_RaceChicane_East"]},

    "Intersection_RaceEastPark_North": {"coords": (288, -297, 5), "neighbors": ["Intersection_RaceEastPark_West",
                                                                                "Intersection_RaceEastPark_South",
                                                                                "Intersection_RaceNationalEast_South"]},
    "Intersection_RaceEastPark_West": {"coords": (298, -338, 4), "neighbors": ["Intersection_RaceEastPark_North",
                                                                               "Intersection_RaceEastPark_South",
                                                                               "Intersection_ParkBridge_North"]},
    "Intersection_RaceEastPark_South": {"coords": (326, -354, 3), "neighbors": ["Intersection_RaceEastPark_North",
                                                                                "Intersection_RaceEastPark_West",
                                                                                "Corner_RaceChicane_North"]},

    "Intersection_RaceNationalEast_North": {"coords": (178, 16, 7), "neighbors": ["Intersection_RaceNationalEast_West",
                                                                                  "Intersection_RaceNationalEast_South",
                                                                                  "Corner_RaceEast_North"]},
    "Intersection_RaceNationalEast_West": {"coords": (144, -44, 7), "neighbors": ["Intersection_RaceNationalEast_North",
                                                                                  "Intersection_RaceNationalEast_South",
                                                                                  "Intersection_RacePaddock_East"]},
    "Intersection_RaceNationalEast_South": {"coords": (204, -62, 7),
                                            "neighbors": ["Intersection_RaceNationalEast_North",
                                                          "Intersection_RaceNationalEast_West",
                                                          "Intersection_RaceEastPark_North"]},

    "Corner_RaceEast_North": {"coords": (-59, 21, 1), "neighbors": ["Intersection_RaceNationalEast_North",
                                                                    "Intersection_RacePaddockBridge_South"]},

    "Intersection_RacePaddockBridge_North": {"coords": (-66, 83, 1),
                                             "neighbors": ["Intersection_RacePaddockBridge_East",
                                                           "Intersection_RacePaddockBridge_South",
                                                           "Intersection_MidPaddockRace3_South"]},
    "Intersection_RacePaddockBridge_East": {"coords": (-46, 73, 1),
                                            "neighbors": ["Intersection_RacePaddockBridge_North",
                                                          "Intersection_RacePaddockBridge_South",
                                                          "Intersection_PaddockBridge_South"]},
    "Intersection_RacePaddockBridge_South": {"coords": (-66, 48, 1),
                                             "neighbors": ["Intersection_RacePaddockBridge_North",
                                                           "Intersection_RacePaddockBridge_East",
                                                           "Corner_RaceEast_North"]},

    "Intersection_PaddockBridge_North": {"coords": (8, -125, 5), "neighbors": ["Intersection_PaddockBridge_South",
                                                                               "Intersection_PaddockBridge_East",
                                                                               "Intersection_PaddockBridge_West",
                                                                               "Intersection_DustinHofmannLot_West"]},
    "Intersection_PaddockBridge_South": {"coords": (-14, 90, 5), "neighbors": ["Intersection_PaddockBridge_North",
                                                                               "Intersection_PaddockBridge_East",
                                                                               "Intersection_PaddockBridge_West",
                                                                               "Intersection_RacePaddockBridge_East"]},
    "Intersection_PaddockBridge_East": {"coords": (32, 109, 6), "neighbors": ["Intersection_PaddockBridge_North",
                                                                              "Intersection_PaddockBridge_South",
                                                                              "Intersection_PaddockBridge_West",
                                                                              "Intersection_WesternMiddle_West"]},
    "Intersection_PaddockBridge_West": {"coords": (-34, 104, 6), "neighbors": ["Intersection_PaddockBridge_North",
                                                                               "Intersection_PaddockBridge_South",
                                                                               "Intersection_PaddockBridge_East",
                                                                               "Intersection_Bridge_East"]},

    "Intersection_DustinHofmannLot_North": {"coords": (-7, 261, 2), "neighbors": ["Intersection_DustinHofmannLot_West",
                                                                                  "Intersection_DustinHofmannLot_East",
                                                                                  "Corner_DustinHofmann_South"]},
    "Intersection_DustinHofmannLot_West": {"coords": (18, 180, 1), "neighbors": ["Intersection_DustinHofmannLot_North",
                                                                                 "Intersection_DustinHofmannLot_East",
                                                                                 "Intersection_PaddockBridge_North"]},
    "Intersection_DustinHofmannLot_East": {"coords": (63, 205, 4), "neighbors": ["Intersection_DustinHofmannLot_North",
                                                                                 "Intersection_DustinHofmannLot_West",
                                                                                 "Intersection_DustinHofmann_West"]},

    "Corner_DustinHofmann_South": {"coords": (-38, 331, 4),
                                   "neighbors": ["Intersection_DustinHofmannLot_North", "Corner_DustinHofmann_North"]},
    "Corner_DustinHofmann_North": {"coords": (-55, 483, 12),
                                   "neighbors": ["Corner_DustinHofmann_South", "Intersection_WesternSmall_South"]},

    "Intersection_WesternSmall_North": {"coords": (-46, 776, 20), "neighbors": ["Intersection_WesternSmall_South",
                                                                                "Intersection_WesternSmall_East",
                                                                                "Corner_NorthSmall_East"]},
    "Intersection_WesternSmall_South": {"coords": (-52, 733, 19), "neighbors": ["Intersection_WesternSmall_North",
                                                                                "Intersection_WesternSmall_East",
                                                                                "Corner_DustinHofmann_North"]},
    "Intersection_WesternSmall_East": {"coords": (-41, 757, 20), "neighbors": ["Intersection_WesternSmall_North",
                                                                               "Intersection_WesternSmall_South",
                                                                               "Intersection_NorthWestern2_West"]},

    "Corner_NorthSmall_East": {"coords": (-13, 974, 21),
                               "neighbors": ["Corner_NorthSmall_Middle", "Intersection_WesternSmall_North"]},
    "Corner_NorthSmall_Middle": {"coords": (-65, 1020, 21),
                                 "neighbors": ["Corner_NorthSmall_East", "Corner_NorthSmall_West"]},
    "Corner_NorthSmall_West": {"coords": (-246, 973, 17),
                               "neighbors": ["Corner_NorthSmall_Middle", "Intersection_NextToRace_North"]},

    "Intersection_NextToRace_North": {"coords": (-237, 770, 9),
                                      "neighbors": ["Intersection_NextToRace_West", "Intersection_NextToRace_South",
                                                    "Corner_NorthSmall_West"]},
    "Intersection_NextToRace_West": {"coords": (-272, 736, 10),
                                     "neighbors": ["Intersection_NextToRace_North", "Intersection_NextToRace_South",
                                                   "Intersection_ScavierNorth_East"]},
    "Intersection_NextToRace_South": {"coords": (-234, 680, 6),
                                      "neighbors": ["Intersection_NextToRace_North", "Intersection_NextToRace_West",
                                                    "Corner_NextToRace_North"]},

    "Corner_NextToRace_North": {"coords": (-234, 525, 3),
                                "neighbors": ["Intersection_NextToRace_South", "Corner_NextToRace_MidNorth"]},
    "Corner_NextToRace_MidNorth": {"coords": (-234, 390, 3),
                                   "neighbors": ["Corner_NextToRace_MidSouth", "Corner_NextToRace_North"]},
    "Corner_NextToRace_MidSouth": {"coords": (-234, 219, 6),
                                   "neighbors": ["Corner_NextToRace_MidNorth", "Corner_NextToRace_South"]},
    "Corner_NextToRace_South": {"coords": (-233, 149, 9),
                                "neighbors": ["Corner_NextToRace_MidSouth", "Intersection_NextToRace2_North"]},

    "Intersection_NextToRace2_North": {"coords": (-233, 38, 14),
                                       "neighbors": ["Intersection_NextToRace2_West", "Intersection_NextToRace2_East",
                                                     "Intersection_NextToRace2_South", "Corner_NextToRace_South"]},
    "Intersection_NextToRace2_West": {"coords": (-247, 17, 15),
                                      "neighbors": ["Intersection_NextToRace2_North", "Intersection_NextToRace2_East",
                                                    "Intersection_NextToRace2_South",
                                                    "Intersection_KartingNational2_East"]},
    "Intersection_NextToRace2_East": {"coords": (-228, 15, 15),
                                      "neighbors": ["Intersection_NextToRace2_North", "Intersection_NextToRace2_West",
                                                    "Intersection_NextToRace2_South",
                                                    "Intersection_RaceEndOfStraightSmall_West"]},
    "Intersection_NextToRace2_South": {"coords": (-235, 2, 16),
                                       "neighbors": ["Intersection_NextToRace2_North", "Intersection_NextToRace2_West",
                                                     "Intersection_NextToRace2_East",
                                                     "Intersection_KartingNextToRace_North"]},

    "Intersection_KartingNextToRace_North": {"coords": (-235, -53, 16),
                                             "neighbors": ["Intersection_KartingNextToRace_West",
                                                           "Intersection_KartingNextToRace_South",
                                                           "Intersection_NextToRace2_South"]},
    "Intersection_KartingNextToRace_West": {"coords": (-249, -65, 15),
                                            "neighbors": ["Intersection_KartingNextToRace_North",
                                                          "Intersection_KartingNextToRace_South",
                                                          "Corner_NextToKartingNational_South"]},
    "Intersection_KartingNextToRace_South": {"coords": (-238, -72, 15),
                                             "neighbors": ["Intersection_KartingNextToRace_North",
                                                           "Intersection_KartingNextToRace_West",
                                                           "Corner_NextToKartingNationalAndRace_South"]},

    "Corner_NextToKartingNational_South": {"coords": (-304, 70, 15),
                                           "neighbors": ["Intersection_KartingNextToRace_West",
                                                         "Intersection_KartingNational_South"]},

    "Corner_NextToKartingNationalAndRace_South": {"coords": (-249, -129, 14),
                                                  "neighbors": ["Intersection_KartingNextToRace_South",
                                                                "Intersection_RaceKarting_North"]},

    "Intersection_RaceKarting_North": {"coords": (-328, -176, 16),
                                       "neighbors": ["Intersection_RaceKarting_East", "Intersection_RaceKarting_West",
                                                     "Corner_NextToKartingNationalAndRace_South",
                                                     "Intersection_BehindPoliceHQ_East"]},
    "Intersection_RaceKarting_East": {"coords": (-320, -198, 16),
                                      "neighbors": ["Intersection_RaceKarting_North", "Intersection_RaceKarting_West",
                                                    "Intersection_RaceEndOfStraight_South"]},
    "Intersection_RaceKarting_West": {"coords": (-351, -205, 17),
                                      "neighbors": ["Intersection_RaceKarting_North", "Intersection_RaceKarting_East",
                                                    "Corner_Race_West"]},

    "Corner_Race_West": {"coords": (-606, -309, 25),
                         "neighbors": ["Intersection_RaceKarting_West", "Intersection_RaceNational_North"]},

    "Intersection_RaceNational_North": {"coords": (-425, -603, 33),
                                        "neighbors": ["Corner_Race_West", "Intersection_RaceNational_South",
                                                      "Intersection_RaceNational_East"]},
    "Intersection_RaceNational_South": {"coords": (-372, -668, 33), "neighbors": ["Intersection_RaceNational_North",
                                                                                  "Intersection_RaceNational_East",
                                                                                  "Intersection_RaceWesternEnd_North"]},
    "Intersection_RaceNational_East": {"coords": (-350, -621, 33), "neighbors": ["Intersection_RaceNational_North",
                                                                                 "Intersection_RaceNational_South",
                                                                                 "Corner_RaceNational_West"]},

    "Corner_RaceNational_West": {"coords": (-226, -469, 20), "neighbors": ["Intersection_RaceNational_East",
                                                                           "Intersection_RaceNationalMiddle_South"]},

    "Intersection_RaceNationalMiddle_North": {"coords": (-293, -373, 20),
                                              "neighbors": ["Intersection_RaceNationalMiddle_South",
                                                            "Intersection_RaceNationalMiddle_East",
                                                            "Intersection_RaceNationalMiddle2_West"]},
    "Intersection_RaceNationalMiddle_South": {"coords": (-303, -409, 20),
                                              "neighbors": ["Intersection_RaceNationalMiddle_North",
                                                            "Intersection_RaceNationalMiddle_East",
                                                            "Corner_RaceNational_West"]},
    "Intersection_RaceNationalMiddle_East": {"coords": (-285, -390, 20),
                                             "neighbors": ["Intersection_RaceNationalMiddle_North",
                                                           "Intersection_RaceNationalMiddle_South",
                                                           "Intersection_RaceNationalPark_West"]},

    "Intersection_RaceNationalMiddle2_South": {"coords": (-227, -357, 21),
                                               "neighbors": ["Intersection_RaceNationalMiddle2_West",
                                                             "Intersection_RaceNationalMiddle2_East",
                                                             "Intersection_RaceNationalPark_North"]},
    "Intersection_RaceNationalMiddle2_West": {"coords": (-228, -344, 21),
                                              "neighbors": ["Intersection_RaceNationalMiddle2_South",
                                                            "Intersection_RaceNationalMiddle2_East",
                                                            "Intersection_RaceNationalMiddle_North"]},
    "Intersection_RaceNationalMiddle2_East": {"coords": (-195, -347, 21),
                                              "neighbors": ["Intersection_RaceNationalMiddle2_South",
                                                            "Intersection_RaceNationalMiddle2_West",
                                                            "Intersection_RacePaddock_West"]},

    "Intersection_RacePaddock_North": {"coords": (-126, -349, 18),
                                       "neighbors": ["Intersection_RacePaddock_West", "Intersection_RacePaddock_East",
                                                     "Intersection_EndOfPaddock_East"]},
    "Intersection_RacePaddock_West": {"coords": (-140, -356, 19),
                                      "neighbors": ["Intersection_RacePaddock_North", "Intersection_RacePaddock_East",
                                                    "Intersection_RaceNationalMiddle2_East"]},
    "Intersection_RacePaddock_East": {"coords": (-95, -362, 17),
                                      "neighbors": ["Intersection_RacePaddock_North", "Intersection_RacePaddock_West",
                                                    "Intersection_RaceNationalEast_West"]},

    "Intersection_RaceNationalPark_North": {"coords": (-247, -385, 20),
                                            "neighbors": ["Intersection_RaceNationalPark_West",
                                                          "Intersection_RaceNationalPark_East",
                                                          "Intersection_RaceNationalMiddle2_South"]},
    "Intersection_RaceNationalPark_West": {"coords": (-260, -397, 20),
                                           "neighbors": ["Intersection_RaceNationalPark_North",
                                                         "Intersection_RaceNationalPark_East",
                                                         "Intersection_RaceNationalMiddle_East"]},
    "Intersection_RaceNationalPark_East": {"coords": (-231, -406, 21),
                                           "neighbors": ["Intersection_RaceNationalPark_North",
                                                         "Intersection_RaceNationalPark_West",
                                                         "Intersection_RaceNationalPark2_West"]},

    "Intersection_RaceNationalPark2_South": {"coords": (-156, -441, 22),
                                             "neighbors": ["Intersection_RaceNationalPark2_West",
                                                           "Intersection_RaceNationalPark2_East",
                                                           "Corner_ParkSmall_North"]},
    "Intersection_RaceNationalPark2_West": {"coords": (-171, -423, 22),
                                            "neighbors": ["Intersection_RaceNationalPark2_South",
                                                          "Intersection_RaceNationalPark2_East",
                                                          "Intersection_RaceNationalPark_East"]},
    "Intersection_RaceNationalPark2_East": {"coords": (-131, -437, 25),
                                            "neighbors": ["Intersection_RaceNationalPark2_South",
                                                          "Intersection_RaceNationalPark2_West",
                                                          "Intersection_ParkMiddle_West"]},

    "Corner_ParkSmall_North": {"coords": (-339, -654, 33),
                               "neighbors": ["Corner_ParkSmall_South", "Intersection_RaceNationalPark2_South"]},
    "Corner_ParkSmall_South": {"coords": (-254, -867, 24),
                               "neighbors": ["Corner_ParkSmall_North", "Intersection_RaceSouthPark_West"]},

    "Intersection_RaceSouthPark_South": {"coords": (71, -743, 11), "neighbors": ["Intersection_RaceSouthPark_West",
                                                                                 "Intersection_RaceSouthPark_East",
                                                                                 "Intersection_ParkEntrySouth_North"]},
    "Intersection_RaceSouthPark_West": {"coords": (53, -742, 11), "neighbors": ["Intersection_RaceSouthPark_South",
                                                                                "Intersection_RaceSouthPark_East",
                                                                                "Corner_ParkSmall_South"]},
    "Intersection_RaceSouthPark_East": {"coords": (75, -727, 11), "neighbors": ["Intersection_RaceSouthPark_South",
                                                                                "Intersection_RaceSouthPark_West",
                                                                                "Intersection_RaceSouthPark2_West"]},

    "Intersection_RaceSouthPark2_North": {"coords": (96, -683, 11), "neighbors": ["Intersection_RaceSouthPark2_South",
                                                                                  "Intersection_RaceSouthPark2_West",
                                                                                  "Intersection_ParkMiddle_South"]},
    "Intersection_RaceSouthPark2_South": {"coords": (131, -711, 11), "neighbors": ["Intersection_RaceSouthPark2_North",
                                                                                   "Intersection_RaceSouthPark2_West",
                                                                                   "Intersection_ParkEntrySouth2_North"]},
    "Intersection_RaceSouthPark2_West": {"coords": (99, -705, 11), "neighbors": ["Intersection_RaceSouthPark2_North",
                                                                                 "Intersection_RaceSouthPark2_South",
                                                                                 "Intersection_RaceSouthPark_East"]},

    "Corner_ParkSmallSouth_North": {"coords": (579, -771, 9),
                                    "neighbors": ["Corner_ParkSmallSouth_Middle", "Intersection_ParkBridge2_South"]},
    "Corner_ParkSmallSouth_Middle": {"coords": (587, -806, 9),
                                     "neighbors": ["Corner_ParkSmallSouth_North", "Corner_ParkSmallSouth_South"]},
    "Corner_ParkSmallSouth_South": {"coords": (566, -873, 8),
                                    "neighbors": ["Corner_ParkSmallSouth_Middle", "Intersection_RaceChicane_North"]},

    "Intersection_MidPaddockRace_North": {"coords": (-118, 316, 3), "neighbors": ["Intersection_MidPaddockRace_South",
                                                                                  "Intersection_MidPaddockRace_East",
                                                                                  "Intersection_Pit_South"]},
    "Intersection_MidPaddockRace_South": {"coords": (-118, 282, 4), "neighbors": ["Intersection_MidPaddockRace_North",
                                                                                  "Intersection_MidPaddockRace_East",
                                                                                  "Intersection_UpperPit_North"]},
    "Intersection_MidPaddockRace_East": {"coords": (-110, 300, 3), "neighbors": ["Intersection_MidPaddockRace_North",
                                                                                 "Intersection_MidPaddockRace_South",
                                                                                 "Intersection_MidPaddockRace2_West"]},

    "Intersection_MidPaddockRace2_North": {"coords": (-86, 316, 3), "neighbors": ["Intersection_MidPaddockRace2_South",
                                                                                  "Intersection_MidPaddockRace2_West",
                                                                                  "Intersection_RaceSmallNorth1_South"]},
    "Intersection_MidPaddockRace2_South": {"coords": (-85, 282, 2), "neighbors": ["Intersection_MidPaddockRace2_North",
                                                                                  "Intersection_MidPaddockRace2_West",
                                                                                  "Intersection_MidPaddockRace3_West"]},
    "Intersection_MidPaddockRace2_West": {"coords": (-91, 300, 3), "neighbors": ["Intersection_MidPaddockRace2_North",
                                                                                 "Intersection_MidPaddockRace2_South",
                                                                                 "Intersection_MidPaddockRace_East"]},

    "Intersection_MidPaddockRace3_North": {"coords": (-70, 245, 1), "neighbors": ["Intersection_MidPaddockRace3_South",
                                                                                  "Intersection_MidPaddockRace3_West",
                                                                                  "Intersection_RaceSmallNorth2_South"]},
    "Intersection_MidPaddockRace3_South": {"coords": (-69, 220, 1), "neighbors": ["Intersection_MidPaddockRace3_North",
                                                                                  "Intersection_MidPaddockRace3_West",
                                                                                  "Intersection_RacePaddockBridge_North"]},
    "Intersection_MidPaddockRace3_West": {"coords": (-82, 232, 1), "neighbors": ["Intersection_MidPaddockRace3_North",
                                                                                 "Intersection_MidPaddockRace3_South",
                                                                                 "Intersection_MidPaddockRace2_South"]},

    "Intersection_RaceSmallNorth1_North": {"coords": (-88, 752, 19), "neighbors": ["Intersection_RaceSmallNorth1_South",
                                                                                   "Intersection_RaceSmallNorth1_East",
                                                                                   "Intersection_RaceNorth1_East"]},
    "Intersection_RaceSmallNorth1_South": {"coords": (-90, 729, 19), "neighbors": ["Intersection_RaceSmallNorth1_North",
                                                                                   "Intersection_RaceSmallNorth1_East",
                                                                                   "Intersection_MidPaddockRace2_North"]},
    "Intersection_RaceSmallNorth1_East": {"coords": (-86, 743, 19), "neighbors": ["Intersection_RaceSmallNorth1_North",
                                                                                  "Intersection_RaceSmallNorth1_South",
                                                                                  "Intersection_RaceSmallNorth2_West"]},

    "Intersection_RaceSmallNorth2_North": {"coords": (-72, 760, 19), "neighbors": ["Intersection_RaceSmallNorth2_South",
                                                                                   "Intersection_RaceSmallNorth2_West",
                                                                                   "Intersection_RaceNorth2_East"]},
    "Intersection_RaceSmallNorth2_South": {"coords": (-75, 728, 19), "neighbors": ["Intersection_RaceSmallNorth2_North",
                                                                                   "Intersection_RaceSmallNorth2_West",
                                                                                   "Intersection_MidPaddockRace3_North"]},
    "Intersection_RaceSmallNorth2_West": {"coords": (-80, 747, 19), "neighbors": ["Intersection_RaceSmallNorth2_North",
                                                                                  "Intersection_RaceSmallNorth2_South",
                                                                                  "Intersection_RaceSmallNorth1_East"]},

    "Intersection_RaceNorth1_North": {"coords": (-123, 946, 18),
                                      "neighbors": ["Intersection_RaceNorth1_West", "Intersection_RaceNorth1_East",
                                                    "Intersection_RaceNorth2_South"]},
    "Intersection_RaceNorth1_West": {"coords": (-126, 940, 17),
                                     "neighbors": ["Intersection_RaceNorth1_North", "Intersection_RaceNorth1_East",
                                                   "Corner_RaceSmallSouth_North"]},
    "Intersection_RaceNorth1_East": {"coords": (-112, 944, 18),
                                     "neighbors": ["Intersection_RaceNorth1_North", "Intersection_RaceNorth1_West",
                                                   "Intersection_RaceSmallNorth1_North"]},

    "Intersection_RaceNorth2_East": {"coords": (-112, 963, 19),
                                     "neighbors": ["Intersection_RaceNorth2_South", "Intersection_RaceNorth2_West",
                                                   "Intersection_RaceSmallNorth2_North"]},
    "Intersection_RaceNorth2_South": {"coords": (-128, 950, 17),
                                      "neighbors": ["Intersection_RaceNorth2_East", "Intersection_RaceNorth2_West",
                                                    "Intersection_RaceNorth1_North"]},
    "Intersection_RaceNorth2_West": {"coords": (-144, 954, 17),
                                     "neighbors": ["Intersection_RaceNorth2_East", "Intersection_RaceNorth2_South",
                                                   "Corner_RaceNorth_North"]},

    "Corner_RaceSmallSouth_North": {"coords": (-197, 830, 11),
                                    "neighbors": ["Corner_RaceSmallSouth_South", "Intersection_RaceNorth1_West"]},
    "Corner_RaceSmallSouth_South": {"coords": (-197, -764, 8),
                                    "neighbors": ["Corner_RaceSmallSouth_North", "Corner_RaceSmallSouth_South2"]},
    "Corner_RaceSmallSouth_South2": {"coords": (-188, -591, 4),
                                     "neighbors": ["Corner_RaceSmallSouth_South", "Intersection_RacePit2_East"]},

    "Corner_RaceNorth_North": {"coords": (-215, 763, 8),
                               "neighbors": ["Intersection_RaceNorth2_West", "Intersection_RacePit_North"]},

    "Intersection_RacePit_North": {"coords": (-215, 685, 6),
                                   "neighbors": ["Intersection_RacePit_South", "Intersection_RacePit_East",
                                                 "Corner_RaceNorth_North"]},
    "Intersection_RacePit_South": {"coords": (-215, 570, 4),
                                   "neighbors": ["Intersection_RacePit_North", "Intersection_RacePit_East",
                                                 "Corner_RaceStart_North"]},
    "Intersection_RacePit_East": {"coords": (-201, 577, 4),
                                  "neighbors": ["Intersection_RacePit_North", "Intersection_RacePit_South",
                                                "Intersection_RacePit2_North"]},

    "Intersection_RacePit2_North": {"coords": (-201, 566, 3),
                                    "neighbors": ["Intersection_RacePit2_South", "Intersection_RacePit2_East",
                                                  "Intersection_RacePit_East"]},
    "Intersection_RacePit2_South": {"coords": (-202, 547, 3),
                                    "neighbors": ["Intersection_RacePit2_North", "Intersection_RacePit2_East",
                                                  "Intersection_RacePitMiddle_North"]},
    "Intersection_RacePit2_East": {"coords": (-191, 557, 3),
                                   "neighbors": ["Intersection_RacePit2_North", "Intersection_RacePit2_South",
                                                 "Corner_RaceSmallSouth_South2"]},

    "Intersection_RacePitMiddle_North": {"coords": (-199, 414, 2), "neighbors": ["Intersection_RacePitMiddle_South",
                                                                                 "Intersection_RacePitMiddle_East",
                                                                                 "Intersection_RacePit2_South"]},
    "Intersection_RacePitMiddle_South": {"coords": (-199, 385, 2), "neighbors": ["Intersection_RacePitMiddle_North",
                                                                                 "Intersection_RacePitMiddle_East",
                                                                                 "Intersection_RacePitSouth_East"]},
    "Intersection_RacePitMiddle_East": {"coords": (-186, 399, 2), "neighbors": ["Intersection_RacePitMiddle_North",
                                                                                "Intersection_RacePitMiddle_South",
                                                                                "Corner_PitLot_Middle"]},

    "Corner_PitLot_Middle": {"coords": (-168, 399, 2),
                             "neighbors": ["Intersection_PitLot_South", "Intersection_RacePitMiddle_East"]},

    "Intersection_PitLot_South": {"coords": (-170, 543, 3),
                                  "neighbors": ["Corner_PitLot_Middle", "Intersection_PitLot_North"]},
    "Intersection_PitLot_North": {"coords": (-150, 587, 4),
                                  "neighbors": ["Intersection_PitLot_South", "Intersection_Pit_West"]},

    "Corner_RaceStart_North": {"coords": (-215, 526, 3),
                               "neighbors": ["Corner_RaceStart_Middle", "Intersection_RacePit_South"]},
    "Corner_RaceStart_Middle": {"coords": (-215, 390, 2),
                                "neighbors": ["Corner_RaceStart_North", "Intersection_RacePitSouth_North"]},

    "Intersection_RacePitSouth_North": {"coords": (-215, 223, 5), "neighbors": ["Intersection_RacePitSouth_South",
                                                                                "Intersection_RacePitSouth_East",
                                                                                "Corner_RaceStart_Middle"]},
    "Intersection_RacePitSouth_South": {"coords": (-215, 112, 10), "neighbors": ["Intersection_RacePitSouth_North",
                                                                                 "Intersection_RacePitSouth_East",
                                                                                 "Intersection_RaceEndOfStraightSmall_North"]},
    "Intersection_RacePitSouth_East": {"coords": (-202, 223, 5), "neighbors": ["Intersection_RacePitSouth_North",
                                                                               "Intersection_RacePitSouth_South",
                                                                               "Intersection_RacePitMiddle_South"]},

    "Intersection_RaceEndOfStraightSmall_North": {"coords": (-215, 24, 15),
                                                  "neighbors": ["Intersection_RaceEndOfStraightSmall_South",
                                                                "Intersection_RaceEndOfStraightSmall_West",
                                                                "Intersection_RacePitSouth_South"]},
    "Intersection_RaceEndOfStraightSmall_South": {"coords": (-215, -14, 16),
                                                  "neighbors": ["Intersection_RaceEndOfStraightSmall_North",
                                                                "Intersection_RaceEndOfStraightSmall_West",
                                                                "Intersection_RaceEndOfStraight_North"]},
    "Intersection_RaceEndOfStraightSmall_West": {"coords": (-223, 5, 16),
                                                 "neighbors": ["Intersection_RaceEndOfStraightSmall_North",
                                                               "Intersection_RaceEndOfStraightSmall_South",
                                                               "Intersection_NextToRace2_East"]},

    "Intersection_RaceEndOfStraight_North": {"coords": (-215, -92, 15),
                                             "neighbors": ["Intersection_RaceEndOfStraight_South",
                                                           "Intersection_RaceEndOfStraight_East",
                                                           "Intersection_RaceEndOfStraightSmall_South"]},
    "Intersection_RaceEndOfStraight_South": {"coords": (-217, -125, 15),
                                             "neighbors": ["Intersection_RaceEndOfStraight_North",
                                                           "Intersection_RaceEndOfStraight_East",
                                                           "Intersection_RaceKarting_East"]},
    "Intersection_RaceEndOfStraight_East": {"coords": (-197, -101, 15),
                                            "neighbors": ["Intersection_RaceEndOfStraight_North",
                                                          "Intersection_RaceEndOfStraight_South",
                                                          "Intersection_Medical_West"]},

}


def find_closest_intersection(x, y, z, intersections):
    min_distance = float('inf')
    closest_intersection = None

    for intersection_name, intersection_data in intersections.items():
        coords = intersection_data["coords"]
        distance = dist((x, y, z), coords)

        if distance < min_distance:
            min_distance = distance
            closest_intersection = intersection_name

    return closest_intersection


def startnav():
    global route_follower
    start = find_closest_intersection(xCoord, yCoord, zCoord, points_westhill)
    print(start)
    end = "Intersection_ParkEntrySouth2_South"

    route = dijkstra_shortest_path(points_westhill, start, end)

    route_follower = NaviRoute(route, points_westhill)


insim.bind(pyinsim.ISP_MCI, get_car_data)
pyinsim.run()
