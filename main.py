from time import sleep

from lib import HC_SR04, AE_AQM0802


distance_sensor = HC_SR04(trigger_pin=14, echo_pin=15)
display = AE_AQM0802(clock_pin=17, data_pin=16)

while True:
    if (distance := distance_sensor.distance) is not None:
        print(f"Distance: {distance:.1f} cm")
        display.write(f"{distance:.1f} cm" + " " * 8)
        display.set_cursor(0, 0)
    sleep(0.5)
