# -*- coding: utf-8 -*-
import math
import pyautogui
from pygame import mouse

import PSC
import active_lane_keeping
import bus_routes
import check_LFS_running
import cruise_control
import keyboard
import load_lane_data
import pyinsim
import random
import sys
import time
import pygame
from threading import Thread
import forward_collision_warning
import gearbox
import get_settings
import helpers
import park_assist
import setting
import wheel_support
from blind_spot_warning import check_blindspots
from shapely.geometry import Polygon, Point
from vehicle import Vehicle
import tkinter as tk

while not check_LFS_running.is_lfs_running():
    print("Waiting for LFS to start.")
    time.sleep(5)
print("LFS.exe seems to be running. Starting!\n\n")
pyautogui.FAILSAFE = False
time.sleep(0.2)
print('PACT DRIVING ASSISTANT VERSION 11.9.9.1')
print('Starting.')
time.sleep(0.2)
for i in range(21):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-20s] %d%%" % ('=' * i, 5 * i))
    sys.stdout.flush()
    time.sleep(0.05)
print("")
print('Start successful')
time.sleep(0.2)
print('Trying to connect to Live for Speed')
time.sleep(0.2)

insim = pyinsim.insim(b'127.0.0.1', 29999, Admin=b'', Prefix=b"$",
                      Flags=pyinsim.ISF_MCI | pyinsim.ISF_LOCAL, Interval=200)
time.sleep(0.1)
insim.send(pyinsim.ISP_MSL,
           Msg=b"PACT Driving Assistant Active")
print('Loading settings')
time.sleep(0.1)
set_def = get_settings.get_settings_from_file()
settings = setting.Setting(set_def[0], set_def[1], set_def[2], set_def[3], set_def[4], set_def[5], set_def[6],
                           set_def[7], set_def[8], set_def[9], set_def[10], set_def[11], set_def[12], set_def[13],
                           set_def[14], set_def[15], set_def[16], set_def[17], set_def[18], set_def[19], set_def[20])
cont_def = get_settings.get_controls_from_file()
SHIFT_UP_KEY = cont_def[0]
SHIFT_DOWN_KEY = cont_def[1]
IGNITION_KEY = cont_def[2]
THROTTLE_AXIS = int(cont_def[3])
BRAKE_AXIS = int(cont_def[4])
STEER_AXIS = int(cont_def[5])
VJOY_AXIS = int(cont_def[6])
VJOY_AXIS1 = int(VJOY_AXIS) + 1
VJOY_AXIS2 = int(VJOY_AXIS) + 2
BRAKE_KEY = cont_def[7]
ACC_KEY = cont_def[8]
HANDBRAKE_KEY = cont_def[9]
controller_throttle, controller_brake, num_joystick = get_settings.get_acc_settings_from_file()
print('In case you need help, hit me up on Discord: Robert M.#6244')

players = {}
cars_on_track = []
cars_relevant = []
cars_previous_speed = []
temp_previous_speed = []
buttons_on_screen = []
for i in range(200):
    buttons_on_screen.append(0)
own_player_id = -1
own_speed = 0
own_rpm = 0
own_gear = 0
own_heading = 0
own_x = 0
own_y = 0
own_steering = 0
own_light = False
accelerator_pressure = 0
brake_pressure = 0
own_gearbox_mode = 0
own_control_mode = 0
collision_warning_intensity = 0
indicators = [0, 0]
track = "none"
roleplay = "civil"
own_player_name = ""
game = False
time_last_check = time.time()
time_menu = time.time()
start_outgauge_again = False
text_entry = False
own_handbrake = False
collision_warning_not_cop = "^2"
own_battery_light = False
auto_clutch = False
vehicle_model = ""
vehicle_model_change = False
current_bus_route = "none"
brake_light = 0
own_warn_multi = 1.0
measuring = False
measure_param = [0, 0, 0, 0]
measuring_fast = False
measuring_very_fast = False
measure_z = 0
warn_multi_arr = []
auto_indicators = "^2"
auto_siren = "^2"
engine_type = "combustion"
indicatorSr = 0
indicatorSl = 0
own_fuel_start = 0
own_fuel_start_capa = 0
own_fuel_moment = 0
own_fuel_avg = 0
own_fuel = 0
own_fuel_was = 0
game_time = 0
own_range = 0
hide_mouse = True
# button 100-110 = park distance control
# button 10-15 = HUD
# button 16 = notifications
# button 17, 18 = blind spot warning
# button 19 - 30, 41-45 = menu
# button 31,32 = waiting in menu
# button 33 - 40 = roleplay
# button 41, 42 = notifications
# button 46 - 48 = lane_buttons
# button 50 = menu lane
# button 51-60 = Bus
# button 61-65 = Police Tracker
# button 66, 67 = menu calculate
# button 68 = auto indicators
# button 69 = strobe assist
# button 70 = ESP
# button 71-75 = more settings
# button 76-80 = fuel stuff
# button 81-85 = ACC
# button 86-90 = Menu
# button 91 = hide_mouse

# TODO Cross-Traffic-Warning
# TODO Lane Keep Assist
# TODO Castle hill 1 sound grand tour

active_lane = False
car_in_control = False
previous_steering = 0
previous_steering2 = 0
previous_steering3 = 0
packets = 0
steering = 0
own_speed_mph = 0


def window():
    global root
    global label, warningImage, crossImage, preWarningImage, label2
    root = tk.Tk()
    # The image must be stored to Tk, or it will be garbage collected.
    preWarningImage = tk.PhotoImage(file='data\\preacute.png')
    warningImage = tk.PhotoImage(file='data\\acute.png')
    label = tk.Label(root, image=warningImage, bg='black')
    label2 = tk.Label(root, image=preWarningImage, bg='black')
    crossImage = tk.PhotoImage(file='data\\cross.png')
    root.configure(background='black')
    root.overrideredirect(True)
    res = settings.resolution
    res = res.split("x")
    res1 = int(res[0]) / 2.16
    res2 = int(res[1]) / 1.95
    root.geometry("200x100+" + str(round(res1)) + "+" + str(round(res2)))
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", "black")
    root.attributes('-alpha', 0.9)
    root.mainloop()
    collision_warning_intensity_was = 0


def change_image_warn():
    global root, label, collision_warning_intensity_was
    if settings.image_hud == "^2":
        label2.pack_forget()
        label.image = warningImage
        label.pack()
        root.update()


def change_image_prewarn():
    global root, label, collision_warning_intensity_was
    if settings.image_hud == "^2":
        label.pack_forget()
        label2.image = preWarningImage
        label2.pack()
        root.update()


def change_image_del():
    global root, label, collision_warning_intensity_was
    label.pack_forget()
    label2.pack_forget()


thread_window = Thread(target=window)
thread_window.start()


def get_collision_state():
    return collision_warning_intensity


