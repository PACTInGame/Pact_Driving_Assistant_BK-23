import pyinsim

insim = pyinsim.insim(b'127.0.0.1', 29999, Admin=b'', Flags=pyinsim.ISF_MCI | pyinsim.ISF_LOCAL, Interval=1000)

PLID = 0
cars = []
xCoord = 0
yCoord = 0
zCoord = 0


# The array cars will contain arrays that represent a car and its data.
# Example: cars[0] would contain PLID, X, Y, Z, Speed, Heading
# Keep in mind: when more than 8 cars are on the track, more than one MCI packet is sent


def outgauge(outgauge, packet):
    global PLID
    PLID = packet.PLID


outgauge = pyinsim.outgauge(b'127.0.0.1', 30000, outgauge, 30.0)



def get_car_data(insim, mci):
    global cars, xCoord, yCoord, zCoord
    # Save new arrays of car data in update cars and then override cars, so that no data gets lost or doubled
    update_cars = []

    for car in mci.Info:
        if car.PLID == PLID:
            xCoord = car.X / 65536
            yCoord = car.Y / 65536
            zCoord = car.Z / 65536
            print(car.Heading)

        else:
            temp = [car.PLID, car.X / 65536, car.Y / 65536, car.Z / 65536, car.Speed / 91.02, car.Heading]
            update_cars.append(temp)

    cars = update_cars


insim.bind(pyinsim.ISP_MCI, get_car_data)

pyinsim.run()