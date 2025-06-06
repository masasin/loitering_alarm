from lib import LCD, Buzzer, DistanceSensor
from time import sleep


class LoiteringAlarm:
    RESOLUTION = 0.5  # seconds

    def __init__(
        self,
        distance_sensor: DistanceSensor,
        display: LCD,
        buzzer: Buzzer,
        *,
        min_distance_cm: float = 60,
        max_distance_cm: float = 120,
        alert_after_seconds: int = 5 * 60,
        timeout_seconds: int = 30,
    ) -> None:
        self.distance_sensor = distance_sensor
        self.display = display
        self.buzzer = buzzer
        self.min_distance_cm = min_distance_cm
        self.max_distance_cm = max_distance_cm
        self.alert_after_seconds = alert_after_seconds
        self.timeout_seconds = timeout_seconds

        self._elapsed_time = 0
        self._occluded_time = 0

    def run(self):
        while True:
            if (distance := self.distance_sensor.distance) is None:
                continue

            self._write_distance(distance)
            self._write_times()

            self._update_times(distance)

            self._trigger_buzzer()

            sleep(self.RESOLUTION)

    def _write_distance(self, distance: float) -> None:
        self.display.set_cursor(0, 0)
        self.display.write(f"{distance:5.1f} cm")

    def _write_times(self) -> None:
        countdown = abs(self.alert_after_seconds - self._elapsed_time)
        minutes, seconds = divmod(countdown, 60)

        self.display.set_cursor(1, 0)
        self.display.write(f"{minutes:02.0f}:{seconds:02.0f}")

        time_to_timeout = self.timeout_seconds - self._occluded_time
        self.display.set_cursor(1, 6)
        self.display.write(f"{time_to_timeout:02.0f}")

    def _update_times(self, distance: float) -> None:
        if self.min_distance_cm <= distance <= self.max_distance_cm:
            self._elapsed_time += self.RESOLUTION
            self._occluded_time = 0
            return

        if self._elapsed_time == 0:
            return

        self._elapsed_time += self.RESOLUTION
        self._occluded_time += self.RESOLUTION
        if self._occluded_time >= self.timeout_seconds:
            self._elapsed_time = 0
            self._occluded_time = 0

    def _trigger_buzzer(self) -> None:
        if self._elapsed_time < self.alert_after_seconds:
            if self.buzzer.is_on:
                self.buzzer.off()
            return

        self.buzzer.on()
