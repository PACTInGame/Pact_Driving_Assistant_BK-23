import math
import time
import winsound
from threading import Thread


def stop_dist_WE(route, own_x, own_y):
    stops = []
    return_array = []

    if route == "route_1":  # Yellow
        stops.append(["south_station", "weston_zoo", (733.44, -748.50)])
        stops.append(["weston_zoo", "dustin", (333.44, -235.13)])
        stops.append(["dustin", "paddock", (73.81, 205.25)])
        stops.append(["paddock", "gas_station", (-124.44, 239.94)])
        stops.append(["gas_station", "roundabout", (-134.00, 571.25)])
        stops.append(["roundabout", "vip_tribune", (-306.63, 766.56)])
        stops.append(["vip_tribune", "west_grill", (-298.75, 355.88)])
        stops.append(["west_grill", "traffic_police", (-423.56, -78.88)])
        stops.append(["traffic_police", "main_station", (-707.88, -184.56)])

    if route == "route_2":  # Green
        stops.append(["south_station", "weston_observatory", (733.44, -748.50)])
        stops.append(["weston_observatory", "infield", (175.88, -545.50)])
        stops.append(["infield", "speedway", (-239.25, -409.75)])
        stops.append(["speedway", "green_mountain", (-342.69, -670.94)])
        stops.append(["green_mountain", "vipers_valley", (84.44, -709.56)])
        stops.append(["vipers_valley", "southampton_road", (247.19, -992.06)])
        stops.append(["southampton_road", "south_station", (634.88, -1133.19)])

    if route == "route_3":  # Red
        stops.append(["main_station", "traffic_police", (-336.25, -287.31)])
        stops.append(["traffic_police", "obsession_street", (-768.13, -203.06)])
        stops.append(["obsession_street", "west_grill", (-439.19, -196.38)])
        stops.append(["west_grill", "karting_international", (-423.56, -78.88)])
        stops.append(["karting_international", "logistics_south", (-751.81, 126.63)])
        stops.append(["logistics_south", "logistics_north", (-504.31, 774.31)])
        stops.append(["logistics_north", "schumacher_tribune", (-375.56, 879.44)])
        stops.append(["schumacher_tribune", "dustin", (16.56, 918.56)])
        stops.append(["dustin", "medical_centre", (73.81, 205.25)])
        stops.append(["medical_centre", "main_station", (-144.63, -151.00)])

    if route == "route_4":  # Blue
        stops.append(["main_station", "traffic_police", (-333.44, -274.38)])
        stops.append(["traffic_police", "north_grandstand_west", (-768.13, -203.06)])
        stops.append(["north_grandstand_west", "north_grandstand_south", (-750.56, -451.44)])
        stops.append(["north_grandstand_south", "southampton_road", (-272.19, -1030.44)])
        stops.append(["southampton_road", "south_station", (634.88, -1133.19)])

    for i, stop in enumerate(stops):
        distance = dist(stop[2], (own_x / 65536, own_y / 65536))
        arr_app = [stop[0], stop[1], distance]
        return_array.append(arr_app)
    return return_array