def outgauge_packet(outgauge, packet):
    global own_player_id, own_speed, own_rpm, own_gear, accelerator_pressure, brake_pressure, indicators, own_light
    global own_handbrake, own_battery_light, vehicle_model, right_indicator_timer, left_indicator_timer, brake_light
    global vehicle_model_change, own_warn_multi, measuring, measure_param, get_brake_dist, measuring_fast, measuring_very_fast
    global warn_multi_arr, engine_type, active_lane, previous_steering, car_in_control, packets, previous_steering2, previous_steering3
    global steering, indicatorSr, indicatorSl, game_time, own_fuel, rectangles_object, own_speed_mph

    if game:
        game_time = packet.Time
        own_fuel = packet.Fuel
        if roleplay == "civil":
            if indicators[1] != indicatorSr:
                indicatorSr = indicators[1]
                if indicators[1] == 1:
                    helpers.playsound_indicator_on()
                else:
                    helpers.playsound_indicator_off()
            elif indicators[0] != indicatorSl:
                indicatorSl = indicators[0]
                if indicators[0] == 1:
                    helpers.playsound_indicator_on()
                else:
                    helpers.playsound_indicator_off()

        if packets % 10 == 0 and (track == b"WE" or track == b"BL"):
            packets = 0
            if active_lane_prep or active_lane:
                backup = steering

                steer_result = active_lane_keeping.calculate_steering(polygons_r, polygons_l, own_x, own_y,
                                                                      previous_steering, previous_steering2)
                steering, actual = steer_result if steer_result[0] != 0 else (backup, steer_result[1])

                if previous_steering3 != actual:
                    previous_steering = previous_steering2
                    previous_steering2 = previous_steering
                previous_steering3 = actual

            if active_lane:
                if own_control_mode == 2 and not car_in_control:
                    insim.send(pyinsim.ISP_MST, Msg=b"/axis %.1i steer" % VJOY_AXIS2)
                    car_in_control = True

                if car_in_control:
                    wheel_support.brake_slow_steer(steering)
            elif car_in_control:
                car_in_control = False
                insim.send(pyinsim.ISP_MST, Msg=b"/axis %.1i steer" % STEER_AXIS)
        else:
            packets += 1

        if len(warn_multi_arr) == 3 and get_brake_dist:
            x = warn_multi_arr[0]
            x = x + warn_multi_arr[1]
            x = x + warn_multi_arr[2]
            x = x / 3
            warn_multi_arr = []
            own_warn_multi = x
            notification("AEB Calibrated", 2)
            get_brake_dist = False

        if not packet.Car == vehicle_model:
            vehicle_model_change = True
            vehicle_model = packet.Car
            rectangles_object = []
            insim.send(pyinsim.ISP_TINY, ReqI=255, SubT=pyinsim.TINY_AXM)

        if own_player_id == -1:
            own_player_id = packet.PLID
            insim.send(pyinsim.ISP_TINY, ReqI=255, SubT=pyinsim.TINY_NPL)

        if pyinsim.DL_HANDBRAKE & packet.ShowLights:
            own_handbrake = True
        else:
            own_handbrake = False

        own_player_id = packet.PLID
        own_gear = packet.Gear

        if not (collision_warning_intensity == 3 and settings.automatic_emergency_braking == "^2"):
            brake_pressure = packet.Brake
        else:
            brake_pressure = 0

        brake_light = packet.Brake
        accelerator_pressure = packet.Throttle
        own_rpm = packet.RPM
        own_speed = packet.Speed * 3.6
        own_speed_mph = packet.Speed * 2.23
        if get_brake_dist and brake_pressure > 0.999 and 140 < own_speed_mci < 150 and not measuring and -120 < own_steering < 120:
            measuring = True
            measuring_very_fast = True

            measure_param = [own_x, own_y, own_speed_mci, own_z]

        elif get_brake_dist and measure_param[2] - own_speed_mci > 25 and measuring_very_fast:
            measuring = False
            measuring_very_fast = False
            get_brake_dist = False
            measured_dist = math.sqrt(
                (own_x - measure_param[0]) * (own_x - measure_param[0]) + (own_y - measure_param[1]) * (
                        own_y - measure_param[1]))
            print(str(measured_dist) + " at {} from {}".format(own_speed_mci, measure_param[2]))

            if own_speed_mci < 110:
                get_brake_dist = True

                measure_param = [0, 0, 0, 0]

            if measured_dist > 9999999:
                measure_param = [0, 0, 0, 0]
                get_brake_dist = True

            if not get_brake_dist:
                warn_multi_tmp = measured_dist / 1450000

                if warn_multi_tmp > 1.0:
                    diff = warn_multi_tmp - 1
                    warn_multi_tmp = warn_multi_tmp - diff / 2.5
                else:
                    diff = 1 - warn_multi_tmp
                    warn_multi_tmp = warn_multi_tmp + diff / 2.5
                warn_multi_arr.append(warn_multi_tmp)
                measure_param = [0, 0, 0, 0]
                get_brake_dist = True

        if get_brake_dist and brake_pressure > 0.999 and 90 < own_speed_mci < 100 and not measuring and -120 < own_steering < 120:
            measuring = True
            measuring_fast = True

            measure_param = [own_x, own_y, own_speed_mci, own_z]

        elif get_brake_dist and measure_param[2] - own_speed_mci > 25 and measuring_fast:
            measuring = False
            measuring_fast = False
            get_brake_dist = False
            measured_dist = math.sqrt(
                (own_x - measure_param[0]) * (own_x - measure_param[0]) + (own_y - measure_param[1]) * (
                        own_y - measure_param[1]))
            print(str(measured_dist) + " at {} from {}".format(own_speed_mci, measure_param[2]))

            if own_speed_mci < 60:
                get_brake_dist = True

                measure_param = [0, 0, 0, 0]

            if measured_dist > 9999999:
                measure_param = [0, 0, 0, 0]
                get_brake_dist = True

            if not get_brake_dist:
                warn_multi_tmp = measured_dist / 900000

                if warn_multi_tmp > 1.0:
                    diff = warn_multi_tmp - 1
                    warn_multi_tmp = warn_multi_tmp - diff / 2.5
                else:
                    diff = 1 - warn_multi_tmp
                    warn_multi_tmp = warn_multi_tmp + diff / 2.5

                warn_multi_arr.append(warn_multi_tmp)
                measure_param = [0, 0, 0, 0]
                get_brake_dist = True

        if get_brake_dist and brake_pressure > 0.999 and 50 < own_speed_mci < 60 and not measuring and -120 < own_steering < 120:
            measuring = True

            measure_param = [own_x, own_y, own_speed_mci, own_z]

        elif get_brake_dist and measure_param[
            2] - own_speed_mci > 25 and measuring and not measuring_fast and not measuring_very_fast:
            measuring = False
            get_brake_dist = False
            measured_dist = math.sqrt(
                (own_x - measure_param[0]) * (own_x - measure_param[0]) + (own_y - measure_param[1]) * (
                        own_y - measure_param[1]))
            print(str(measured_dist) + " at {} from {}".format(own_speed_mci, measure_param[2]))

            if own_speed_mci < 20:
                get_brake_dist = True

                measure_param = [0, 0, 0, 0]

            if measured_dist > 9999999:
                measure_param = [0, 0, 0, 0]
                get_brake_dist = True

            if not get_brake_dist:
                warn_multi_tmp = measured_dist / 650000

                if warn_multi_tmp > 1.0:
                    diff = warn_multi_tmp - 1
                    warn_multi_tmp = warn_multi_tmp - diff / 2.5
                else:
                    diff = 1 - warn_multi_tmp
                    warn_multi_tmp = warn_multi_tmp + diff / 2.5
                warn_multi_arr.append(warn_multi_tmp)
                measure_param = [0, 0, 0, 0]
                get_brake_dist = True

        if measuring and brake_pressure < 0.998:
            measuring = False
            measuring_fast = False

            measure_param = [0, 0, 0, 0]

        elif not -120 < own_steering < 120 and measuring:
            measuring = False
            measuring_fast = False

            measure_param = [0, 0, 0, 0]

        elif measuring and not -0.3 < own_z / 65536 - measure_param[3] / 65536 < 0.3:
            measuring = False
            measuring_fast = False

            measure_param = [0, 0, 0, 0]
        if b"Batt" in packet.Display1:
            engine_type = "electric"
        else:
            engine_type = "combustion"
        if engine_type == "combustion":
            if 0.1 <= packet.Fuel <= 0.102:
                notification("^3Low Fuel", 1)
            elif 0.048 <= packet.Fuel <= 0.05:
                notification("^1Low Fuel", 1)
        else:
            if 0.1 <= packet.Fuel <= 0.102:
                notification("^3Low Battery", 1)
            elif 0.048 <= packet.Fuel <= 0.05:
                notification("^1Low Battery", 1)

        hudheight = 119 + settings.offseth
        hudwidth = 116 + settings.offsetw

        if not park_assist_active:
            if packet.Fuel < 0.048:
                send_button(13, pyinsim.ISB_DARK, hudheight, hudwidth, 4, 4, '^1<<!>>')
            elif 0.05 <= packet.Fuel <= 0.1:
                send_button(13, pyinsim.ISB_DARK, hudheight, hudwidth, 4, 4, '^3<<!>>')
            else:
                del_button(13)

        own_battery_light = bool(pyinsim.DL_BATTERY & packet.ShowLights)
        indicators[1] = bool(pyinsim.DL_SIGNAL_R & packet.ShowLights)
        indicators[0] = bool(pyinsim.DL_SIGNAL_L & packet.ShowLights)
        own_light = bool(pyinsim.DL_FULLBEAM & packet.ShowLights)

        if settings.head_up_display == "^2" or collision_warning_intensity > 0:
            head_up_display()


outgauge = pyinsim.outgauge('127.0.0.1', 30000, outgauge_packet, 30.0)


def new_player(insim, npl):
    global roleplay, own_player_name, game, own_gearbox_mode, own_control_mode, collision_warning_not_cop
    global auto_clutch, dist_travelled, own_fuel_start, own_fuel_start_capa, own_fuel_capa
    players[npl.PLID] = npl

    cars_already_known = []
    for car in cars_on_track:
        cars_already_known.append(car.player_id)
    if npl.PLID not in cars_already_known:
        cars_on_track.append(Vehicle(0, 0, 0, 0, 0, 0, 0, npl.PLID, 0, 0, npl.CName))
    for car in cars_on_track:
        if npl.PLID == car.player_id:
            if car.cname != npl.CName:
                car.update_cname(npl.CName)
    if npl.PLID == own_player_id:

        flags = [int(i) for i in str("{0:b}".format(npl.Flags))]
        if b"[COP]" in npl.PName:
            roleplay = "cop"

        elif b"[MED]" in npl.PName or b"[RES]" in npl.PName:
            roleplay = "res"

        elif b"[TOW]" in npl.PName:
            roleplay = "tow"
        else:
            roleplay = "civil"
            del_button(33)
            del_button(34)
        if len(flags) >= 4 and flags[-4] == 1:
            own_gearbox_mode = 0  # automatic
        elif len(flags) >= 5 and flags[-5] == 1:
            own_gearbox_mode = 1  # shifter
        else:
            own_gearbox_mode = 2  # sequential
        if len(flags) >= 10 and flags[-10] == 1:
            auto_clutch = True
        else:
            auto_clutch = False
        if len(flags) >= 11 and flags[-11] == 1:
            own_control_mode = 0  # mouse
        elif (len(flags) >= 12 and flags[-12] == 1) or (len(flags) >= 13 and flags[-13] == 1):
            own_control_mode = 1  # keyboard
        else:
            own_control_mode = 2  # wheel
        tmp = npl.PName

        tmp = tmp.replace(b"^1", b"")
        tmp = tmp.replace(b"^2", b"")
        tmp = tmp.replace(b"^3", b"")
        tmp = tmp.replace(b"^4", b"")
        tmp = tmp.replace(b"^5", b"")
        tmp = tmp.replace(b"^6", b"")
        tmp = tmp.replace(b"^7", b"")
        tmp = tmp.replace(b"^8", b"")
        tmp = tmp.replace(b"^9", b"")
        own_player_name = tmp.replace(b"^0", b"")


def player_left(insim, pll):
    try:
        del players[pll.PLID]
        for car in cars_on_track:
            if car.player_id == pll.PLID:
                cars_on_track.remove(car)
                break
    except:
        print("An error occurred in player handling. Typically that's not a problem.")


def player_pits(insim, plp):
    global game
    try:
        del players[plp.PLID]

        for car in cars_on_track:
            if car.player_id == plp.PLID:
                cars_on_track.remove(car)
    except:
        print("An error occurred in player handling. Typically that's not a problem.")


updated_cars = []
num_of_packages_temp = 0
num_of_packages = 0
shift_pressed = False


def rev_bounce():
    keyboard.press("i")
    time.sleep(0.02)
    keyboard.release("i")
    time.sleep(0.01)
    keyboard.press("i")
    time.sleep(0.02)
    keyboard.release("i")


current_stop = []


def bus_route():
    global bus_next_stop_timer, bus_announce_timer, current_stop, current_bus_route

    try:
        if (current_stop[1] == "main_station" or current_stop[1] == "east_station" or current_stop[
            1] == "south_station" or current_stop[
                1] == "west_station" or current_stop[1] == "main_station_a" or current_stop[1] == "main_station_b" or
            current_stop[1] == "drifters_corner" or current_stop[1] == "simons_way") and (
                track == b"SO" or track == b"KY" or track == b"FE" or track == b"BL" or track == b"AS" or track == b"WE"):
            current_bus_route = "none"

    except:
        pass
    if not current_bus_route == "none" and track == b"SO":
        next_stop = bus_routes.stop_dist(current_bus_route, own_x, own_y)

        for stops in next_stop:
            if stops[2] < 15 and own_speed < 2 and bus_announce_timer == 0:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 9")
                bus_announce_timer = 120
                bus_routes.play_stop_sound(current_bus_route, track, bus_route_sound, bus_door_sound)
                bus_next_stop_timer = 40
                current_stop = stops
    elif not current_bus_route == "none" and track == b"KY":
        next_stop = bus_routes.stop_dist_KY(current_bus_route, own_x, own_y)

        for stops in next_stop:
            if stops[2] < 15 and own_speed < 2 and bus_announce_timer == 0:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 9")
                bus_announce_timer = 120

                bus_routes.play_stop_sound(current_bus_route, track, bus_route_sound, bus_door_sound)
                bus_next_stop_timer = 40
                current_stop = stops
    elif not current_bus_route == "none" and track == b"FE":
        next_stop = bus_routes.stop_dist_FE(current_bus_route, own_x, own_y)

        for stops in next_stop:
            if stops[2] < 15 and own_speed < 2 and bus_announce_timer == 0:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 9")
                bus_announce_timer = 120

                bus_routes.play_stop_sound(current_bus_route, track, bus_route_sound, bus_door_sound)
                bus_next_stop_timer = 40
                current_stop = stops

    elif not current_bus_route == "none" and track == b"BL":
        next_stop = bus_routes.stop_dist_BL(current_bus_route, own_x, own_y)

        for stops in next_stop:
            if stops[2] < 15 and own_speed < 2 and bus_announce_timer == 0:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 9")
                bus_announce_timer = 120

                bus_routes.play_stop_sound(current_bus_route, track, bus_route_sound, bus_door_sound)
                bus_next_stop_timer = 40
                current_stop = stops

    elif not current_bus_route == "none" and track == b"AS":
        next_stop = bus_routes.stop_dist_AS(current_bus_route, own_x, own_y)

        for stops in next_stop:
            if stops[2] < 15 and own_speed < 2 and bus_announce_timer == 0:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 9")
                bus_announce_timer = 120

                bus_routes.play_stop_sound(current_bus_route, track, bus_route_sound, bus_door_sound)
                bus_next_stop_timer = 40
                current_stop = stops

    elif not current_bus_route == "none" and track == b"WE":
        next_stop = bus_routes.stop_dist_WE(current_bus_route, own_x, own_y)

        for stops in next_stop:
            if stops[2] < 15 and own_speed < 2 and bus_announce_timer == 0:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 9")
                bus_announce_timer = 120

                bus_routes.play_stop_sound(current_bus_route, track, bus_route_sound, bus_door_sound)
                bus_next_stop_timer = 40
                current_stop = stops


