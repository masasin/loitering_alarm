import time

from controllers import LEDController
from lib import LCD, Buzzer, DistanceSensor
from states import State
from writers import Writer, lcd_formatter, serial_writer


class LoiteringAlarm:
    def __init__(
        self,
        distance_sensor: DistanceSensor,
        display: LCD,
        buzzer: Buzzer,
        monitor: LoiteringMonitor,
        *,
        min_distance_cm: float = 60,
        max_distance_cm: float = 120,
        led_controller: LEDController = LEDController(pin_number=25),
        debug: bool = False,
    ) -> None:
        self.distance_sensor = distance_sensor
        self.display = display
        self.buzzer = buzzer
        self.monitor = monitor
        self.min_distance_cm = min_distance_cm
        self.max_distance_cm = max_distance_cm

        self.led = led_controller

        self._action_handlers = {
            State.IDLE: self._action_idle,
            State.DETECTED: self._action_detected,
            State.OCCLUDED: self._action_occluded,
            State.ALARM: self._action_alarm,
            State.ARMED: self._action_armed,
        }

        self._writers = []
        if debug:
            self._writers.append(serial_writer)
        if self.display.is_available():
            self._writers.append(Writer(self.display.write, lcd_formatter))

    def run(self):
        while True:
            if (distance := self.distance_sensor.distance) is None:
                continue

            is_in_range = self.min_distance_cm <= distance <= self.max_distance_cm
            self.monitor.update(is_in_range)

            self._action_handlers[self.monitor.state]()
            self._write_data(distance)

    def _write_data(self, distance: float) -> None:
        data = {
            "distance": distance,
            "state": self.monitor.state,
            "time_to_alert": self.monitor.time_to_alert,
            "time_to_reset": self.monitor.time_to_reset,
        }
        for writer in self._writers:
            writer.function(writer.formatter(data))

    def _action_idle(self):
        self.led.on()
        self.buzzer.off()
        time.sleep(self.resolution)

    def _action_detected(self):
        if self.monitor.elapsed_time >= self.resolution * 2:
            # At least two consecutive detections
            self.led.flash_detected(self.resolution)
        else:
            time.sleep(self.resolution)
        self.buzzer.off()

    def _action_occluded(self):
        self.led.flash_occluded(self.resolution)
        self.buzzer.off()

    def _action_alarm(self):
        self.led.flash_alarm(self.resolution)
        self.buzzer.on()

    def _action_armed(self):
        self.led.flash_armed(self.resolution)

    @property
    def resolution(self) -> float:
        return self.monitor.resolution