def stop_dist_AS(route, own_x, own_y):
    stops = []
    return_array = []

    if route == "route_1":  # 1
        stops.append(["drifters_corner", "main_street_south", (-1006.31, -1050.69)])
        stops.append(["main_street_south", "main_street_north", (-461.81, -651.06)])
        stops.append(["main_street_north", "snake_pass", (-338.94, 37.13)])
        stops.append(["snake_pass", "the_bridge", (-308.81, 524.81)])
        stops.append(["the_bridge", "corkscrew", (-103.81, 657.25)])
        stops.append(["corkscrew", "main_station", (104.44, 100.06)])

    if route == "route_2":  #1 rev
        stops.append(["main_station", "corkscrew", (-129.88, -267.19)])
        stops.append(["corkscrew", "the_bridge", (104.44, 100.06)])
        stops.append(["the_bridge", "snake_pass", (-103.81, 657.25)])
        stops.append(["snake_pass", "main_street_north", (-308.81, 524.81)])
        stops.append(["main_street_north", "main_street_south", (-357.63, 34.56)])
        stops.append(["main_street_south", "drifters_corner", (-461.81, -651.06)])

    if route == "route_3":  # 2
        stops.append(["drifters_corner", "hillside_road", (-1006.31, -1050.69)])
        stops.append(["hillside_road", "main_pass", (-414.63, -989.06)])
        stops.append(["main_pass", "gas_station", (-129.88, -267.19)])
        stops.append(["gas_station", "simons_way", (384.69, -500.81)])

    if route == "route_4":  # 2 rev
        stops.append(["simons_way", "gas_station", (892.19, -992.31)])
        stops.append(["gas_station", "main_pass", (384.69, -500.81)])
        stops.append(["main_pass", "hillside_road", (-129.88, -267.19)])
        stops.append(["hillside_road", "drifters_corner", (-414.63, -989.06)])

    if route == "route_5":  # 3
        stops.append(["simons_way", "corkscrew", (892.19, -992.31)])
        stops.append(["corkscrew", "the_bridge", (104.44, 100.06)])
        stops.append(["the_bridge", "snake_pass", (-103.81, 657.25)])
        stops.append(["snake_pass", "main_street_north", (-308.81, 524.81)])
        stops.append(["main_street_north", "pond_lane", (-357.63, 34.56)])
        stops.append(["pond_lane", "main_station", (-256.31, -71.56)])

    if route == "route_6":  # 3 rev
        stops.append(["main_station", "pond_lane", (-211.63, 231.00)])
        stops.append(["pond_lane", "main_street_north", (-256.31, -71.56)])
        stops.append(["main_street_north", "snake_pass", (-338.94, 37.13)])
        stops.append(["snake_pass", "the_bridge", (-308.81, 524.81)])
        stops.append(["the_bridge", "corkscrew", (-103.81, 657.25)])
        stops.append(["corkscrew", "simons_way", (104.44, 100.06)])

    if route == "route_7":  # 4
        stops.append(["drifters_corner", "main_street_south", (-1006.31, -1050.69)])
        stops.append(["main_street_south", "main_street_north", (-461.81, -651.06)])
        stops.append(["main_street_north", "corkscrew", (-338.94, 37.13)])
        stops.append(["corkscrew", "simons_way", (104.44, 100.06)])

    if route == "route_8":  # 4rev
        stops.append(["simons_way", "corkscrew", (892.19, -992.31)])
        stops.append(["corkscrew", "main_street_north", (104.44, 100.06)])
        stops.append(["main_street_north", "main_street_south", (-357.63, 34.56)])
        stops.append(["main_street_south", "drifters_corner", (-461.81, -651.06)])

    for i, stop in enumerate(stops):
        distance = dist(stop[2], (own_x / 65536, own_y / 65536))
        arr_app = [stop[0], stop[1], distance]
        return_array.append(arr_app)
    return return_array


def stop_dist_BL(route, own_x, own_y):
    stops = []
    return_array = []

    if route == "route_1":  # red
        stops.append(["main_station", "forest_hill", (-219.19, 215.00)])
        stops.append(["forest_hill", "velocity_ave", (-347.81, 344.75)])
        stops.append(["velocity_ave", "blackwood_heights", (-544.94, 401.56)])
        stops.append(["blackwood_heights", "narrow_passage", (-892.94, 401.38)])
        stops.append(["narrow_passage", "forest", (-823.31, 729.75)])
        stops.append(["forest", "forest_hill", (-302.94, 698.06)])
        stops.append(["forest_hill", "main_station_a", (-310.38, 344.13)])

    if route == "route_2":  # blue
        stops.append(["main_station", "ellecsix_boulevard", (-211.63, 231.00)])
        stops.append(["ellecsix_boulevard", "industry_lane", (-384.56, 169.38)])
        stops.append(["industry_lane", "lyon_road", (-698.63, 204.00)])
        stops.append(["lyon_road", "bourne_road", (-750.56, 430.19)])
        stops.append(["bourne_road", "manor_way", (-594.19, 715.75)])
        stops.append(["manor_way", "forest_hill", (-378.81, 534.06)])
        stops.append(["forest_hill", "main_station_b", (-310.38, 344.13)])

    if route == "route_3":  # yellow
        stops.append(["main_station", "gas_station", (-211.63, 231.00)])
        stops.append(["gas_station", "devils_corner", (-125.75, 165.06)])  # TODO Bug investigation
        stops.append(["devils_corner", "hw1_underpass", (32.44, 631.44)])
        stops.append(["hw1_underpass", "southslope", (339.44, -244.00)])
        stops.append(["southslope", "lower_bl_parking", (298.19, -777.88)])
        stops.append(["lower_bl_parking", "pit_entrance", (-166.69, -349.13)])
        stops.append(["pit_entrance", "main_station_b", (-97.25, -65.75)])

    if route == "route_4":  # green
        stops.append(["main_station", "south_exit", (-219.19, 215.00)])
        stops.append(["south_exit", "pioneer_approach", (-194.69, -74.31)])
        stops.append(["pioneer_approach", "calleons_drive", (-355.19, -110.06)])
        stops.append(["calleons_drive", "taunton_road", (-435.38, 36.38)])
        stops.append(["taunton_road", "willow_way", (-557.69, 208.00)])
        stops.append(["willow_way", "burnt_mills", (-483.06, 180.19)])
        stops.append(["burnt_mills", "idle_road", (-753.94, 61.06)])
        stops.append(["idle_road", "velocity_ave", (-661.31, 319.38)])
        stops.append(["velocity_ave", "lyon_road", (-544.94, 401.56)])
        stops.append(["lyon_road", "bourne_road", (-750.56, 430.19)])
        stops.append(["bourne_road", "manor_way", (-594.19, 715.75)])
        stops.append(["manor_way", "forest_hill", (-378.81, 534.06)])
        stops.append(["forest_hill", "main_station_b", (-310.38, 344.13)])

    for i, stop in enumerate(stops):
        distance = dist(stop[2], (own_x / 65536, own_y / 65536))
        arr_app = [stop[0], stop[1], distance]
        return_array.append(arr_app)
    return return_array