def bus_announce_next_stop():
    global current_stop
    if bus_next_stop_sound:
        bus_routes.play_stop_sound(current_stop[1], track, bus_route_sound, bus_door_sound)
    if (current_stop[1] == "main_station" or current_stop[1] == "east_station" or current_stop[
        1] == "south_station" or current_stop[
        1] == "west_station" or current_stop[1] == "main_station_a" or current_stop[1] == "main_station_b" or
            current_stop[1] == "drifters_corner" or current_stop[1] == "simons_way"):
        current_stop = []


own_speed_mci = 0
own_z = 0
timers_timer = 0
own_previous_steering = 0
pscActive = False
acc_active = False
acc_paused = False
acc_set_speed = 0

pygame.joystick.init()
pygame.joystick.get_count()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
pygame.init()
own_throttle_input = 0
own_brake_input = 0

insim.send(pyinsim.ISP_MST,
           Msg=b"/axis %.1i steer" % STEER_AXIS)


def check_controller_input():
    global own_throttle_input, own_brake_input
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            if event.joy == num_joystick:
                if event.axis == controller_throttle:
                    throttle = event.value
                    own_throttle_input = (throttle - 1) / -2
                elif event.axis == controller_brake:
                    brake = event.value
                    own_brake_input = (brake - 1) / -2


acc_override = False
acc_cars_in_front = False


def check_adaptive_cruise_control():
    global acc_active, acc_paused, acc_set_speed, acc_override, acc_cars_in_front
    thread_controller = Thread(target=check_controller_input)
    thread_controller.start()
    acc_bra = 0
    cars_in_front = helpers.get_cars_in_front(own_heading, own_x, own_y, cars_relevant)
    if len(cars_in_front) == 0:
        acc_cars_in_front = False
        acc_bra = cruise_control.adaptive_cruise_control(own_speed, 0, 0, 0, False, acc_set_speed)
    else:
        acc_cars_in_front = True
        acc_bra = 1000
        for car in cars_in_front:
            rel = car[0].speed - own_speed

            acc_bra_new = cruise_control.adaptive_cruise_control(own_speed, rel, car[0].distance, car[0].dynamic, True,
                                                                 acc_set_speed)
            if acc_bra_new < acc_bra:
                acc_bra = acc_bra_new
    if collision_warning_intensity < 2 and acc_active:
        wheel_support.acc_control(acc_bra)
        if own_speed < 0.5 and not acc_paused:
            thread_press_q = Thread(target=handbrake)
            thread_press_q.start()
            notification("^3ACC Paused", 1)
            acc_paused = True
    if own_speed > 5 and acc_paused:
        acc_paused = False
    if acc_active and own_control_mode == 2:
        if own_throttle_input > 0.1 and not acc_override:
            acc_override = True
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i brake" % BRAKE_AXIS)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i throttle" % THROTTLE_AXIS)
        elif own_throttle_input < 0.1 and acc_override:
            acc_override = False
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i brake" % VJOY_AXIS)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i throttle" % VJOY_AXIS1)
        if own_brake_input > 0.1:
            acc_active = False
            del_button(81)
            del_button(82)
            del_button(83)
            notification("^3ACC Disengaged.", 2)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i brake" % BRAKE_AXIS)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i throttle" % THROTTLE_AXIS)

stopped = False


def get_car_data(insim, MCI):
    global own_x, own_y, own_heading, cars_previous_speed, temp_previous_speed, time_last_check, own_steering
    global park_assist_active, updated_cars, num_of_packages, num_of_packages_temp, shift_timer, shift_pressed
    global own_speed_mci, own_z, timers_timer, steering, own_previous_steering, pscActive, own_fuel_was
    global own_fuel_avg, own_fuel_moment, dist_travelled, own_range, own_fuel_start, own_fuel_start_capa, own_fuel_capa
    global stopped

    if time.time() - time_last_check > 0.1:
        time_last_check = time.time()
        cars_previous_speed = temp_previous_speed
        temp_previous_speed = []
        if stopped:
            if own_speed_mci > 5:
                stopped = False
                close_menu()
        else:
            if own_speed_mci < 5:
                stopped = True
                close_menu()

        for i, j in enumerate(cars_on_track):

            if j.player_id == own_player_id:
                own_speed_mci = j.speed
                own_x = j.x
                own_y = j.y
                own_z = j.z
                own_heading = j.heading
                own_steering = j.steer_forces

            temp_previous_speed.append((j.speed, j.player_id))

        [car.update_distance(own_x, own_y, own_z) for car in cars_on_track]
        [car.update_dynamic(speed[0] - car.speed) for speed in cars_previous_speed for car in cars_on_track if
         speed[1] == car.player_id and speed[0] - car.speed != 0.0]

        get_relevant_cars()

        timers()

        if settings.park_distance_control == "^2" and not chase:
            start_park_assistance()
        if (settings.park_distance_control == "^1" or chase) and park_assist_active:
            park_assist_active = False
            [del_button(i) for i in range(101, 110) if buttons_on_screen[i] == 1]

        if not acc_active and own_control_mode == 2 and PSC.calculateStabilityControl(own_speed, own_steering,
                                                                                      own_previous_steering) and settings.PSC == "^2" and (
                vehicle_model == b"FZ5" or vehicle_model == b'\xb6i\xbd' or vehicle_model == b'>\x8c\x88'):
            pscActive = True
            send_button(70, pyinsim.ISB_DARK, 114, 103, 13, 5, "^3PSC")
            wheel_support.brake_psc_rwd()
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i brake" % VJOY_AXIS)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i throttle" % VJOY_AXIS1)

        elif pscActive:
            pscActive = False
            if own_control_mode == 2:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/axis %.1i brake" % BRAKE_AXIS)
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/axis %.1i throttle" % THROTTLE_AXIS)
            del_button(70)
        own_previous_steering = own_steering

        if settings.forward_collision_warning == "^2" and not siren:
            collision_warning()
        if settings.blind_spot_warning == "^2":
            blind_spots()
        if settings.light_assist == "^2" or auto_indicators == "^2":
            light_assist()
        if settings.lane_assist == "^2" and roleplay != "cop":
            lane_assist()
        if collision_warning_intensity == 0 and settings.head_up_display == "^1":
            for i in range(6):
                del_button(10 + i)
        if roleplay == "cop" and settings.cop_aid_system == "^2":
            cop()
        other_assistances()
        if track != "none" and own_speed < 120:
            yield_assist()
        if helpers.get_shift_buttons():
            shift_pressed = True
        else:
            shift_pressed = False
        if settings.automatic_gearbox == "^2" and own_gearbox_mode == 2 and own_max_gears != -1 and auto_clutch == True and own_control_mode == 2:
            gear_to_be = gearbox.get_gear(accelerator_pressure, brake_pressure, own_gear, own_rpm, redline,
                                          own_max_gears, vehicle_model)
            if shift_timer == 0 or (own_rpm > own_max_rpm and shift_timer < 3):
                if not text_entry and not shift_pressed and own_gear > 1:
                    gearbox.shift(gear_to_be, own_gear, accelerator_pressure, own_steering)
                    shift_timer = 7
        elif settings.automatic_gearbox == "^2" and own_gearbox_mode == 2:
            if not auto_clutch:
                notification("^3Gearbox only with Auto-clutch", 4)
            elif own_control_mode != 2:
                notification("^3Gearbox only with Wheel", 4)
            else:
                notification("^3Gearbox not supported in this car", 4)
            settings.automatic_gearbox = change_setting(settings.automatic_gearbox)
        if track == b"SO" or track == b"KY" or track == b"FE" or track == b"BL" or track == b"AS" or track == b"WE":
            bus_route()

        dist_travelled = dist_travelled + (own_speed_mci / 3.6) / 5
        own_fuel_avg, own_fuel_moment, own_range = helpers.calculate_fuel(own_fuel_was, own_fuel, own_fuel_start_capa,
                                                                          own_fuel_capa, own_speed, dist_travelled)
        if own_fuel_was < own_fuel and engine_type != "electric":
            dist_travelled = 0
            own_fuel_start = time
            own_fuel_start_capa = own_fuel
            own_fuel_capa = helpers.get_fuel_capa(vehicle_model)

        own_fuel_was = own_fuel

        fuel_hud()
        acc_thread = Thread(target=check_adaptive_cruise_control)
        acc_thread.start()
    # DATA RECEIVING ---------------
    updated_this_packet = []
    [car.update_data(data.X, data.Y, data.Z, data.Heading, data.Direction, data.AngVel, data.Speed / 91.02, data.PLID)
     for data
     in MCI.Info for car in cars_on_track if car.player_id == data.PLID]
    [updated_this_packet.append(data.PLID) for data in MCI.Info]

    for data in MCI.Info:
        if data.PLID not in updated_cars:
            updated_cars.append(data.PLID)


siren = False
strobe = False
chase = False
job = False
many_cars_close = False
color_siren_button = "^4"

yield_sound = False


def yield_assist():
    global yield_polygons, yield_sound
    yield_note = False
    for poly in yield_polygons:
        if I_in_rectangle(poly[0]):
            for car in cars_relevant:
                if car_in_rectangle(poly[1], car[0].x, car[0].y) and car[0].speed > 20:
                    yield_note = True
                else:
                    try:
                        if car_in_rectangle(poly[2], car[0].x, car[0].y) and car[0].speed > 20:
                            yield_note = True
                    except:
                        pass

    if yield_note and own_speed > 60 and not yield_sound:
        notification("^1YIELD", 2)
        yield_sound = True
        play_yield_thread = Thread(target=helpers.yield_sound)
        play_yield_thread.start()
    elif yield_note and own_speed > 50:
        notification("^1YIELD", 2)
    elif yield_note:
        notification("^3YIELD", 2)
    if not yield_note and yield_sound:
        yield_sound = False


# TODO Error message when program not connected


def I_in_rectangle(polygon):
    point = Point(own_x / 65536, own_y / 65536)
    return polygon.contains(point)


def car_in_rectangle(polygon, x, y):
    point = Point(x / 65536, y / 65536)
    return polygon.contains(point)


def cop():
    hudheight = 115 + settings.offseth
    hudwidth = 90 + settings.offsetw
    if siren or strobe:
        change_strobe()
    if strobe:
        send_button(34, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, hudheight, hudwidth, 7, 4,
                    '{}Strobe'.format(color_siren_button))
    else:
        send_button(34, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, hudheight, hudwidth, 7, 4, 'Strobe')
    if siren:
        send_button(33, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, hudheight, hudwidth + 7, 6, 4,
                    '{}Siren'.format(color_siren_button))
    else:
        send_button(33, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, hudheight, hudwidth + 7, 6, 4, 'Siren')

    if chase and (siren or strobe):
        for car in cars_on_track:
            if car.player_id == player_id_to_track:
                x_chased_car = car.x
                y_chased_car = car.y
                speed_chased_car = car.speed
                tracker(x_chased_car, y_chased_car, speed_chased_car)
    else:
        del_button(61)
        del_button(62)


