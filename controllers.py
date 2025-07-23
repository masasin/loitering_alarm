from lib import Pin


class LEDController:
    def __init__(
        self,
        pin_number: int,
        freq_detected: float = 10,
        freq_occluded: float = 2,
        freq_alarm: float | None = None,
        freq_armed: float | None = None,
    ):
        self.led = Pin(pin_number, Pin.OUT)
        self.freq_detected = freq_detected
        self.freq_occluded = freq_occluded

        if freq_alarm is None:
            freq_alarm = freq_detected
        self.freq_alarm = freq_alarm

        if freq_armed is None:
            freq_armed = freq_occluded
        self.freq_armed = freq_armed

    def on(self):
        self.led.on()

    def flash_detected(self, duration: float) -> None:
        self.led.pulse(self.freq_detected, duration)

    def flash_occluded(self, duration: float) -> None:
        self.led.pulse(self.freq_occluded, duration)

    def flash_alarm(self, duration: float) -> None:
        self.led.pulse(self.freq_detected, duration)

    def flash_armed(self, duration: float) -> None:
        self.led.pulse(self.freq_armed, duration)