def stop_dist_FE(route, own_x, own_y):
    stops = []
    return_array = []

    if route == "route_1":  # Eastern Short
        stops.append(["east_station", "the_swamps", (267.19, -495.00)])
        stops.append(["the_swamps", "highway_1", (230.69, -277.94)])
        stops.append(["highway_1", "hills_north", (206.75, 401.75)])
        stops.append(["hills_north", "the_ridge", (294.94, 40.25)])
        stops.append(["the_ridge", "the_swamps", (382.19, -133.50)])
        stops.append(["the_swamps", "east_station", (202.88, -280.19)])

    if route == "route_2":  # Eastern short rev
        stops.append(["east_station", "the_swamps", (267.19, -495.00)])
        stops.append(["the_swamps", "the_ridge", (230.69, -277.94)])
        stops.append(["the_ridge", "hills_north", (382.19, -133.50)])
        stops.append(["hills_north", "highway_1", (294.94, 40.25)])
        stops.append(["highway_1", "the_swamps", (206.75, 401.75)])
        stops.append(["the_swamps", "east_station", (202.88, -280.19)])

    if route == "route_3":  # Eastern Route
        stops.append(["east_station", "dead_mens", (267.19, -495.00)])
        stops.append(["dead_mens", "highway_1", (172.19, -245.00)])
        stops.append(["highway_1", "hills_north", (206.75, 401.75)])
        stops.append(["hills_north", "hills_central", (294.94, 40.25)])
        stops.append(["hills_central", "hills_south", (481.50, -192.13)])
        stops.append(["hills_south", "devils_corner", (513.88, -471.00)])
        stops.append(["devils_corner", "underpass", (-23.06, -783.94)])
        stops.append(["underpass", "east_station", (194.50, -713.88)])

    if route == "route_4":  # Eastern Route Rev
        stops.append(["east_station", "underpass", (267.19, -495.00)])
        stops.append(["underpass", "devils_corner", (194.50, -713.88)])
        stops.append(["devils_corner", "hills_south", (-23.06, -783.94)])
        stops.append(["hills_south", "hills_central", (513.88, -471.00)])
        stops.append(["hills_central", "hills_north", (481.50, -192.13)])
        stops.append(["hills_north", "highway_1", (294.94, 40.25)])
        stops.append(["highway_1", "dead_mens", (206.75, 401.75)])
        stops.append(["dead_mens", "east_station", (305.31, 79.00)])

    if route == "route_7":  # Transit West
        stops.append(["east_station", "the_swamps", (267.19, -495.00)])
        stops.append(["the_swamps", "the_ridge", (222.75, -797.31)])
        stops.append(["the_ridge", "hills_central", (382.19, -133.50)])
        stops.append(["hills_central", "hills_south", (481.50, -192.13)])
        stops.append(["hills_south", "west_station", (513.88, -471.00)])

    if route == "route_5":  # Grand Tour
        stops.append(["east_station", "dead_mens", (267.19, -495.00)])
        stops.append(["dead_mens", "highway_1", (-114.25, -485.44)])
        stops.append(["highway_1", "hills_north", (206.75, 401.75)])
        stops.append(["hills_north", "hills_central", (294.94, 40.25)])
        stops.append(["hills_central", "hills_south", (481.50, -192.13)])
        stops.append(["hills_south", "the_steeps", (513.88, -471.00)])
        stops.append(["the_steeps", "lower_bayside", (-341.81, -732.38)])
        stops.append(["lower_bayside", "upper_bayside", (-436.56, -463.69)])
        stops.append(["upper_bayside", "the_villa", (-233.06, 206.81)])
        stops.append(["the_villa", "highway_2_north", (-35.38, 513.63)])
        stops.append(["highway_2_north", "highway_2_central", (24.75, 280.75)])
        stops.append(["highway_2_central", "highway_2_south", (24.25, -16.56)])
        stops.append(["highway_2_south", "devils_corner", (-0.13, -568.13)])
        stops.append(["devils_corner", "underpass", (-23.06, -783.94)])
        stops.append(["underpass", "east_station", (194.50, -713.88)])

    if route == "route_6":  # Grand Tour Rev
        stops.append(["east_station", "underpass", (267.19, -495.00)])
        stops.append(["underpass", "devils_corner", (194.50, -713.88)])
        stops.append(["devils_corner", "highway_2_south", (-23.06, -783.94)])
        stops.append(["highway_2_south", "highway_2_central", (-0.13, -568.13)])
        stops.append(["highway_2_central", "highway_2_north", (24.25, -16.56)])
        stops.append(["highway_2_north", "the_villa", (24.75, 280.75)])
        stops.append(["the_villa", "upper_bayside", (-35.38, 513.63)])
        stops.append(["upper_bayside", "lower_bayside", (-233.06, 206.81)])
        stops.append(["lower_bayside", "the_steeps", (-436.56, -463.69)])
        stops.append(["the_steeps", "hills_south", (-341.81, -732.38)])
        stops.append(["hills_south", "hills_central", (513.88, -471.00)])
        stops.append(["hills_central", "hills_north", (481.50, -192.13)])
        stops.append(["hills_north", "highway_1", (294.94, 40.25)])
        stops.append(["highway_1", "the_swamps", (206.75, 401.75)])
        stops.append(["the_swamps", "east_station", (202.88, -280.19)])
    # TODO Routes missing
    if route == "route_8":  # western short route
        stops.append(["west_station", "northpark_1", (267.19, -495.00)])
        stops.append(["northpark_1", "northpark_2", (-54.94, -171.38)])
        stops.append(["northpark_2", "highway_2_central", (-40.88, 74.63)])
        stops.append(["highway_2_central", "highway_2_south", (24.25, -16.56)])
        stops.append(["highway_2_south", "west_station", (-0.13, -568.13)])

    if route == "route_9":  # western short route rev
        stops.append(["west_station", "highway_2_south", (267.19, -495.00)])
        stops.append(["highway_2_south", "highway_2_central", (-0.13, -568.13)])
        stops.append(["highway_2_central", "northpark_2", (24.25, -16.56)])
        stops.append(["northpark_2", "northpark_1", (-40.88, 74.63)])
        stops.append(["northpark_1", "west_station", (-54.94, -171.38)])

    for i, stop in enumerate(stops):
        distance = dist(stop[2], (own_x / 65536, own_y / 65536))
        arr_app = [stop[0], stop[1], distance]
        return_array.append(arr_app)
    return return_array


