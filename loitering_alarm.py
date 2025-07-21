from time import sleep

from lib import LCD, Buzzer, DistanceSensor, Pin


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
        debug: bool = False,
    ) -> None:
        self.distance_sensor = distance_sensor
        self.display = display
        self.buzzer = buzzer
        self.min_distance_cm = min_distance_cm
        self.max_distance_cm = max_distance_cm
        self.alert_after_seconds = alert_after_seconds
        self.timeout_seconds = timeout_seconds
        self.debug = debug
        self.led = Pin(25, Pin.OUT)
        self.led.on()

        self._elapsed_time = 0
        self._occluded_time = 0

        self._writers = []

        if self.debug:
            self._writers.append(print)

        if self.display.is_available():
            self._writers.append(display.write)

    def run(self):
        while True:
            if (distance := self.distance_sensor.distance) is None:
                continue

            self._write_data(distance)

            self._update_times(distance)
            self._trigger_buzzer()
            self._flash_led()

    def _write_data(self, distance: float) -> None:
        for writer in self._writers:
            distance_str = f"{distance:5.1f} cm"
            time_str = (
                f"{self._format_mmss(self._countdown)} {self._time_to_timeout:02.0f}"
            )
            writer(f"{distance_str}\n{time_str}")

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

    def _flash_led(self) -> None:
        if self._elapsed_time == 0:
            self.led.on()
            sleep(self.RESOLUTION)
            return

        if self._occluded_time > 0:
            flashes_per_resolution = 5
            pulse_length = self.RESOLUTION * 1e6 // flashes_per_resolution
            for _ in range(flashes_per_resolution):
                self.led.send_pulse_us(pulse_length, high=self.led.is_on)
        else:
            self.led.send_pulse_us(self.RESOLUTION * 1e6, high=self.led.is_on)

    def _trigger_buzzer(self) -> None:
        if self._elapsed_time < self.alert_after_seconds:
            if self.buzzer.is_on:
                self.buzzer.off()
            return

        if self._occluded_time == 0:
            self.buzzer.on()

    def _format_mmss(self, seconds: float) -> str:
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"

    @property
    def _countdown(self) -> float:
        return abs(self.alert_after_seconds - self._elapsed_time)

    @property
    def _time_to_timeout(self) -> float:
        return self.timeout_seconds - self._occluded_time
