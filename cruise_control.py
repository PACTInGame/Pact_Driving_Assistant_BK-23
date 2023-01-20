
def calculate_acc_distance(speed, other_car_dynamic, rel_speed):

    return speed/8 + other_car_dynamic - rel_speed + 11

# TODO SLOPES!
def adaptive_cruise_control(speed, rel_speed, distance, other_car_dynamic, car_in_front, set_speed):
    acc_distance = 0
    if car_in_front:
        acc_distance = calculate_acc_distance(speed, other_car_dynamic, rel_speed)
        acc_bra = (distance - acc_distance)*2
    else:
        acc_bra = 100

    if acc_bra > 100:
        acc_bra = 100

    elif acc_bra < -100:
        acc_bra = -100

    limit = set_speed - speed + 10
    if limit < acc_bra:
        acc_bra = limit * 2
    return acc_bra