def stop_dist_KY(route, own_x, own_y):
    stops = []
    return_array = []

    if route == "route_3":
        stops.append(["main_station", "overpass", (237.44, -469.81)])
        stops.append(["overpass", "gas_station", (-114.25, -485.44)])
        stops.append(["gas_station", "needles", (-413.81, -216.19)])
        stops.append(["needles", "business_park", (-501.50, 1011.94)])
        stops.append(["business_park", "pit_lane_2_exit", (-589.75, 787.19)])
        stops.append(["pit_lane_2_exit", "ab_resting_station", (-461.63, 596.06)])
        stops.append(["ab_resting_station", "arena", (-14.50, 738.63)])
        stops.append(["arena", "underpass", (315.69, 92.63)])
        stops.append(["underpass", "northpoint_view", (-145.44, -526.44)])
        stops.append(["northpoint_view", "main_station", (222.75, -797.31)])

    if route == "route_2":
        stops.append(["main_station", "northpoint_view", (237.44, -469.81)])
        stops.append(["northpoint_view", "underpass", (222.75, -797.31)])
        stops.append(["underpass", "arena", (-145.44, -526.44)])
        stops.append(["arena", "roundabout", (315.69, 92.63)])
        stops.append(["roundabout", "pit_lane_2_entry", (101.81, 48.06)])
        stops.append(["pit_lane_2_entry", "business_park", (-371.25, 75.94)])
        stops.append(["business_park", "needles", (-589.75, 787.19)])
        stops.append(["needles", "gas_station", (-501.50, 1011.94)])
        stops.append(["gas_station", "overpass", (-413.81, -216.19)])
        stops.append(["overpass", "main_station", (-114.25, -485.44)])

    if route == "route_1":
        stops.append(["main_station", "overpass", (237.44, -469.81)])
        stops.append(["overpass", "gas_station", (-114.25, -485.44)])
        stops.append(["gas_station", "needles", (-413.81, -216.19)])
        stops.append(["needles", "business_park", (-501.50, 1011.94)])
        stops.append(["business_park", "pit_lane_2_exit", (-589.75, 787.19)])
        stops.append(["pit_lane_2_exit", "ab_resting_station", (-461.63, 596.06)])
        stops.append(["ab_resting_station", "the_beach", (-14.50, 738.63)])
        stops.append(["the_beach", "infield", (161.69, 477.81)])
        stops.append(["infield", "swimming_pool", (-142.94, 369.31)])
        stops.append(["swimming_pool", "arena", (-33.06, 225.25)])
        stops.append(["arena", "underpass", (315.69, 92.63)])
        stops.append(["underpass", "northpoint_view", (-145.44, -526.44)])
        stops.append(["northpoint_view", "main_station", (222.75, -797.31)])

    if route == "route_4":
        stops.append(["main_station", "northpoint_view", (237.44, -469.81)])
        stops.append(["northpoint_view", "underpass", (208.63, -793.75)])
        stops.append(["underpass", "arena", (-130.44, -526.19)])
        stops.append(["arena", "swimming_pool", (326.25, 105.19)])
        stops.append(["swimming_pool", "infield", (-33.06, 225.25)])
        stops.append(["infield", "the_beach", (-142.94, 369.31)])
        stops.append(["the_beach", "arena", (161.69, 477.81)])
        stops.append(["arena", "underpass", (305.31, 79.00)])
        stops.append(["underpass", "northpoint_view", (-161.00, -526.75)])
        stops.append(["northpoint_view", "main_station", (237.13, -801.31)])

    for i, stop in enumerate(stops):
        distance = dist(stop[2], (own_x / 65536, own_y / 65536))
        arr_app = [stop[0], stop[1], distance]
        return_array.append(arr_app)
    return return_array


