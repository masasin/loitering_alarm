import time

from lib.utils import PWM, Pin


class Pulse:
    def __init__(
        self,
        *,
        duration_ms: int,
        rest_ms: int = 0,
        freq: int | None = None,
        duty_cycle: float | None = None,
    ) -> None:
        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")
        if rest_ms < 0:
            raise ValueError("rest_ms cannot be negative")
        if duty_cycle is not None and not 0 <= duty_cycle <= 1:
            raise ValueError("duty_cycle must be between 0 and 1")
        if freq is not None and freq <= 0:
            raise ValueError("freq must be positive")

        self.duration_ms = duration_ms
        self.rest_ms = rest_ms
        self.freq = freq
        self.duty_cycle = duty_cycle


class Buzzer:
    def __init__(
        self,
        pin_number: int,
        *,
        is_active: bool = True,
        freq: int = 5000,
        duty_cycle: float = 0.5,
    ) -> None:
        self._is_active = is_active

        self.hardware: Pin | PWM
        if self.is_active:
            self.hardware = Pin(pin_number, Pin.OUT)
        else:
            self.hardware = PWM(pin_number, freq=freq, duty_cycle=duty_cycle)

    def on(self) -> None:
        self.hardware.on()

    def off(self) -> None:
        self.hardware.off()

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_on(self) -> bool:
        return self.hardware.is_on

    @property
    def is_off(self) -> bool:
        return not self.is_on

    def beep(
        self,
        duration_ms: int,
        *,
        freq: int | None = None,
        duty_cycle: float | None = None,
    ) -> None:
        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

        if self.is_active:
            assert isinstance(self.hardware, Pin)
            self.hardware.send_pulse_us(duration_ms * 1000)
        else:
            assert isinstance(self.hardware, PWM)
            self.hardware.send_pulse_us(
                duration_ms * 1000,
                freq=freq,
                duty_cycle=duty_cycle,
            )

    def play(self, pulses: list[Pulse]) -> None:
        for pulse in pulses:
            self.beep(
                pulse.duration_ms,
                freq=pulse.freq,
                duty_cycle=pulse.duty_cycle,
            )

            time.sleep_ms(pulse.rest_ms)