def tracker(x, y, sp):
    hudheight = 109 + settings.offseth
    hudwidth = 103 + settings.offsetw
    if sp < own_speed - 50:
        notification("^1SUSPECT SLOW", 1)

    angle_chased_car = helpers.calculate_angle(own_x, x, own_y, y, own_heading)

    if angle_chased_car > 329 or angle_chased_car < 31:
        str_arrow = "^2STRAIGHT"
    elif 30 < angle_chased_car < 150:
        str_arrow = "^3RIGHT -->"
    elif 149 < angle_chased_car < 210:
        str_arrow = "^1BEHIND"
    elif 209 < angle_chased_car < 330:
        str_arrow = "^3<-- LEFT"
    else:
        str_arrow = "error"
    send_button(61, pyinsim.ISB_DARK, hudheight + 5, hudwidth, 13, 5, str_arrow)
    if sp < own_speed - 25:
        send_button(62, pyinsim.ISB_DARK, hudheight, hudwidth, 13, 5, '^3{} kph'.format(round(sp)))
    else:
        send_button(62, pyinsim.ISB_DARK, hudheight, hudwidth, 13, 5, '{} kph'.format(round(sp)))


def change_siren():
    global siren, strobe
    if siren:
        if auto_siren == "^2":
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/siren off")
            siren = False
    else:
        if auto_siren == "^2":
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/siren slow")
            siren = True
            strobe = True


def change_strobe():
    global strobe_timer, color_siren_button
    if strobe_timer == 0:
        strobe_timer = 1
        if many_cars_close:
            if color_siren_button == "^4":
                color_siren_button = "^1"
            else:
                color_siren_button = "^4"

        if not many_cars_close:
            color_siren_button = "^4"
        x = random.choice([1, 2, 3])
        if not text_entry and not shift_pressed:
            if x == 1:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 3")
            elif x == 2:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 7")
            elif x == 3:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 8")


polygons_r = Polygon([(0, 0), (0, 1), (1, 0)])
polygons_l = Polygon([(0, 0), (0, 1), (1, 0)])

string_lane = ""

lane_detected = False


def lane_assist():
    global polygons_r, polygons_l, string_lane, car_in_control, previous_steering, lane_detected

    if polygons_r == Polygon([(0, 0), (0, 1), (1, 0)]) and (track == b"WE" or track == b"BL"):
        print("loading map data...")
        if track == b"WE":
            polygons_r, polygons_l = load_polygons("WE")
        elif track == b"BL":
            polygons_r, polygons_l = load_polygons("BL")

        print("map data loaded successfully")
    elif track == b"WE" or track == b"BL":
        reduced = False
        if settings.lane_dep_intensity == "normal":
            dep_set = 6
        elif settings.lane_dep_intensity == "early":
            dep_set = 5

        else:
            dep_set = 6
            reduced = True
        lane_d = False
        if own_speed > 30 and own_gear > 0 and -400 <= own_steering <= 400:
            lane_departure_r = False
            lane_departure_l = False
            if right_indicator_timer == 0:
                for p in polygons_r:
                    point = Point(own_x, own_y)
                    if p[6].contains(point):
                        lane_d = True

                        if not p[dep_set - 1].contains(point) and (
                                (reduced and ema_timer > 3) or not reduced):
                            right_lane_btn()
                            lane_departure_r = True
            if left_indicator_timer == 0:
                for p in polygons_l:
                    point = Point(own_x, own_y)
                    if p[6].contains(point):
                        lane_d = True
                        if not p[dep_set - 1].contains(point) and (
                                (reduced and ema_timer > 3) or not reduced):
                            left_lane_btn()
                            lane_departure_l = True
            lane_detected = lane_d
            if lane_detected and buttons_on_screen[47] == 0:
                if reduced:
                    if string_lane == '^2/ \\':
                        del_button(48)
                    string_lane = '^3/ \\'
                else:
                    if string_lane == '^3/ \\':
                        del_button(48)
                    string_lane = '^2/ \\'
                send_button(48, pyinsim.ISB_DARK, 119 + settings.offseth, 84 + settings.offsetw, 3, 3, string_lane)
            else:
                del_button(48)
            if not lane_departure_l and not lane_departure_r and buttons_on_screen[47] == 1:
                del_button(47)
            if not lane_departure_l and not lane_departure_r and buttons_on_screen[46] == 1:
                del_button(46)
        elif buttons_on_screen[47] == 1:
            del_button(47)
        elif buttons_on_screen[46] == 1:
            del_button(46)
        else:
            del_button(48)


def right_lane_btn():
    global lane_btn_timer, ema_timer
    if buttons_on_screen[46] == 0:
        del_button(48)
        send_button(46, pyinsim.ISB_DARK, 119 + settings.offseth, 120 + settings.offsetw, 3, 3, '^1|')
    else:
        del_button(46)
    lane_btn_timer += 30
    if 6 <= ema_timer < 14:
        ema_timer = 14
    if lane_btn_timer > 450:
        lane_btn_timer = 450
    if lane_btn_timer > 400:
        play_emawarning_thread = Thread(target=helpers.emawarningsound)
        play_emawarning_thread.start()
        notification("^1Stay in lane", 3)
        lane_btn_timer = 100


def left_lane_btn():
    global lane_btn_timer, ema_timer
    if buttons_on_screen[47] == 0:
        del_button(48)
        send_button(47, pyinsim.ISB_DARK, 119 + settings.offseth, 84 + settings.offsetw, 3, 3, '^1|')
    else:
        del_button(47)
    lane_btn_timer += 40
    if 6 <= ema_timer < 14:
        ema_timer = 14
    if lane_btn_timer > 450:
        lane_btn_timer = 450
    if lane_btn_timer > 400:
        play_emawarning_thread = Thread(target=helpers.emawarningsound)
        play_emawarning_thread.start()
        notification("^1Stay in lane", 3)
        lane_btn_timer = 100


def load_polygons(tra):
    polygons_right, polygons_left = load_lane_data.load(tra)

    return polygons_right, polygons_left


def blind_spots():
    blind_spot_r, blind_spot_l = check_blindspots(cars_relevant, own_x, own_y, own_heading, own_speed)
    if blind_spot_l:
        send_button(17, pyinsim.ISB_DARK, 110, 10, 5, 10, '^3!')
    else:
        del_button(17)
    if blind_spot_r:
        send_button(18, pyinsim.ISB_DARK, 110, 190, 5, 10, '^3!')
    else:
        del_button(18)


def get_distance(list_of_cars):
    return list_of_cars[0].distance


def get_relevant_cars():
    global cars_relevant, many_cars_close
    temp_list = []

    for i, j in enumerate(cars_on_track):
        if j.distance < 130 and not j.distance == 0:
            angle_temp = helpers.calculate_angle(own_x, j.x, own_y, j.y, own_heading)
            temp_list.append([j, angle_temp])
    temp_list = sorted(temp_list, key=get_distance)
    many_cars = False
    while len(temp_list) > 8:
        del temp_list[-1]
        if siren and not many_cars_close:
            if auto_siren == "^2":
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/siren fast")
        many_cars = True
    if siren and not many_cars and many_cars_close:
        if auto_siren == "^2":
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/siren slow")
    many_cars_close = many_cars

    cars_relevant = temp_list


timer_pdc_sound = 0
slow_timer = 0
timer_collision_warning = 0
timer_collision_warning_sound = 0
notification_timer = 0
notification_timer2 = 0
notification_timer3 = 0
send_timer = 0
timer_brake_light = 0
timer_turned_right = 0
timer_turned_left = 0
strobe_timer = 0
engine_start_timer = 0
timer_update_npl = 0
shift_timer = 0
ema_timer = 0
lane_btn_timer = 0
right_indicator_timer = 0
left_indicator_timer = 0
bus_announce_timer = 0
bus_next_stop_timer = 0


def decrement_timer(timer, decrement_value=1.0):
    return max(timer - decrement_value, 0)


def timers():
    global timer_pdc_sound, slow_timer, timer_collision_warning, timer_collision_warning_sound, notification_timer
    global send_timer, timer_brake_light, timer_turned_right, timer_turned_left, strobe_timer, engine_start_timer
    global timer_update_npl, shift_timer, notification_timer2, notification_timer3, notifications, ema_timer
    global lane_btn_timer, right_indicator_timer, left_indicator_timer, bus_announce_timer, bus_next_stop_timer
    global message_handling_error_count

    message_handling_error_count = decrement_timer(message_handling_error_count, 0.01)

    if bus_next_stop_timer > 0 and own_speed > 2:
        if bus_next_stop_timer == 1:
            bus_announce_next_stop()
        bus_next_stop_timer = decrement_timer(bus_next_stop_timer)

    bus_announce_timer = decrement_timer(bus_announce_timer) if own_speed > 2 else bus_announce_timer
    right_indicator_timer = decrement_timer(right_indicator_timer)
    left_indicator_timer = decrement_timer(left_indicator_timer)
    lane_btn_timer = decrement_timer(lane_btn_timer)

    if timer_update_npl == 0:
        timer_update_npl = 20
        insim.send(pyinsim.ISP_TINY, ReqI=255, SubT=pyinsim.TINY_NPL)
    timer_update_npl = decrement_timer(timer_update_npl)

    timer_pdc_sound = decrement_timer(timer_pdc_sound)
    slow_timer = decrement_timer(slow_timer)
    timer_collision_warning = decrement_timer(timer_collision_warning)
    timer_collision_warning_sound = decrement_timer(timer_collision_warning_sound)

    notification_timer = decrement_timer(notification_timer)
    if notification_timer == 1:
        notification_timer, notifications[0] = 0, ""
        del_button(16)

    notification_timer2 = decrement_timer(notification_timer2)
    if notification_timer2 == 1:
        notification_timer2, notifications[1] = 0, ""
        del_button(41)

    notification_timer3 = decrement_timer(notification_timer3)
    if notification_timer3 == 1:
        notification_timer3, notifications[2] = 0, ""
        del_button(42)

    send_timer = 0
    timer_brake_light = decrement_timer(timer_brake_light)
    timer_turned_left = decrement_timer(timer_turned_left)
    timer_turned_right = decrement_timer(timer_turned_right)
    strobe_timer = decrement_timer(strobe_timer)
    engine_start_timer = decrement_timer(engine_start_timer)
    shift_timer = decrement_timer(shift_timer)
    ema_timer = ema_timer + 1
    if ema_timer == 12 and settings.emergency_assist == "^2":
        play_emawarning_thread = Thread(target=helpers.emawarningsound)
        play_emawarning_thread.start()
    if ema_timer == 16 and settings.emergency_assist == "^2":
        play_emawarning2_thread = Thread(target=helpers.emawarningsound2)
        play_emawarning2_thread.start()


park_assist_active = False

#TODO PSC OFFSET BUTTON