def stop_dist(route, own_x, own_y):
    stops = []
    return_array = []
    if route == "route_1":
        stops.append(["main_station", "station_boulevard", (-114.19, 462.88)])
        stops.append(["station_boulevard", "highway_1", (-197.63, 590.94)])
        stops.append(["highway_1", "foster_street", (269.81, -19.81)])
        stops.append(["foster_street", "mendora_bend", (350.31, -347.88)])
        stops.append(["mendora_bend", "acme_street", (324.94, -531.5)])
        stops.append(["acme_street", "lower_high_st", (-253.13, -38.69)])
        stops.append(["lower_high_st", "main_station", (-168.63, 206.00)])

    elif route == "route_2":
        stops.append(["main_station", "station_boulevard_2", (-114.19, 462.88)])
        stops.append(["station_boulevard_2", "upper_high_st", (-149.94, 426.88)])
        stops.append(["upper_high_st", "highway_1", (-67.13, 34.31)])
        stops.append(["highway_1", "main_station", (245.13, -74.00)])

    elif route == "route_3":
        stops.append(["main_station", "station_boulevard", (-114.19, 462.88)])
        stops.append(["station_boulevard", "highway_1", (-197.63, 590.94)])
        stops.append(["highway_1", "foster_street", (269.81, -19.81)])
        stops.append(["foster_street", "mendora_bend", (350.31, -347.88)])
        stops.append(["mendora_bend", "acme_street", (324.94, -531.5)])
        stops.append(["acme_street", "upper_high_st", (-253.13, -38.69)])
        stops.append(["upper_high_st", "highway_1", (-67.13, 34.31)])
        stops.append(["highway_1", "main_station", (245.13, -74.00)])

    elif route == "route_4":
        stops.append(["main_station", "station_boulevard_2", (-114.19, 462.88)])
        stops.append(["station_boulevard_2", "acme_street", (-149.94, 426.88)])
        stops.append(["acme_street", "mendora_bend", (-253.31, 24.38)])
        stops.append(["mendora_bend", "foster_street", (295.50, -482.81)])
        stops.append(["foster_street", "highway_1", (332.81, -343.56)])
        stops.append(["highway_1", "main_station", (245.13, -74.00)])

    elif route == "route_5":
        stops.append(["main_station", "station_boulevard_2", (-114.19, 462.88)])
        stops.append(["station_boulevard_2", "castle_hill_1", (-149.94, 426.88)])
        stops.append(["castle_hill_1", "castle_hill_2", (-383.31, 425.81)])
        stops.append(["castle_hill_2", "castle_hill_3", (-565.06, 449.44)])
        stops.append(["castle_hill_3", "main_station", (-441.94, 209.94)])

    elif route == "route_6":
        stops.append(["main_station", "station_boulevard_2", (-423.38, 186.75)])
        stops.append(["station_boulevard_2", "castle_hill_3", (-149.94, 426.88)])
        stops.append(["castle_hill_3", "castle_hill_2", (-423.38, 186.75)])
        stops.append(["castle_hill_2", "castle_hill_1", (-600.56, 446.13)])
        stops.append(["castle_hill_1", "main_station", (-379.38, 457.19)])

    elif route == "route_7":
        stops.append(["main_station", "station_boulevard", (-114.19, 462.88)])
        stops.append(["station_boulevard", "highway_1", (-197.63, 590.94)])
        stops.append(["highway_1", "foster_street", (269.81, -19.81)])
        stops.append(["foster_street", "mendora_bend", (350.31, -347.88)])
        stops.append(["mendora_bend", "acme_street", (324.94, -531.5)])
        stops.append(["acme_street", "upper_high_st", (-253.13, -38.69)])
        stops.append(["upper_high_st", "highway_1", (-67.13, 34.31)])
        stops.append(["highway_1", "station_boulevard_2", (245.13, -74.00)])
        stops.append(["station_boulevard_2", "castle_hill", (-149.94, 426.88)])
        stops.append(["castle_hill_1", "castle_hill_2", (-383.31, 425.81)])
        stops.append(["castle_hill_2", "castle_hill_3", (-565.06, 449.44)])
        stops.append(["castle_hill_3", "main_station", (-441.94, 209.94)])
    for i, stop in enumerate(stops):
        distance = dist(stop[2], (own_x / 65536, own_y / 65536))
        arr_app = [stop[0], stop[1], distance]
        return_array.append(arr_app)
    return return_array


