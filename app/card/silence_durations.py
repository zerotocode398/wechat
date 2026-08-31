from typing import Dict, List, Tuple, Union
from datetime import timedelta


DEFAULT_DURATION_OPTIONS = [
    {"id": "2h", "text": "2小时"},
    {"id": "4h", "text": "4小时"},
]

# default duration deltas
DEFAULT_DURATION_DELTAS = {"2h": timedelta(hours=2), "4h": timedelta(hours=4)}
DEFAULT_DURATION_DISPLAYS = {"2h": "2小时", "4h": "4小时"}


_UNIT_MAP = {
    "h": "hours",
    "d": "days",
    "m": "minutes",
}

_DISPLAY_UNIT_MAP = {
    "h": "小时",
    "d": "天",
    "m": "分钟",
}


def _value_to_display(value: str) -> str:
    num = value[:-1]
    unit = value[-1]
    unit_display = _DISPLAY_UNIT_MAP.get(unit, unit)
    return f"{num}{unit_display}"


# parse durations config, use to card silence durations select options
def parse_durations_config(durations_raw: Union[dict, list]):
    options = []
    deltas = {}
    displays = {}

    if isinstance(durations_raw, dict):
        for display, value in durations_raw.items():
            options.append({"id": value, "text": display})
            displays[value] = display

            num = int(value[:-1])
            unit = value[-1]
            kwarg = _UNIT_MAP.get(unit, "hours")
            deltas[value] = timedelta(**{kwarg: num})
    else:
        for value in durations_raw:
            display = _value_to_display(value)
            options.append({"id": value, "text": display})
            displays[value] = display

            num = int(value[:-1])
            unit = value[-1]
            kwarg = _UNIT_MAP.get(unit, "hours")
            deltas[value] = timedelta(**{kwarg: num})

    return options, deltas, displays
