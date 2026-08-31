from datetime import datetime, timezone, timedelta
from typing import Dict

CST = timezone(timedelta(hours=8))


def _build_resolved_time(alert: dict) -> str:
    ends_at = alert.get("endsAt", "")
    if ends_at:
        try:
            dt = datetime.fromisoformat(ends_at.replace("Z", "+00:00")).astimezone(CST)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            pass
    return "unknown"


def resolved_entry_card(
    alert_id: str, resolve_title: str, alert_details: str, alert: dict
) -> Dict:
    resolved_time = _build_resolved_time(alert)
    tc = {
        "card_type": "button_interaction",
        "task_id": f"resolved_{alert_id}",
        "main_title": {
            "title": resolve_title,
            "desc": "",
        },
        "button_list": [
            {
                "text": "✅ 已恢复",
                "style": 1,
                "key": f"resolved:{alert_id}",
            }
        ],
    }
    tc["sub_title_text"] = alert_details + f"\n恢复时间: {resolved_time}"

    return {"msgtype": "template_card", "template_card": tc}