stop_name = ""
track1 = ""
door = True
route = True


def play_sound_stop():
    if door and "route" in stop_name:
        winsound.PlaySound('data\\bus\\door_open.wav', winsound.SND_FILENAME)
    if route and "route" in stop_name or not "route" in stop_name:
        if track1 == b"SO":
            winsound.PlaySound('data\\bus\\' + stop_name + '.wav', winsound.SND_FILENAME)
        elif track1 == b"KY":
            winsound.PlaySound('data\\bus\\kyoto_' + stop_name + '.wav', winsound.SND_FILENAME)
        elif track1 == b"FE":
            winsound.PlaySound('data\\bus\\fern_' + stop_name + '.wav', winsound.SND_FILENAME)
        elif track1 == b"BL":
            winsound.PlaySound('data\\bus\\bl_' + stop_name + '.wav', winsound.SND_FILENAME)
        elif track1 == b"AS":
            winsound.PlaySound('data\\bus\\as_' + stop_name + '.wav', winsound.SND_FILENAME)
        elif track1 == b"WE":
            winsound.PlaySound('data\\bus\\we_' + stop_name + '.wav', winsound.SND_FILENAME)
    if door and "route" in stop_name:
        time.sleep(1)
        winsound.PlaySound('data\\bus\\door_close.wav', winsound.SND_FILENAME)


def play_stop_sound(string, track, route_sound, door_sound):
    global stop_name
    global track1
    global door
    global route
    door = door_sound
    route = route_sound
    track1 = track
    stop_name = string
    play_stop_thread = Thread(target=play_sound_stop)
    play_stop_thread.start()


def dist(a=(0, 0), b=(0, 0)):
    """Determine the distance between two points."""
    return math.sqrt(
        (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]))
