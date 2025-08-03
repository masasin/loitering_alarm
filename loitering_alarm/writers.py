from ucollections import namedtuple

Writer = namedtuple("Writer", ["function", "formatter"])


def _format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02}:{int(seconds):02}"


def serial_formatter(data: dict) -> str:
    return (
        f"Distance: {data['distance']:.1f} cm\n"
        f"State: {data['state']}\n"
        f"Time to alert: {_format_time(data['time_to_alert'])}\n"
        f"Time to reset: {_format_time(data['time_to_reset'])}"
    )


def lcd_formatter(data: dict) -> str:
    return (
        f"{data['distance']:5.1f} {data['state'][:2].upper()}\n"
        f"{_format_time(data['time_to_alert'])} {data['time_to_reset']:02.0f}"
    )


serial_writer = Writer(print, serial_formatter)
