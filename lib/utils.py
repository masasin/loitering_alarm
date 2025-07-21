import time

import machine


class Pin(machine.Pin):
    def __init__(
        self,
        pin_number: int,
        mode: int = -1,
        pull: int = -1,
        *args,
        **kwargs,
    ) -> None:
        self.pin = machine.Pin(pin_number, mode, pull, *args, **kwargs)

    def __getattr__(self, name: str):
        try:
            return getattr(self.pin, name)
        except AttributeError:
            return getattr(machine.Pin, name)

    @property
    def value(self) -> int:
        return self.pin.value()

    @value.setter
    def value(self, value: int | float) -> None:
        self.pin.value(value)

    def on(self) -> None:
        self.value = 1

    def off(self) -> None:
        self.value = 0

    def toggle(self):
        self.value = 1 - self.value

    @property
    def is_on(self) -> bool:
        return self.value == 1

    @property
    def is_off(self) -> bool:
        return not self.is_on

    def send_pulse_us(self, duration_us: float | int, *, high: bool = True) -> None:
        base_level = 0 if high else 1
        pulse_level = 1 if high else 0

        self.value = base_level
        time.sleep_us(2)
        self.value = pulse_level
        time.sleep_us(int(duration_us - 2))
        self.value = base_level

    def time_pulse_us(self, *, high: bool = True, timeout_us: int = 1_000_000) -> int:
        return machine.time_pulse_us(self.pin, 1 if high else 0, timeout_us)


class PWM:
    DUTY_CYCLE_MAX = 65535

    def __init__(
        self,
        pin_number: int,
        freq: int = 5000,
        duty_cycle: float = 0,
        **kwargs,
    ) -> None:
        self.pwm = machine.PWM(
            machine.Pin(pin_number, machine.Pin.OUT),
            freq=freq,
            duty_u16=0,
            **kwargs,
        )
        self._duty_cycle = duty_cycle

    def __getattr__(self, name: str):
        try:
            return getattr(self.pwm, name)
        except AttributeError:
            return getattr(machine.PWM, name)

    @property
    def freq(self) -> int:
        return self.pwm.freq()

    @freq.setter
    def freq(self, value: int) -> None:
        self.pwm.freq(value)

    def on(self, *, freq: int | None = None, duty_cycle: float | None = None) -> None:
        if freq is not None:
            self.freq = freq
        if duty_cycle is None:
            duty_cycle = self._duty_cycle

        self.pwm.duty_u16(int(self.DUTY_CYCLE_MAX * duty_cycle))

    def off(self) -> None:
        self.pwm.duty_u16(0)

    @property
    def is_on(self) -> bool:
        return self.pwm.duty_u16() > 0

    @property
    def is_off(self) -> bool:
        return not self.is_on

    def send_pulse_us(
        self,
        duration_us: int,
        *,
        freq: int | None = None,
        duty_cycle: float | None = None,
    ) -> None:
        self.on(freq=freq, duty_cycle=duty_cycle)
        time.sleep_us(duration_us)
        self.off()