def send_pdcbtns(angles, distances):
    global send_timer

    if send_timer == 0:
        send_timer = 1
        front = 110
        rear = 125
        sidel = 114
        sider = 122
        buttons_to_change = []
        color_to_change = []

        angle_ranges = {
            (345, 360): 1,
            (0, 15): 1,
            (15, 40): 2,
            (40, 140): 3,
            (140, 165): 4,
            (165, 195): 5,
            (195, 220): 6,
            (220, 320): 7,
            (320, 345): 8
        }

        buttons_to_change = []
        for angle in angles:
            for r, x in angle_ranges.items():
                if r[0] <= angle <= r[1]:
                    buttons_to_change.append(x)
                    break

        for dist in distances:
            if dist == 3:
                indend = 1
                color_pdc = "^2"
            elif dist == 2:
                indend = 2
                color_pdc = "^3"
            elif dist == 1:
                indend = 3
                color_pdc = "^3"
            elif dist == 0:
                indend = 4
                color_pdc = "^1"

            else:
                indend = 0
                color_pdc = "^2"
            color_this_sensor = color_pdc
            color_to_change.append((indend, color_this_sensor))

        if 8 not in buttons_to_change:
            send_button(108, pyinsim.ISB_LMB, front, 115, 20, 10, "^2-")
        if 1 not in buttons_to_change:
            send_button(101, pyinsim.ISB_LMB, front, 118, 20, 10, "^2-")
        if 2 not in buttons_to_change:
            send_button(102, pyinsim.ISB_LMB, front, 121, 20, 10, "^2-")
        if 4 not in buttons_to_change:
            send_button(104, pyinsim.ISB_LMB, rear, 121, 20, 10, "^2-")
        if 5 not in buttons_to_change:
            send_button(105, pyinsim.ISB_LMB, rear, 118, 20, 10, "^2-")
        if 6 not in buttons_to_change:
            send_button(106, pyinsim.ISB_LMB, rear, 115, 20, 10, "^2-")
        if 7 not in buttons_to_change:
            send_button(107, pyinsim.ISB_LMB, 117, sidel, 20, 10, "^2|")
        if 3 not in buttons_to_change:
            send_button(103, pyinsim.ISB_LMB, 117, sider, 20, 10, "^2|")
        for i, change in enumerate(buttons_to_change):
            move = color_to_change[i][0]
            color_this_sensor = color_to_change[i][1]

            if change == 8:
                send_button(108, pyinsim.ISB_LMB, front + move, 115, 20, 10, "{}-".format(color_this_sensor))

            if change == 1:
                send_button(101, pyinsim.ISB_LMB, front + move, 118, 20, 10, "{}-".format(color_this_sensor))

            if change == 2:
                send_button(102, pyinsim.ISB_LMB, front + move, 121, 20, 10, "{}-".format(color_this_sensor))

            if change == 4:
                send_button(104, pyinsim.ISB_LMB, rear - move, 121, 20, 10, "{}-".format(color_this_sensor))

            if change == 5:
                send_button(105, pyinsim.ISB_LMB, rear - move, 118, 20, 10, "{}-".format(color_this_sensor))

            if change == 6:
                send_button(106, pyinsim.ISB_LMB, rear - move, 115, 20, 10, "{}-".format(color_this_sensor))

            if change == 7:
                send_button(107, pyinsim.ISB_LMB, 117, sidel + move, 20, 10, "{}|".format(color_this_sensor))

            if change == 3:
                send_button(103, pyinsim.ISB_LMB, 117, sider - move, 20, 10, "{}|".format(color_this_sensor))



def get_sensor_pdc():
    sensors = park_assist.sensors(cars_relevant, own_x, own_y, own_heading, vehicle_model, rectangles_object)
    return sensors


emergency_light = False
emergency_stopped = False
turned_right = False
turned_left = False


def light_assist():
    global timer_brake_light, emergency_light, emergency_stopped, turned_left, turned_right, timer_turned_right
    global timer_turned_left

    def send_msg(msg):
        if not text_entry and not shift_pressed:
            insim.send(pyinsim.ISP_MST, Msg=msg)

    if settings.light_assist == "^2":
        if not any((own_light, emergency_light, siren, strobe, text_entry, shift_pressed)):
            send_msg(b"/press 3")

        if timer_brake_light == 0:
            timer_brake_light = 1
            if brake_light > 0.6 and own_speed > 15 and not any((siren, strobe)):
                emergency_light = True
                send_msg(b"/press 3")
            elif brake_light > 0.8 and own_speed < 15 and emergency_light:
                emergency_light = False
                emergency_stopped = True
                if roleplay == "civil":
                    send_msg(b"/press 9")
            elif own_speed > 15 and not emergency_light and emergency_stopped:
                if roleplay == "civil":
                    send_msg(b"/press 0")
                emergency_stopped = False
            elif own_speed > 15 and emergency_light:
                emergency_light = False

    if auto_indicators == "^2":
        if own_steering > 800:
            turned_left = True

        if own_steering < -800:
            turned_right = True

        if turned_right and own_steering < -80:
            timer_turned_right = 6

        if turned_left and own_steering > 80:
            timer_turned_left = 6

        conditions = (not text_entry, not shift_pressed, own_speed > 10)
        if all(conditions):
            if turned_left and indicators[0] == 1 and own_steering < 80:
                send_msg(b"/press 0")

            if turned_right and indicators[1] == 1 and own_steering > -80:
                send_msg(b"/press 0")

        if timer_turned_right == 0:
            turned_right = False
        if timer_turned_left == 0:
            turned_left = False


def start_park_assistance():
    global timer_pdc_sound
    global park_assist_active
    global slow_timer

    if game:
        if own_speed > 12:
            slow_timer = 10
        if slow_timer == 0 and (len(cars_relevant) > 0 or len(rectangles_object) > 0):

            sensors = get_sensor_pdc()
            angles = []
            distances = []
            for data in sensors:
                angles.append(data[1])
                distances.append(data[0])

            park_distance = min(distances)

            if park_distance < 4:
                park_assist_active = True
                send_button(109, pyinsim.ISB_DARK, 119 + settings.offseth, 116 + settings.offsetw, 4, 4, '^7PDC')
                send_pdcbtns(angles, distances)

                angle = 0
                for i, j in enumerate(distances):
                    if j == min(distances):
                        angle = angles[i]

                if timer_pdc_sound == 0:
                    if park_distance < 4 and own_speed > 0.1 and timer_pdc_sound == 0:
                        if park_distance == 3:
                            timer_pdc_sound = 4
                        elif park_distance == 2:
                            timer_pdc_sound = 3
                        elif park_distance == 1:
                            timer_pdc_sound = 2
                        elif park_distance == 0:
                            timer_pdc_sound = 1
                            notification("^1Stop!", 1)
                        try:
                            park_assist.makesound(park_distance, angle)
                        except:
                            print("It seems like your Windows version cant beep! (Park Assist)")

        else:
            [del_button(i) for i in range(101, 110) if buttons_on_screen[i] == 1]
            park_assist_active = False


new_warning = True
new_pre_warn = True


def collision_warning():
    global collision_warning_intensity, timer_collision_warning_sound, new_warning, current_control, new_pre_warn, acc_active
    if own_speed > 12 or collision_warning_intensity > 0:
        if acc_active:
            collision_warning_intensity = forward_collision_warning.check_warning_needed(cars_relevant, own_x, own_y,
                                                                                         own_heading, own_speed,
                                                                                         accelerator_pressure,
                                                                                         brake_pressure,
                                                                                         own_gear,
                                                                                         "late",
                                                                                         own_warn_multi,
                                                                                         own_vehicle_length,
                                                                                         own_speed_mci,
                                                                                         True)
        else:
            collision_warning_intensity = forward_collision_warning.check_warning_needed(cars_relevant, own_x, own_y,
                                                                                         own_heading, own_speed,
                                                                                         accelerator_pressure,
                                                                                         brake_pressure,
                                                                                         own_gear,
                                                                                         settings.collision_warning_distance,
                                                                                         own_warn_multi,
                                                                                         own_vehicle_length,
                                                                                         own_speed_mci,
                                                                                         False)
    if collision_warning_intensity == 1 and new_pre_warn and settings.head_up_display:
        new_pre_warn = False
        hud_image = Thread(target=change_image_prewarn)
        hud_image.start()

    if collision_warning_intensity <= 1:

        if collision_warning_intensity == 0 and (not new_warning or not new_pre_warn):
            new_pre_warn = True
            hud_image = Thread(target=change_image_del)
            hud_image.start()
        new_warning = True

    elif collision_warning_intensity > 1 and timer_collision_warning_sound == 0 and new_warning and settings.head_up_display:
        timer_collision_warning_sound = 10
        hud_image = Thread(target=change_image_warn)
        hud_image.start()
        new_warning = False
        helpers.collisionwarningsound(settings.collision_warning_sound)

    if collision_warning_intensity == 3 and settings.automatic_emergency_braking == "^2":
        if acc_active:
            acc_active = False
            del_button(81)
            del_button(82)
            del_button(83)
            notification("^3ACC Disengaged", 3)
        if own_control_mode == 2:
            brake()

        elif own_control_mode == 0:
            current_control = 1
            thread_br_mouse = Thread(target=brake_mouse)
            thread_br_mouse.start()

        elif own_control_mode == 1:
            current_control = 1
            thread_br_key = Thread(target=brake_keyboard)
            thread_br_key.start()

    elif current_control == 1:
        current_control = 0
        if own_control_mode == 2:
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i brake" % BRAKE_AXIS)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i throttle" % THROTTLE_AXIS)
            notification("^1Emergency Brake", 2)
        elif own_control_mode == 0:
            thread_rel_mouse = Thread(target=release_mouse)
            thread_rel_mouse.start()
            notification("^1Emergency Brake", 2)
        elif own_control_mode == 1:
            thread_rel_key = Thread(target=release_keyboard)
            thread_rel_key.start()
            notification("^1Emergency Brake", 2)


def brake_keyboard():
    pyautogui.keyDown(BRAKE_KEY)


def brake_mouse():
    pyautogui.mouseUp()
    pyautogui.mouseDown(button="right")


def release_keyboard():
    pyautogui.keyUp(BRAKE_KEY)


def release_mouse():
    pyautogui.mouseUp(button="right")


redline = 7000
own_vehicle_length = 0
own_max_gears = 6
own_max_rpm = -1
get_brake_dist = True
own_fuel_capa = -1
dist_travelled = 0


def head_up_display():
    global timer_collision_warning, vehicle_model_change, redline, own_vehicle_length, get_brake_dist, own_warn_multi
    global own_max_gears, own_max_rpm, own_fuel_capa, own_fuel_start, own_fuel_start_capa, dist_travelled
    if vehicle_model_change:
        print(vehicle_model)
        dist_travelled = 0
        own_fuel_start = time
        own_fuel_start_capa = own_fuel
        own_fuel_capa = helpers.get_fuel_capa(vehicle_model)
        vehicle_model_change = False
        own_warn_multi = 1.0
        get_brake_dist = False
        redline = helpers.get_vehicle_redline(vehicle_model)
        own_max_gears, own_max_rpm = helpers.get_max_gears(vehicle_model)
        own_vehicle_length, own_warn_multi = helpers.get_vehicle_length(vehicle_model)

    hudheight, hudwidth = 119 + settings.offseth, 90 + settings.offsetw
    btn_flags = pyinsim.ISB_DARK | pyinsim.ISB_CLICK
    speed_display = '^7%.1f MPH' % own_speed_mph if settings.unit == "imperial" else '^7%.1f KPH' % own_speed
    acc_speed_display = '^3%.1f MPH' % own_speed_mph if settings.unit == "imperial" else '^3%.1f KPH' % own_speed
    rpm_display = ('^7' if own_rpm < redline else '^1') + '%.1f RPM' % (own_rpm / 1000)
    send_button(11, pyinsim.ISB_DARK, hudheight, hudwidth + 13, 13, 8, rpm_display)
    if collision_warning_intensity == 0:
        if acc_active:
            acc_set_speed_display = '^2%.0f' % (acc_set_speed * 0.621 if settings.unit == "imperial" else acc_set_speed)
            send_button(81, pyinsim.ISB_DARK, hudheight + 3, hudwidth - 4, 4, 5, acc_set_speed_display)
            send_button(82, btn_flags, hudheight + 3, hudwidth - 10, 3, 5, '^7+')
            send_button(83, btn_flags, hudheight + 3, hudwidth - 7, 3, 5, '^7-')
            speed_display = acc_speed_display if acc_cars_in_front else '^2' + speed_display[2:]
        send_button(10, btn_flags, hudheight, hudwidth, 13, 8, speed_display)

    elif collision_warning_intensity > 0:
        warning_display = '^1<< ---', '^1--- >>'
        if collision_warning_intensity == 1 or timer_collision_warning == 1:
            send_button(10, pyinsim.ISB_DARK, hudheight, hudwidth, 13, 8, warning_display[0])
            send_button(11, pyinsim.ISB_DARK, hudheight, hudwidth + 13, 13, 8, warning_display[1])
        elif timer_collision_warning == 2:
            send_button(10, pyinsim.ISB_LIGHT, hudheight, hudwidth, 13, 8, warning_display[0])
            send_button(11, pyinsim.ISB_LIGHT, hudheight, hudwidth + 13, 13, 8, warning_display[1])
        if timer_collision_warning == 0:
            timer_collision_warning = 2

    if settings.head_up_display == "^2":
        gear_display = '^7'
        if own_gear > 1:
            gear_display += '' if own_gearbox_mode > 0 and not (
                    settings.automatic_gearbox == "^2" and own_gearbox_mode == 2) else 'D'
            gear_display += '%.i' % (own_gear - 1)
        elif own_gear == 1:
            gear_display += 'n'
        elif own_gear == 0:
            gear_display += 'r'
        send_button(12, pyinsim.ISB_DARK, hudheight + 4, hudwidth + 26, 4, 4, gear_display)


