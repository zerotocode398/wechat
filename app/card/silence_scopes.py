from typing import Any, Dict, List, Optional, Tuple


DEFAULT_SCOPE_OPTIONS = [
    {"id": "当前告警", "text": "当前告警"},
]


# parse scopes config
def parse_scopes_config(scopes_raw: list) -> List[Dict]:
    options = []
    for item in scopes_raw:
        scope = {"id": item["text"], "text": item["text"]}
        if "labels" in item:
            scope["labels"] = item["labels"]
        options.append(scope)
    return options


# alert status: firing
def firing_alerts(payload: dict) -> List[dict]:
    return [a for a in payload.get("alerts") if (a.get("status")).lower() == "firing"]


# alert status: resolved
def resolved_alerts(payload: dict) -> List[dict]:
    return [a for a in payload.get("alerts") if (a.get("status")).lower() == "resolved"]


# get label value from payload, ready to use in matcher sets
# return first alert label value
def _first_label_value(payload: dict, label: str) -> Optional[str]:

    for alert in firing_alerts(payload):
        labels = alert.get("labels")
        val = labels.get(label, None)
        return None if val is None else str(val)

    return None


# matcher sets
def _matchers_from_labels(labels: dict) -> List[Dict[str, Any]]:

    return [
        {"name": str(name), "value": str(value), "isRegex": False}
        for name, value in labels.items()
        if value is not None and str(value) != ""
    ]


# build silence matcher sets from scope id
def build_silence_matcher_sets(
    scope_id: str, scopes_config: list, payload: dict
) -> Tuple[List[Dict[str, Any]], Optional[str]]:

    scope = next((item for item in scopes_config if item.get("id") == scope_id), None)
    if scope is None:
        scope = {}

    # resolved alerts don't apply to silence
    firings = firing_alerts(payload)
    if not firings:
        return [], "no firing alerts to silence"

    # label names from scope, ready to use in matcher sets
    label_names = scope.get("labels", [])

    # Wide scope: one or more silences by configured label(s)
    # least one label is required
    if label_names:
        matchers = []
        for name in label_names:
            val = _first_label_value(payload, name)
            if val is None:
                return [], f"label {name} not found, please check the scope config"
            matchers.append({"name": name, "value": val, "isRegex": False})
        return [matchers], None
    else:
        # default scope: filter all labels
        sets = []
        for alert in firings:
            matchers = _matchers_from_labels(alert.get("labels") or {})
            if not matchers:
                continue
            sets.append(matchers)
        return sets, None
