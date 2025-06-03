from lib.utils import Pin


class HC_SR04:
    def __init__(
        self, trigger_pin: int, echo_pin: int, echo_timeout_us: int = 10_000
    ) -> None:
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.echo_timeout_us = echo_timeout_us

    @property
    def distance(self) -> float | None:
        self.trigger.send_pulse_us(10)
        try:
            pulse_time = self.echo.time_pulse_us(timeout_us=self.echo_timeout_us)
            if pulse_time < 0:
                print("Timeout occurred while waiting for echo.")
                return
            return (pulse_time * 0.0343) / 2  # cm
        except Exception as e:
            print(e)