notifications = ["", "", ""]


def notification(notification_text, duration_in_sec):
    global notification_timer, notifications, notification_timer2, notification_timer3
    hudheight = 127 + settings.offseth
    hudwidth = 90 + settings.offsetw
    send_to_screen = True

    for notes in notifications:
        if notes == notification_text:
            send_to_screen = False

    if send_to_screen:
        if notifications[0] == "":
            notifications[0] = notification_text
            send_button(16, pyinsim.ISB_DARK, hudheight, hudwidth, 26, 6, notification_text)
            notification_timer = duration_in_sec * 5
        elif notifications[1] == "":
            notifications[1] = notification_text
            notification_timer2 = duration_in_sec * 5
            send_button(41, pyinsim.ISB_DARK, hudheight + 6, hudwidth, 26, 6, notification_text)
        elif notifications[2] == "":
            notifications[2] = notification_text
            notification_timer3 = duration_in_sec * 5
            send_button(42, pyinsim.ISB_DARK, hudheight + 13, hudwidth, 26, 6, notification_text)


def send_button(click_id, style, t, l, w, h, text):
    global buttons_on_screen

    valid_click_ids = [
        *range(10, 16), *range(19, 31), *range(33, 35), *range(41, 44),
        50, *range(52, 55), 61, 62, *range(100, 111), *range(68, 70),
        *range(71, 74), *range(76, 82), *range(86, 92)
    ]
    flags = [int(i) for i in str("{0:b}".format(style))]
    try:
        if own_control_mode == 0 and own_speed_mci > 5 and hide_mouse and flags[-4] == 1:
            style = style - 8
    except:
        pass

    if click_id in valid_click_ids or buttons_on_screen[click_id] == 0:
         buttons_on_screen[click_id] = 1
         insim.send(pyinsim.ISP_BTN,
                    ReqI=255,
                    ClickID=click_id,
                    BStyle=style | 3,
                    T=t,
                    L=l,
                    W=w,
                    H=h,
                    Text=text.encode())


def del_button(click_id):
    global buttons_on_screen
    if buttons_on_screen[click_id] == 1:
        insim.send(pyinsim.ISP_BFN,
                   ReqI=255,
                   ClickID=click_id
                   )
        buttons_on_screen[click_id] = 0


yield_polygons = []


def insim_state(insim, sta):
    global track, game, text_entry, start_outgauge_again, polygons_r, polygons_l, yield_polygons

    tracks = [b"WE", b"BL", b"AS", b"SO", b"FE", b"KY", b"AU", b"RO", b"LA"]

    for track_code in tracks:
        if track_code in sta.Track and track != track_code:
            polygons_r = Polygon([(0, 0), (0, 1), (1, 0)])
            polygons_l = Polygon([(0, 0), (0, 1), (1, 0)])
            track = track_code
            break

    yield_polygons = helpers.load_yield_polygons(track)
    flags = [int(i) for i in str("{0:b}".format(sta.Flags))]

    if len(flags) >= 15:
        game_active = flags[-1] == 1 and flags[-15] == 1

        if not game and game_active:
            game_insim()

        elif game and not game_active:
            menu_insim()
            start_outgauge_again = True

    elif game:
        menu_insim()

    text_entry = len(flags) >= 16 and flags[-16] == 1


def menu_insim():
    global insim, game, time_menu
    if game:
        game = False
        time_menu = time.time()
    insim.unbind(pyinsim.ISP_MCI, get_car_data)
    [del_button(i) for i in range(200)]
    send_button(31, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, 180, 0, 25, 5, "Waiting for you to hit the road.")


def game_insim():
    global insim, game, time_menu, outgauge, start_outgauge_again
    if time.time() - time_menu > 30 and not game:
        try:
            outgauge = pyinsim.outgauge('127.0.0.1', 30000, outgauge_packet, 30.0)
        except:
            print("Couldn't restart outgauge. Maybe it was still active.")
    game = True
    start_outgauge_again = False
    send_button(30, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, 100, 0, 7, 5, "Menu")
    del_button(31)
    del_button(32)
    insim.bind(pyinsim.ISP_MCI, get_car_data)
    insim.send(pyinsim.ISP_TINY, ReqI=255, SubT=pyinsim.TINY_NPL)


def open_menu():
    menu_top = 80
    del_button(30)
    if track == b"WE" or track == b"BL":
        color = [pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 30, 0, 20, 5,
                 "{}Lane Assist".format(settings.lane_assist)]
    else:
        color = [pyinsim.ISB_LIGHT, menu_top + 30, 0, 20, 5, "^0Lane Assist".format(settings.lane_assist)]
    if own_control_mode == 0:
        if hide_mouse:
            mouseStr = "^2Hide Mouse while Driving"

        else:
            mouseStr = "^1Hide Mouse while Driving"
        send_button(91, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top - 5, 35, 20, 5,
                    "{}".format(mouseStr))
    send_button(19, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top - 5, 0, 20, 5,
                "^7Menu")
    send_button(86, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top - 5, 20, 15, 5,
                "{}".format(settings.unit))
    send_button(20, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top, 0, 20, 5,
                "{}Head-Up Display".format(settings.head_up_display))
    send_button(21, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 5, 0, 20, 5,
                "{}Collision Warning".format(settings.forward_collision_warning))
    send_button(22, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 10, 0, 20, 5,
                "{}Blind-Spot Warning".format(settings.blind_spot_warning))
    send_button(23, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 15, 0, 20, 5,
                "{}Cross-Traffic Warn.".format(settings.cross_traffic_warning))
    send_button(24, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 20, 0, 20, 5,
                "{}Light Assist".format(settings.light_assist))
    send_button(68, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 20, 20, 20, 5,
                "{}Auto-Indicator Turnoff".format(auto_indicators))
    send_button(25, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 25, 0, 20, 5,
                "{}Emergency Assist".format(settings.emergency_assist))
    send_button(26, color[0], color[1], color[2], color[3], color[4], color[5])
    send_button(27, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 35, 0, 20, 5,
                "{}Parking Aid".format(settings.park_distance_control))
    send_button(28, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 40, 0, 20, 5,
                "{}Cop Aid System".format(settings.cop_aid_system))
    send_button(69, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 40, 20, 20, 5,
                "{}Auto-Siren".format(auto_siren))
    send_button(41, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 5, 20, 15, 5,
                "{}Automatic Brake".format(settings.automatic_emergency_braking))
    send_button(42, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 5, 35, 10, 5,
                "{}".format(settings.collision_warning_distance))
    send_button(43, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 45, 0, 20, 5,
                "{}Auto Gearshift".format(settings.automatic_gearbox))
    send_button(50, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 30, 20, 10, 5,
                "{}".format(settings.lane_dep_intensity))
    send_button(71, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 0, 20, 15, 5,
                "{}HUD-Images".format(settings.image_hud))
    send_button(87, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top, 35, 5, 5,
                "up".format(settings.unit))
    send_button(88, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top, 40, 5, 5,
                "down".format(settings.unit))
    send_button(89, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top, 45, 5, 5,
                "right".format(settings.unit))
    send_button(90, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top, 50, 5, 5,
                "left".format(settings.unit))
    if own_control_mode == 2:
        if vehicle_model == b"FZ5" or vehicle_model == b'\xb6i\xbd' or vehicle_model == b'>\x8c\x88':
            send_button(72, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 50, 0, 20, 5,
                        "{}Stability Control (beta)".format(settings.PSC))
        else:
            send_button(72, pyinsim.ISB_LIGHT, menu_top + 50, 0, 20, 5,
                        "^0This car has no ESP yet")
    else:
        send_button(72, pyinsim.ISB_LIGHT, menu_top + 50, 0, 20, 5,
                    "^0Stability Cont. (only wheel yet)")
    send_button(73, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 5, 45, 10, 5,
                "sound {}".format(settings.collision_warning_sound))

    send_button(51, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 55, 0, 20, 5,
                "Bus Menu")

    if get_brake_dist:
        send_button(66, pyinsim.ISB_LIGHT, menu_top + 60, 0, 20, 5,
                    "^0Re-Calibrating AEB...")
        send_button(67, pyinsim.ISB_LIGHT, menu_top + 60, 20, 35, 5,
                    "^0Brake hard from 70 kph 3x (straight)")
    else:
        send_button(66, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 60, 0, 20, 5,
                    "Recalibrate AEB")

    send_button(29, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 65, 0, 20, 5,
                "^1Close")


def close_menu():
    button_ids = [
        41, 42, 43, 50, 51, 66, 67, 68, 69, 71, 72, 73, 86, 87, 88, 89, 90, 91
    ]

    for i in range(19, 30):
        del_button(i)

    for button_id in button_ids:
        del_button(button_id)
    if own_speed_mci > 5 and hide_mouse and own_control_mode == 0:
        del_button(30)
        send_button(92, pyinsim.ISB_DARK, 100, 0, 7, 5, "Menu")
    else:
        del_button(92)
        send_button(30, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, 100, 0, 7, 5, "Menu")
    get_settings.write_settings(settings)


def change_setting(sett):
    if sett == "^1":
        sett = "^2"
    else:
        sett = "^1"

    return sett


bus_next_stop_sound = True
bus_route_sound = True
bus_door_sound = True


# def on_click_preview_gpt(insim, btc):
#     global settings, strobe, siren, collision_warning_not_cop
#     global current_bus_route, current_stop, bus_next_stop_sound, bus_route_sound, bus_door_sound, measure_param
#     global own_warn_multi, get_brake_dist, auto_indicators, auto_siren, acc_active, acc_set_speed
#
#     def open_menu_case():
#         open_menu()
#
#     def offseth_decrease():
#         settings.offseth -= 1
#
#     def offseth_increase():
#         settings.offseth += 1
#
#     def offsetw_increase():
#         settings.offsetw += 1
#
#     def offsetw_decrease():
#         settings.offsetw -= 1
#
#     def toggle_unit():
#         settings.unit = "imperial" if settings.unit == "metric" else "metric"
#         open_menu()
#
#     def acc_set_speed_increase():
#         nonlocal acc_set_speed
#         acc_set_speed = min(acc_set_speed + 5 - (acc_set_speed % 5), 130)
#
#     def acc_set_speed_decrease():
#         nonlocal acc_set_speed
#         acc_set_speed = max(acc_set_speed - 5 - (acc_set_speed % 5), 30)
#
#     click_actions = {
#         30: open_menu_case,
#         87: offseth_decrease,
#         88: offseth_increase,
#         89: offsetw_increase,
#         90: offsetw_decrease,
#         86: toggle_unit,
#         82: acc_set_speed_increase,
#         83: acc_set_speed_decrease,
#     }
#
#     action = click_actions.get(btc.ClickID)
#     if action:
#         action()


