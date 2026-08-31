from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta

from app.card.silence_durations import (
    DEFAULT_DURATION_OPTIONS,
    DEFAULT_DURATION_DELTAS,
    DEFAULT_DURATION_DISPLAYS,
    parse_durations_config,
)
from app.card.silence_reason import DEFAULT_REASON_OPTIONS
from app.card.silence_scopes import parse_scopes_config, DEFAULT_SCOPE_OPTIONS


def build_silence_structures(
    durations_raw, reasons_raw: list, scopes_raw: list
) -> Dict[str, list]:

    # silence durations
    if durations_raw and isinstance(durations_raw, (dict, list)):
        duration_options, duration_deltas, duration_displays = parse_durations_config(
            durations_raw
        )
    else:
        duration_options = DEFAULT_DURATION_OPTIONS
        duration_deltas = DEFAULT_DURATION_DELTAS
        duration_displays = DEFAULT_DURATION_DISPLAYS

    # silence reasons
    if reasons_raw and isinstance(reasons_raw, list):
        reason_options = [{"id": r, "text": r} for r in reasons_raw]
    else:

        reason_options = DEFAULT_REASON_OPTIONS

    # silence scopes
    if scopes_raw and isinstance(scopes_raw, list):
        scope_options = parse_scopes_config(scopes_raw)
    else:
        scope_options = DEFAULT_SCOPE_OPTIONS

    return {
        "duration_options": duration_options,
        "duration_deltas": duration_deltas,
        "duration_displays": duration_displays,
        "reason_options": reason_options,
        "scope_options": scope_options,
    }


def silence_entry_card(alert_id: str, alert_title: str, alert_details: str) -> Dict:
    tc = {
        "card_type": "button_interaction",
        "task_id": f"silence_{alert_id}",
        "main_title": {
            "title": alert_title,
            "desc": "",
        },
        "button_list": [
            {
                "text": "🔕 静默告警",
                "style": 1,
                "key": f"silence:{alert_id}",
            }
        ],
    }
    tc["sub_title_text"] = alert_details

    return {"msgtype": "template_card", "template_card": tc}


def silence_confirm_entry_card(alert_id: str) -> Dict:
    return {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "button_interaction",
            "main_title": {
                "title": "🔕 静默告警",
                "desc": f"告警 id: {alert_id}",
            },
            "sub_title_text": "",
            "button_list": [
                {
                    "text": "继续静默",
                    "style": 1,
                    "key": f"silence_continue:{alert_id}",
                },
                {
                    "text": "取消返回",
                    "style": 2,
                    "key": f"silence_back:{alert_id}",
                },
            ],
        },
    }


def silence_select_card(alert_id: str, reason_options, duration_options, scope_options):
    # 企微 multiple_interaction：select_list 最多 3 个
    scope_option_list = [
        {"id": s["id"], "text": s["text"]} for s in (scope_options or [])
    ]
    duration_options = (duration_options or [])[:10]
    reason_options = (reason_options or [])[:10]
    scope_option_list = scope_option_list[:10]

    return {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "multiple_interaction",
            "main_title": {
                "title": "🔕 静默告警",
                "desc": "请选择静默时长、原因和范围",
            },
            "select_list": [
                {
                    "question_key": "silence_duration",
                    "title": "时长",
                    "selected_id": (
                        duration_options[0]["id"] if duration_options else "2h"
                    ),
                    "option_list": duration_options,
                },
                {
                    "question_key": "silence_reason",
                    "title": "原因",
                    "selected_id": (
                        reason_options[0]["id"] if reason_options else "其他"
                    ),
                    "option_list": reason_options,
                },
                {
                    "question_key": "silence_scope",
                    "title": "范围",
                    "selected_id": (
                        scope_option_list[0]["id"]
                        if scope_option_list
                        else "this_alert"
                    ),
                    "option_list": scope_option_list,
                },
            ],
            "submit_button": {
                "text": "确认静默",
                "key": f"silence_confirm:{alert_id}",
            },
        },
    }


def compute_ends_at(
    duration_part: str,
    now: datetime,
    duration_deltas: Optional[Dict[str, timedelta]] = None,
) -> datetime:

    if duration_deltas is None:
        duration_deltas = DEFAULT_DURATION_DELTAS

    if duration_part in duration_deltas:
        ends_at = now + duration_deltas[duration_part]
    else:
        ends_at = now + timedelta(hours=2)

    if ends_at <= now:
        ends_at = now + timedelta(minutes=30)
    return ends_at


