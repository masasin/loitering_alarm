from loitering_alarm import LoiteringAlarm

from lib import (
    AE_AQM0802,
    Buzzer,
    HC_SR04,
)


def build_test_loitering_alarm(*, distance_sensor, display, buzzer):
    return LoiteringAlarm(
        distance_sensor=distance_sensor,
        display=display,
        buzzer=buzzer,
        min_distance_cm=10,
        max_distance_cm=20,
        alert_after_seconds=10,
        timeout_seconds=5,
    )


def build_loitering_alarm(*, distance_sensor, display, buzzer):
    return LoiteringAlarm(
        distance_sensor=distance_sensor,
        display=display,
        buzzer=buzzer,
        min_distance_cm=60,
        max_distance_cm=120,
        alert_after_seconds=5 * 60,
        timeout_seconds=30,
    )


if __name__ == "__main__":
    distance_sensor = HC_SR04(trigger_pin=14, echo_pin=15)
    display = AE_AQM0802(clock_pin=17, data_pin=16)
    buzzer = Buzzer(pin_number=13, is_active=False)

    # loitering_alarm = build_test_loitering_alarm(
    loitering_alarm = build_loitering_alarm(
        distance_sensor=distance_sensor,
        display=display,
        buzzer=buzzer,
    )

    loitering_alarm.run()