def on_click(insim, btc):
    global settings, strobe, siren, collision_warning_not_cop
    global current_bus_route, current_stop, bus_next_stop_sound, bus_route_sound, bus_door_sound, measure_param
    global own_warn_multi, get_brake_dist, auto_indicators, auto_siren, acc_active, acc_set_speed, hide_mouse

    if btc.ClickID == 30:
        open_menu()
    elif btc.ClickID == 87:
        settings.offseth = settings.offseth - 1
    elif btc.ClickID == 88:
        settings.offseth = settings.offseth + 1
    elif btc.ClickID == 89:
        settings.offsetw = settings.offsetw + 1
    elif btc.ClickID == 90:
        settings.offsetw = settings.offsetw - 1
    elif btc.ClickID == 91:
        hide_mouse = not hide_mouse
        if hide_mouse:
            notification("^3Buttons avail. when stationary", 5)
        open_menu()
    elif btc.ClickID == 86:
        if settings.unit == "metric":
            settings.unit = "imperial"
        else:
            settings.unit = "metric"

        open_menu()
    elif btc.ClickID == 82:
        acc_set_speed = acc_set_speed + 5 - (acc_set_speed % 5)
        if acc_set_speed > 130:
            acc_set_speed = 130
    elif btc.ClickID == 83:
        acc_set_speed = acc_set_speed - 5 - (acc_set_speed % 5)
        if acc_set_speed < 30:
            acc_set_speed = 30
    elif btc.ClickID == 10:

        if controller_throttle != -1 and controller_brake != -1 and num_joystick != -1:
            if (29 < own_speed < 131 or (
                    own_speed < 131 and acc_cars_in_front) or acc_active) and own_control_mode == 2:
                if not acc_active:
                    if own_speed < 30:
                        acc_set_speed = 30
                    else:
                        acc_set_speed = own_speed
                acc_active = not acc_active
            else:
                notification("ACC not available!", 3)
        else:
            notification("ACC not set up!", 3)
        if not acc_active:
            del_button(81)
            del_button(82)
            del_button(83)
        if acc_active and own_control_mode == 2:

            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i brake" % VJOY_AXIS)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i throttle" % VJOY_AXIS1)
        elif own_control_mode == 2:
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i brake" % BRAKE_AXIS)
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/axis %.1i throttle" % THROTTLE_AXIS)
    elif btc.ClickID == 76:
        if settings.bc == "average":
            settings.bc = "moment"
        elif settings.bc == "moment":
            settings.bc = "range"
        elif settings.bc == "range":
            settings.bc = "off"
        elif settings.bc == "off":
            settings.bc = "average"
        get_settings.write_settings(settings)
    elif btc.ClickID == 68:
        auto_indicators = change_setting(auto_indicators)
    elif btc.ClickID == 69:
        auto_siren = change_setting(auto_siren)
    elif btc.ClickID == 71:
        settings.image_hud = change_setting(settings.image_hud)
    elif btc.ClickID == 72:
        settings.PSC = change_setting(settings.PSC)
    elif btc.ClickID == 73:

        if settings.collision_warning_sound < 5:
            settings.collision_warning_sound = settings.collision_warning_sound + 1

        else:
            settings.collision_warning_sound = 1
        helpers.playsound(settings.collision_warning_sound)
    elif btc.ClickID == 66:
        get_brake_dist = True
        own_warn_multi = 1.0
        measure_param = [0, 0, 0, 0]
        del_button(66)
        del_button(67)
        open_menu()
    elif btc.ClickID == 29 or btc.ClickID == 19:
        close_menu()
    elif btc.ClickID == 20:
        settings.head_up_display = change_setting(settings.head_up_display)
    elif btc.ClickID == 21:
        settings.forward_collision_warning = change_setting(settings.forward_collision_warning)
        if roleplay != "cop":
            collision_warning_not_cop = settings.forward_collision_warning
    elif btc.ClickID == 22:
        settings.blind_spot_warning = change_setting(settings.blind_spot_warning)
    elif btc.ClickID == 23:
        settings.cross_traffic_warning = change_setting(settings.cross_traffic_warning)
    elif btc.ClickID == 24:
        settings.light_assist = change_setting(settings.light_assist)
    elif btc.ClickID == 25:
        settings.emergency_assist = change_setting(settings.emergency_assist)
    elif btc.ClickID == 26:
        settings.lane_assist = change_setting(settings.lane_assist)
        if settings.lane_assist == "^1":
            del_button(46)
            del_button(47)
            del_button(48)
    elif btc.ClickID == 27:
        settings.park_distance_control = change_setting(settings.park_distance_control)
    elif btc.ClickID == 41:
        settings.automatic_emergency_braking = change_setting(settings.automatic_emergency_braking)
    elif btc.ClickID == 42:
        if settings.collision_warning_distance == "early":
            settings.collision_warning_distance = "medium"
        elif settings.collision_warning_distance == "medium":
            settings.collision_warning_distance = "late"
        else:
            settings.collision_warning_distance = "early"
    elif btc.ClickID == 50:
        if settings.lane_dep_intensity == "early":
            settings.lane_dep_intensity = "normal"
        elif settings.lane_dep_intensity == "normal":
            settings.lane_dep_intensity = "reduced"
        else:
            settings.lane_dep_intensity = "early"
    elif btc.ClickID == 43:
        settings.automatic_gearbox = change_setting(settings.automatic_gearbox)
    elif btc.ClickID == 28:
        settings.cop_aid_system = change_setting(settings.cop_aid_system)
        del_button(33)
        del_button(34)
        if siren or strobe:
            strobe = False
    elif btc.ClickID == 33:
        change_siren()
    elif btc.ClickID == 34:
        strobe = not strobe
        if not strobe and not text_entry and not shift_pressed:
            insim.send(pyinsim.ISP_MST,
                       Msg=b"/press 0")
    if 20 <= btc.ClickID <= 28 or 41 <= btc.ClickID <= 43 or btc.ClickID == 50 or 68 <= btc.ClickID <= 69 or 71 <= btc.ClickID <= 73:
        open_menu()

    if btc.ClickID == 51:
        if track == b"SO" or track == b"KY" or track == b"FE" or track == b"BL" or track == b"AS" or track == b"WE":
            load_bus_menu()
        else:
            notification("^1No Routes on this Map", 3)

    if btc.ClickID == 52:
        bus_next_stop_sound = not bus_next_stop_sound
        load_bus_menu()

    elif btc.ClickID == 53:
        bus_route_sound = not bus_route_sound
        load_bus_menu()

    elif btc.ClickID == 54:
        bus_door_sound = not bus_door_sound
        load_bus_menu()

    elif btc.ClickID == 59:
        x = 52
        del_button(19)
        for i in range(8):
            del_button(x + i)
        close_menu()


player_id_to_track = 0
person_chased = ""
message_handling_error_count = 0


def load_bus_menu():
    menu_top = 80
    close_menu()
    del_button(30)

    send_button(51, pyinsim.ISB_DARK, menu_top - 5, 0, 20, 5, "Bus Settings")
    if bus_next_stop_sound:
        send_button(52, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top, 0, 20, 5, "^2Next Stop sound")
    else:
        send_button(52, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top, 0, 20, 5, "^1Next Stop sound")

    if bus_route_sound:
        send_button(53, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 5, 0, 20, 5, "^2Current Route sound")
    else:
        send_button(53, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 5, 0, 20, 5, "^1Current Route sound")

    if bus_door_sound:
        send_button(54, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 10, 0, 20, 5, "^2Door sound")
    else:
        send_button(54, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 10, 0, 20, 5, "^1Door sound")

    send_button(59, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, menu_top + 15, 0, 20, 5, "^1Close")


string_bust = b""
string_bust2 = b""


