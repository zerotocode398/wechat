from typing import Dict, List, Optional

# default silence reason options
DEFAULT_REASON_OPTIONS = [
    {"id": "人为触发", "text": "人为触发"},
    {"id": "上线/发布", "text": "上线/发布"},
    {"id": "护网/重保", "text": "护网/重保"},
    {"id": "变更/维护", "text": "变更/维护"},
    {"id": "误报", "text": "误报"},
    {"id": "演练", "text": "演练"},
    {"id": "其他", "text": "其他"},
]


# final status card confirmed
def silence_confirmed_card(
    alert_id: str,
    alert_details: str,
    alert_title: str,
    duration_display: str,
    reason: str,
) -> Dict:
    tc: dict = {
        "card_type": "button_interaction",
        "task_id": f"silence_{alert_id}",
        "main_title": {
            "title": f"{alert_title}",
            "desc": f"告警 id: {alert_id}",
        },
        "button_list": [
            {
                "text": "✅ 已静默",
                "style": 1,
                "key": f"silence_done:{alert_id}",
            }
        ],
    }
    silence_meta = ""
    if duration_display and reason:
        silence_meta = f"静默时长：{duration_display}\n静默原因：{reason}"
    elif duration_display:
        silence_meta = f"静默时长：{duration_display}"
    elif reason:
        silence_meta = f"静默原因：{reason}"

    tc["sub_title_text"] = f"{alert_details}\n{silence_meta}"

    return {"msgtype": "template_card", "template_card": tc}


# final failed card
def silence_failed_card(alert_id: str, error: str) -> Dict:
    return {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "button_interaction",
            "main_title": {
                "title": "❌ 静默失败",
                "desc": f"告警 id: {alert_id}",
            },
            "sub_title_text": (
                f"错误信息：{error}\n"
                "请稍后重试或联系管理员。可点击下方按钮返回告警。"
            ),
            "button_list": [
                {
                    "text": "返回告警",
                    "style": 1,
                    "key": f"silence_back:{alert_id}",
                }
            ],
        },
    }


# final expired card
def silence_expired_card(alert_id: str, ttl_minutes: int = 30) -> Dict:
    return {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "button_interaction",
            "main_title": {
                "title": "⏰ 静默已过期",
                "desc": f"告警 id: {alert_id}",
            },
            "sub_title_text": (
                f"告警发出已超过 {ttl_minutes} 分钟，无法操作。\n"
                "请关注新告警或联系管理员处理。"
            ),
            "button_list": [
                {
                    "text": "返回告警",
                    "style": 1,
                    "key": f"silence_back:{alert_id}",
                }
            ],
        },
    }