def card_to_update_xml(card: Dict) -> str:
    # convert a card dict to qywx update-template-card XML string
    tc = card.get("template_card", card)
    card_type = tc.get("card_type", "button_interaction")

    parts = []
    parts.append(f"<CardType><![CDATA[{card_type}]]></CardType>")

    main_title = tc.get("main_title", {})
    if main_title:
        parts.append(
            "<MainTitle>"
            f"<Title><![CDATA[{main_title.get('title', '')}]]></Title>"
            f"<Desc><![CDATA[{main_title.get('desc', '')}]]></Desc>"
            "</MainTitle>"
        )

    sub_title = tc.get("sub_title_text", "")
    if sub_title:
        parts.append(f"<SubTitleText><![CDATA[{sub_title}]]></SubTitleText>")

    quote_area = tc.get("quote_area")
    if quote_area:
        qa = (
            "<QuoteArea>"
            f"<Type>{quote_area.get('type', 0)}</Type>"
            f"<Title><![CDATA[{quote_area.get('title', '')}]]></Title>"
            f"<QuoteText><![CDATA[{quote_area.get('quote_text', '')}]]></QuoteText>"
        )
        if quote_area.get("url"):
            qa += f"<Url><![CDATA[{quote_area['url']}]]></Url>"
        qa += "</QuoteArea>"
        parts.append(qa)

    horizontal = tc.get("horizontal_content_list")
    if horizontal:
        for item in horizontal:
            hc = (
                "<HorizontalContentList>"
                f"<Keyname><![CDATA[{item.get('keyname', '')}]]></Keyname>"
                f"<Value><![CDATA[{item.get('value', '')}]]></Value>"
            )
            if item.get("type"):
                hc += f"<Type>{item['type']}</Type>"
            if item.get("url"):
                hc += f"<Url><![CDATA[{item['url']}]]></Url>"
            hc += "</HorizontalContentList>"
            parts.append(hc)

    button_selection = tc.get("button_selection")
    if button_selection:
        bs_xml = (
            "<ButtonSelection>"
            f"<QuestionKey><![CDATA[{button_selection.get('question_key', '')}]]></QuestionKey>"
            f"<Title><![CDATA[{button_selection.get('title', '')}]]></Title>"
            f"<SelectedId><![CDATA[{button_selection.get('selected_id', '')}]]></SelectedId>"
        )
        for opt in button_selection.get("option_list", []):
            bs_xml += (
                "<OptionList>"
                f"<Id><![CDATA[{opt['id']}]]></Id>"
                f"<Text><![CDATA[{opt['text']}]]></Text>"
                "</OptionList>"
            )
        bs_xml += "</ButtonSelection>"
        parts.append(bs_xml)

    select_list = tc.get("select_list")
    if select_list:
        for sl in select_list[:3]:
            sl_xml = (
                "<SelectList>"
                f"<QuestionKey><![CDATA[{sl.get('question_key', '')}]]></QuestionKey>"
                f"<Title><![CDATA[{sl.get('title', '')}]]></Title>"
                f"<SelectedId><![CDATA[{sl.get('selected_id', '')}]]></SelectedId>"
            )
            for opt in (sl.get("option_list") or [])[:10]:
                sl_xml += (
                    "<OptionList>"
                    f"<Id><![CDATA[{opt['id']}]]></Id>"
                    f"<Text><![CDATA[{opt['text']}]]></Text>"
                    "</OptionList>"
                )
            sl_xml += "</SelectList>"
            parts.append(sl_xml)

    submit_button = tc.get("submit_button")
    if submit_button:
        parts.append(
            "<SubmitButton>"
            f"<Text><![CDATA[{submit_button.get('text', '')}]]></Text>"
            f"<Key><![CDATA[{submit_button.get('key', '')}]]></Key>"
            "</SubmitButton>"
        )

    button_list = tc.get("button_list")
    if button_list:
        for btn in button_list[:6]:
            btn_xml = (
                "<ButtonList>"
                f"<Text><![CDATA[{btn['text']}]]></Text>"
                f"<Style>{btn.get('style', 1)}</Style>"
            )
            key = btn.get("key")
            if key:
                btn_xml += f"<Key><![CDATA[{key}]]></Key>"
            btn_xml += "</ButtonList>"
            parts.append(btn_xml)

    card_action = tc.get("card_action")
    if card_action:
        ca_xml = "<CardAction>"
        ca_xml += f"<Type>{card_action.get('type', 0)}</Type>"
        url = card_action.get("url")
        if url:
            ca_xml += f"<Url><![CDATA[{url}]]></Url>"
        appid = card_action.get("appid")
        if appid:
            ca_xml += f"<AppId><![CDATA[{appid}]]></AppId>"
        pagepath = card_action.get("pagepath")
        if pagepath:
            ca_xml += f"<PagePath><![CDATA[{pagepath}]]></PagePath>"
        ca_xml += "</CardAction>"
        parts.append(ca_xml)

    replace_text = tc.get("replace_text")
    if replace_text:
        parts.append(f"<ReplaceText><![CDATA[{replace_text}]]></ReplaceText>")

    return "".join(parts)