def message_handling(insim, mso):
    global siren, strobe, chase, player_id_to_track, person_chased, message_handling_error_count, current_bus_route
    global string_bust, string_bust2

    if mso.Msg == b'PACT Driving Assistant Active':
        print("Connection to LFS sucessful!")
    try:
        own_player_name_str = str(own_player_name)
        own_player_name_str = own_player_name_str.replace("b'", "")
        own_player_name_str = own_player_name_str.replace("'", "")
        print(mso.Msg)
        if message_handling_error_count < 8:
            stop_str = "Stop complete.".encode()
            route1_str = (own_player_name_str + "none_route").encode()
            route2_str = (own_player_name_str + "none_route").encode()
            route3_str = (own_player_name_str + "none_route").encode()
            route4_str = (own_player_name_str + "none_route").encode()
            route5_str = (own_player_name_str + "none_route").encode()
            route6_str = (own_player_name_str + "none_route").encode()
            route7_str = (own_player_name_str + "none_route").encode()
            route8_str = (own_player_name_str + "none_route").encode()
            if track == b"BL":
                route1_str = (own_player_name_str + "^L started Red Route").encode()
                route2_str = (own_player_name_str + "^L started Blue Route").encode()
                route3_str = (own_player_name_str + "^L started Yellow Route").encode()
                route4_str = (own_player_name_str + "^L started Green Route").encode()

            elif track == b"SO":
                route1_str = (own_player_name_str + "^L started Southern Route Short").encode()
                route2_str = (own_player_name_str + "^L started Southern Route Short Rev").encode()
                route3_str = (own_player_name_str + "^L started Southern Route Long").encode()
                route4_str = (own_player_name_str + "^L started Southern Route Long Rev").encode()
                route5_str = (own_player_name_str + "^L started Castle Hill Route").encode()
                route6_str = (own_player_name_str + "^L started Castle Hill Route Rev").encode()
                route7_str = (own_player_name_str + "^L started Le Grand Tour").encode()

            elif track == b"FE":
                route1_str = (own_player_name_str + "^L started Eastern Short Route").encode()
                route2_str = (own_player_name_str + "^L started Eastern Short Route Rev").encode()
                route3_str = (own_player_name_str + "^L started Eastern Route").encode()
                route4_str = (own_player_name_str + "^L started Eastern Route Rev").encode()
                route5_str = (own_player_name_str + "^L started The Grand Tour").encode()
                route6_str = (own_player_name_str + "^L started The Grand Tour Rev").encode()
                route7_str = (own_player_name_str + "^L started Transit West").encode()

            elif track == b"AS":
                route1_str = (own_player_name_str + "^L started Route 1").encode()
                route2_str = (own_player_name_str + "^L started Route 1 Rev").encode()
                route3_str = (own_player_name_str + "^L started Route 2").encode()
                route4_str = (own_player_name_str + "^L started Route 2 Rev").encode()
                route5_str = (own_player_name_str + "^L started Route 3").encode()
                route6_str = (own_player_name_str + "^L started Route 3 Rev").encode()
                route7_str = (own_player_name_str + "^L started Route 4").encode()
                route8_str = (own_player_name_str + "^L started Route 4 Rev").encode()

            elif track == b"KY":
                route1_str = (own_player_name_str + "^L started Route 1 Long").encode()
                route2_str = (own_player_name_str + "^L started Route 1 Rev").encode()
                route3_str = (own_player_name_str + "^L started Route 1").encode()
                route4_str = (own_player_name_str + "^L started Route 2").encode()

            elif track == b"WE":
                route1_str = (own_player_name_str + "^L started Yellow Route").encode()
                route2_str = (own_player_name_str + "^L started Green Route").encode()
                route3_str = (own_player_name_str + "^L started Red Route").encode()
                route4_str = (own_player_name_str + "^L started Blue Route").encode()

            route_message = mso.Msg
            route_message = str(route_message)
            route_message = route_message.encode()
            route_message = route_message.replace(b"^1", b"")
            route_message = route_message.replace(b"^2", b"")
            route_message = route_message.replace(b"^3", b"")
            route_message = route_message.replace(b"^4", b"")
            route_message = route_message.replace(b"^5", b"")
            route_message = route_message.replace(b"^6", b"")
            route_message = route_message.replace(b"^7", b"")
            route_message = route_message.replace(b"^8", b"")
            route_message = route_message.replace(b"^9", b"")
            route_message = route_message.replace(b"^0", b"")

            if route2_str in route_message:
                current_bus_route = "route_2"
            elif route1_str in route_message:
                current_bus_route = "route_1"
            elif route4_str in route_message:
                current_bus_route = "route_4"
            elif route3_str in route_message:
                current_bus_route = "route_3"
            elif route6_str in route_message:
                current_bus_route = "route_6"
            elif route5_str in route_message:
                current_bus_route = "route_5"
            elif route8_str in route_message:
                current_bus_route = "route_8"
            elif route7_str in route_message:
                current_bus_route = "route_7"

            if stop_str in mso.Msg:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 0")
            if settings.cop_aid_system == "^2":
                string_chase = (own_player_name_str + "^L chasing:").encode()
                string_join = (own_player_name_str + "^L joined on").encode()
                string_lost = (own_player_name_str + "^L lost contact with suspect.").encode()
                string_left = (own_player_name_str + "^L left the chase.").encode()
                string_backup = (own_player_name_str + "^L is calling for backup.").encode()

                if string_chase in mso.Msg or string_join in mso.Msg:
                    if not siren:
                        change_siren()

                    chase = True
                    person_chased = mso.Msg
                    if string_chase in mso.Msg:
                        person_chased = person_chased.split(b"chasing:")
                    else:
                        person_chased = person_chased.split(b"joined on")
                    person_chased = person_chased[1]
                    person_chased = person_chased[1:]

                    for key in players:

                        name = players[key].PName
                        name = name.replace(b"^1", b"")
                        name = name.replace(b"^2", b"")
                        name = name.replace(b"^3", b"")
                        name = name.replace(b"^4", b"")
                        name = name.replace(b"^5", b"")
                        name = name.replace(b"^6", b"")
                        name = name.replace(b"^7", b"")
                        name = name.replace(b"^8", b"")
                        name = name.replace(b"^0", b"")
                        if person_chased == name:
                            player_id_to_track = players[key].PLID
                            person_chased = str(name)
                            person_chased = person_chased.replace("b'", "")
                            person_chased = person_chased.replace("'", "")

                            string_bust = (person_chased + " has been busted ^Lby").encode()
                            string_bust2 = (person_chased + " has been auto-busted").encode()
                elif string_lost in mso.Msg or string_left in mso.Msg or ((
                                                                                  string_bust in mso.Msg or string_bust2 in mso.Msg) and string_bust != b"" and string_bust2 != b""):

                    if siren:
                        change_siren()

                    strobe = False
                    if not strobe and not text_entry and not shift_pressed and roleplay == "cop":
                        insim.send(pyinsim.ISP_MST,
                                   Msg=b"/press 0")
                    chase = False

    except:
        print("Error in message handling. Usually not a problem, maybe unknown character!")
        message_handling_error_count = message_handling_error_count + 1


def start_eng():
    pyautogui.keyDown(IGNITION_KEY)
    pyautogui.keyUp(IGNITION_KEY)


def handbrake():
    pyautogui.keyDown(HANDBRAKE_KEY)
    pyautogui.keyUp(HANDBRAKE_KEY)


times = 0

previous_acceleration = 0
previous_brake = 0
previous_steer = 0
ema_active = False
active_lane_prep = False


def other_assistances():
    global engine_start_timer, times, ema_timer, previous_steer, previous_brake, previous_acceleration, ema_active, current_control
    global active_lane, active_lane_prep

    if own_rpm < 150 and own_battery_light:
        if not text_entry and not shift_pressed and engine_type != "electric":
            thread_press_i = Thread(target=start_eng)
            thread_press_i.start()
            notification("^3Anti-Stall", 2)

    elif accelerator_pressure > 0.2 and own_rpm < 150 and engine_start_timer == 0:
        engine_start_timer = 2
        if not text_entry and not shift_pressed and engine_type != "electric":
            thread_press_i = Thread(target=start_eng)
            thread_press_i.start()
            notification("^3Auto-Engine-Start", 2)
    if settings.emergency_assist == "^2":
        movement_of_car = 10
        if ema_timer > 14:
            movement_of_car = ema_timer * 3
            if movement_of_car > 80:
                movement_of_car = 80

        if own_speed > 10 and not ema_active and ((
                                                          accelerator_pressure != previous_acceleration or (
                                                          brake_light != previous_brake and ema_timer < 15) or not previous_steer - movement_of_car <= own_steering <= previous_steer + movement_of_car) or accelerator_pressure > 0.25 or brake_light > 0.75):
            previous_steer = own_steering
            previous_brake = brake_light
            previous_acceleration = accelerator_pressure
            ema_timer = 0

        elif own_speed < 11 and not ema_active:
            ema_timer = 0
        previous_steer = own_steering
        if ema_active and own_speed < 1:
            ema_timer = 0
            if not text_entry and not shift_pressed:
                thread_press_q = Thread(target=handbrake)
                thread_press_q.start()
                notification("^3Auto-Hold", 1)

        acc_move = 0.2

        if ema_active and (
                not previous_acceleration - acc_move <= accelerator_pressure <= previous_acceleration + acc_move or not previous_steer - movement_of_car <= own_steering <= previous_steer + movement_of_car):
            previous_steer = own_steering
            previous_brake = brake_pressure
            previous_acceleration = accelerator_pressure
            ema_timer = 0

        if ema_active:
            previous_acceleration = accelerator_pressure

        if 8 < ema_timer <= 12 and not acc_active:
            notification("Pay Attention", 1)

        elif 12 <= ema_timer <= 15 and not acc_active:
            notification("^1Pay Attention", 2)

        elif ema_timer > 15 and not acc_active:
            ema_active = True

            notification("^1Stopping Car", 2)
            if not text_entry and not shift_pressed:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 9")
            if ema_timer == 20 or (ema_timer > 20 and ema_timer % 15 == 0):
                play_emawarning_thread = Thread(target=helpers.emawarningsound2)
                play_emawarning_thread.start()

            if current_control == 0:
                current_control = 1

                if own_control_mode == 2:
                    insim.send(pyinsim.ISP_MST,
                               Msg=b"/axis %.1i brake" % VJOY_AXIS)
                    if lane_detected and 85 > own_speed > 15:
                        active_lane = True
                    elif not active_lane:
                        wheel_support.brake_slow()

                elif own_control_mode == 0:
                    thread_rel_mouse = Thread(target=brake_mouse)
                    thread_rel_mouse.start()

                elif own_control_mode == 1:
                    thread_rel_key = Thread(target=brake_keyboard)
                    thread_rel_key.start()
        if ema_timer < 15 and active_lane:
            active_lane = False

        if ema_timer > 10:
            active_lane_prep = True
        if ema_active and ema_timer <= 15 and own_speed > 5:
            if not text_entry and not shift_pressed:
                insim.send(pyinsim.ISP_MST,
                           Msg=b"/press 0")
        else:
            active_lane_prep = False
        if ema_active and ema_timer <= 15:
            ema_active = False

            if current_control == 1:
                current_control = 0

                if own_control_mode == 2:
                    insim.send(pyinsim.ISP_MST,
                               Msg=b"/axis %.1i brake" % BRAKE_AXIS)

                elif own_control_mode == 0:
                    thread_rel_mouse = Thread(target=release_mouse)
                    thread_rel_mouse.start()

                elif own_control_mode == 1:
                    thread_rel_key = Thread(target=release_keyboard)
                    thread_rel_key.start()

    if brake_pressure > 0.2 and accelerator_pressure < 0.1 and own_speed < 0.01 and not own_handbrake:
        if not text_entry and not shift_pressed:
            thread_press_q = Thread(target=handbrake)
            thread_press_q.start()
            notification("^3Auto-Hold", 1)


send_button(31, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, 175, 0, 25, 5, "Waiting for you to hit the road.")
send_button(32, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, 180, 0, 25, 5, "^1Press 'V' if you're already on track.")

current_control = 0  # 0 = Player, 1 = Python


def brake():
    global current_control
    if current_control == 0:
        current_control = 1
        insim.send(pyinsim.ISP_MST,
                   Msg=b"/axis %.1i brake" % VJOY_AXIS)
        insim.send(pyinsim.ISP_MST,
                   Msg=b"/axis %.1i throttle" % VJOY_AXIS1)

    wheel_support.brake()


def fuel_hud():
    r = own_range - 1
    r2 = round(r / 10) * 10

    if 1.9 < r < 2.0:
        notification("^1< 2km range!", 5)
    elif 9.9 < r < 10.0:
        notification("^3< 10km range!", 5)
    elif 49.9 < r < 50.0:
        notification("^7< 50km range!", 5)

    h = 113 + settings.offseth if roleplay == "civil" else 109 + settings.offseth
    hudwidth = 90 + settings.offsetw

    button_label = None
    if settings.bc == "moment":
        button_label = '^7%.1f L/100km' % own_fuel_moment if engine_type != "electric" else '^7%.1f kwh/100km' % own_fuel_moment
    elif settings.bc == "average":
        button_label = '^7%.1f L/100km' % own_fuel_avg if engine_type != "electric" else '^7%.1f kwh/100km' % own_fuel_avg
    elif settings.bc == "range":
        if r > 50:
            button_label = '^7%.0i km' % r2
        elif r > 10:
            button_label = '^7%.0f km' % r
        elif r > 5:
            button_label = '^3%.0f km' % r
        elif r > 2:
            button_label = '^1%.1f km' % r
        elif r > 1:
            button_label = '^1%.2f km' % r
        elif r > 0.5:
            button_label = '^1%.2f km' % r
        elif 0 <= r <= 0.5:
            button_label = '^1--- km'
        else:
            button_label = '^7calculating'
    elif settings.bc == "off":
        send_button(76, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, h + 6, hudwidth - 3, 3, 3, 'BC')

    if button_label:
        send_button(76, pyinsim.ISB_DARK | pyinsim.ISB_CLICK, h, hudwidth, 13, 6, button_label)


rectangles_object = []


def object_detection(insim, axm):
    global rectangles_object
    try:
        rectangles_object_temp = helpers.create_rectangles_for_objects(axm.Info, own_x, own_y, own_heading)
        for obj in rectangles_object_temp:
            rectangles_object.append(obj)

    except:
        print("Error while loading layout. No PDC available for layout objects.")


insim.bind(pyinsim.ISP_MSO, message_handling)
insim.bind(pyinsim.ISP_STA, insim_state)
insim.bind(pyinsim.ISP_NPL, new_player)
insim.bind(pyinsim.ISP_PLL, player_left)
insim.bind(pyinsim.ISP_PLP, player_pits)
insim.bind(pyinsim.ISP_BTC, on_click)
insim.bind(pyinsim.ISP_AXM, object_detection)

pyinsim.run()
