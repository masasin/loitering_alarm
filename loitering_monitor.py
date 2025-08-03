from states import Event, State, create_state_machine

from lib import StateMachine


class LoiteringMonitor:
    def __init__(
        self,
        alert_after_seconds: int = 5 * 60,
        timeout_seconds: int = 30,
        resolution: float = 0.5,
        fsm: StateMachine = create_state_machine(),
    ):
        self.alert_after_seconds = alert_after_seconds
        self.timeout_seconds = timeout_seconds
        self.resolution = resolution
        self._fsm = fsm

        self._elapsed_time = 0
        self._occluded_time = 0

    def update(self, is_in_range: bool) -> None:
        self._update_times()

        if is_in_range:
            self._fsm.transition(Event.TARGET_IN_RANGE)
        else:
            self._fsm.transition(Event.TARGET_OUT_OF_RANGE)

        if self._elapsed_time >= self.alert_after_seconds:
            self._fsm.transition(Event.ALERT_TIME_REACHED)

        if self._occluded_time >= self.timeout_seconds:
            self._fsm.transition(Event.OCCLUSION_TIMEOUT)

    def _update_times(self) -> None:
        if self.state == State.IDLE:
            self._elapsed_time = 0
            self._occluded_time = 0
            return

        self._elapsed_time += self.resolution

        if self.state in [State.DETECTED, State.ALARM]:
            self._occluded_time = 0
        elif self.state in [State.OCCLUDED, State.ARMED]:
            self._occluded_time += self.resolution

    @property
    def state(self) -> str:
        return self._fsm.state

    @property
    def elapsed_time(self) -> float:
        return self._elapsed_time

    @property
    def occluded_time(self) -> float:
        return self._occluded_time

    @property
    def time_to_alert(self) -> float:
        return max(0, self.alert_after_seconds - self._elapsed_time)

    @property
    def time_to_reset(self) -> float:
        if self._fsm.state in [State.OCCLUDED, State.ARMED]:
            return max(0, self.timeout_seconds - self._occluded_time)
        return float(self.timeout_seconds)
