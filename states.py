from lib import StateMachine


class State:
    IDLE = "idle"
    DETECTED = "detected"
    ALARM = "alarm"
    ARMED = "armed"
    OCCLUDED = "occluded"


class Event:
    TARGET_IN_RANGE = "target in range"
    TARGET_OUT_OF_RANGE = "target out of range"
    ALERT_TIME_REACHED = "alert time reached"
    OCCLUSION_TIMEOUT = "occlusion timeout"


TRANSITIONS = {
    State.IDLE: {
        Event.TARGET_IN_RANGE: State.DETECTED,
    },
    State.DETECTED: {
        Event.TARGET_OUT_OF_RANGE: State.OCCLUDED,
        Event.ALERT_TIME_REACHED: State.ALARM,
    },
    State.OCCLUDED: {
        Event.TARGET_IN_RANGE: State.DETECTED,
        Event.OCCLUSION_TIMEOUT: State.IDLE,
    },
    State.ALARM: {
        Event.TARGET_OUT_OF_RANGE: State.ARMED,
    },
    State.ARMED: {
        Event.TARGET_IN_RANGE: State.ALARM,
        Event.OCCLUSION_TIMEOUT: State.IDLE,
    },
}


def create_state_machine(
    transitions: dict[str, dict[str, str]] | None = None,
) -> StateMachine:
    if transitions is None:
        transitions = TRANSITIONS

    return StateMachine(
        initial_state=State.IDLE,
        transitions=transitions,
    )
