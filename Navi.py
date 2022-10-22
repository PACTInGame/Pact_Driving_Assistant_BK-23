import math
from threading import Thread

import pyinsim
from pygame import mixer

insim = pyinsim.insim(b'127.0.0.1', 29999, Admin=b'', Flags=pyinsim.ISF_MCI | pyinsim.ISF_LOCAL, Interval=500)

PLID = 0
points = [[-253, -1087, 26, 1], [-185, -1061, 25, 2], [709, -1018, 15, 3], [325, -189, 7, 4], [220, 100, 9, 5],
          [3, 105, 6, 6], [-98, 103, 6, 7], [-118, -23, 12, 8], [-118, -94, 17, 9], [-143, -125, 16, 10],
          [-574, -302, 18, 11], [-712, -188, 26, 12], [-767, -95, 26, 13], [-309, 405, 15, 14], [-348, 691, 13, 15],
          [-72, 1037, 13, 16],  [16, 962, 21, 17], [-7, 796, 21, 18], [-39, 757, 20, 19], [-15, 276, 2, 20]]
xCoord = 0
yCoord = 0
zCoord = 0
soundtoplay = 0
soundplayed = 0


def outgauge(outgauge, packet):
    global PLID
    PLID = packet.PLID


outgauge = pyinsim.outgauge(b'127.0.0.1', 30000, outgauge, 30.0)


def dist(a=(0, 0, 0), b=(0, 0, 0)):
    return math.sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]) + (b[2] - a[2]) * (b[2] - a[2]))


mixer.init()


def playsound():
    global soundplayed
    if soundtoplay != soundplayed:
        soundplayed = soundtoplay
        mixer.music.load('Navi\\' + str(soundtoplay) + '.mp3')
        mixer.music.play()


def get_car_data(insim, mci):
    global cars, xCoord, yCoord, zCoord, soundtoplay
    # Save new arrays of car data in update cars and then override cars, so that no data gets lost or doubled
    distances_to_points = []

    for car in mci.Info:
        if car.PLID == PLID:
            xCoord = car.X / 65536
            yCoord = car.Y / 65536
            zCoord = car.Z / 65536

    for point in points:
        distance_to_car = dist((xCoord, yCoord, zCoord), (point[0], point[1], point[2]))
        distances_to_points.append([distance_to_car, point[3]])
    s = [5000, 0]
    for sound in distances_to_points:
        if sound[0] <= s[0]:
            s = (sound[0], sound[1])
    if s[0] <= 20:
        print("play_sound", str(s[1]))
        soundtoplay = s[1]

    play_thread = Thread(target=playsound)
    play_thread.start()


insim.bind(pyinsim.ISP_MCI, get_car_data)

pyinsim.run()
