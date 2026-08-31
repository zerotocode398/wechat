# Reference: https://developer.work.weixin.qq.com/document/path/90236#%E6%96%87%E6%9C%AC%E6%B6%88%E6%81%AF
import json
import time
import uuid

from typing import Optional

from app.client.wechat import Wechat
from app.config import Config
from app.log import logger, WeLog
from app.card.silence import silence_entry_card
from app.card.resolved import resolved_entry_card
from app.database import execute, fetch_one
from datetime import datetime
from zoneinfo import ZoneInfo

# default silence action ttl seconds is 30 minutes
SILENCE_ACTION_TTL_SECONDS = 30 * 60


# save alert details to database
@WeLog
def save_alert_details(alert_id: str, alert_title: str, details: str, alert: dict):

    data = {"sub_title_text": details}
    data["alerts"] = [alert]
    data["alert_title"] = alert_title

    execute(
        """
        INSERT OR REPLACE INTO alert_receive (alert_id, data) VALUES (?, ?)
        """,
        (alert_id, json.dumps(data, ensure_ascii=False)),
    )


# load alert payload from database
@WeLog
def load_alert_payload(alert_id: str) -> Optional[dict]:

    row = fetch_one(
        """
        SELECT data FROM alert_receive
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    if not row or not row["data"]:
        return None

    try:
        data = json.loads(row["data"])
    except (TypeError, json.JSONDecodeError):
        logger.error(f"load alert payload failed: {row['data']}")
        return None
    if isinstance(data, dict) and "alerts" not in data and "sub_title_text" in data:
        return None
    return data if isinstance(data, dict) else None


# load alert details from database
@WeLog
def load_alert_details(alert_id: str) -> str:

    payload = load_alert_payload(alert_id)
    if payload:
        alerts = payload.get("alerts")
        if alerts:
            return _build_alert_details(alerts[0])
        logger.error(f"load alert details from payload failed: {payload}")
        return ""

    row = fetch_one(
        """
        SELECT data FROM alert_receive
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    if not row:
        return ""
    try:
        data = json.loads(row["data"])
        return data.get("sub_title_text")
    except (TypeError, json.JSONDecodeError):
        logger.error(f"load alert details from database failed: {row['data']}")
        return ""


# load alert card view from database
@WeLog
def load_alert_card_view(alert_id: str) -> dict:

    payload = load_alert_payload(alert_id)

    if payload:
        alerts = payload.get("alerts")
        if alerts:
            return {
                "alert_details": _build_alert_details(alerts[0]),
            }

    # when alert details is not found in payload, load from database
    return {
        "alert_details": load_alert_details(alert_id),
    }


# load alert receive time from database
@WeLog
def load_alert_receive_time(alert_id: str) -> Optional[float]:
    row = fetch_one(
        """
        SELECT receive_time FROM alert_receive
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    if not row or not row["receive_time"]:
        return None

    return time.mktime(time.strptime(str(row["receive_time"]), "%Y-%m-%d %H:%M:%S"))


# check if silence action is expired
@WeLog
def is_silence_action_expired(
    alert_id: str, ttl: int, now_ts: Optional[float] = None
) -> bool:
    # check if silence action is expired
    # True is expired
    # False is not expired
    receive_ts = load_alert_receive_time(alert_id)

    if receive_ts is None:
        return True

    if now_ts is None:
        now_ts = time.time()

    return (now_ts - receive_ts) > ttl


# save silence info to database
@WeLog
def save_silence_info(
    alert_id: str, duration_display: str, reason: str, from_user: str
) -> None:
    execute(
        """
        INSERT INTO silence_info (alert_id, duration_display, reason, from_user)
        VALUES (?, ?, ?, ?)
        """,
        (alert_id, duration_display, reason, from_user),
    )


# save response_code for card update
@WeLog
def save_response_code(alert_id: str, response_code: str) -> None:
    execute(
        """
        INSERT OR REPLACE INTO alert_response_code (alert_id, response_code)
        VALUES (?, ?)
        """,
        (alert_id, response_code),
    )


# load response_code for card update
@WeLog
def load_response_code(alert_id: str) -> Optional[str]:
    row = fetch_one(
        """
        SELECT response_code FROM alert_response_code
        WHERE alert_id = ?
        """,
        (alert_id,),
    )
    return row["response_code"] if row else None


# load silence info from database
@WeLog
def load_silence_info(alert_id: str) -> Optional[dict]:
    row = fetch_one(
        """
        SELECT duration_display, reason, from_user FROM silence_info
        WHERE alert_id = ?
        ORDER BY id DESC LIMIT 1
        """,
        (alert_id,),
    )

    if not row:
        return None

    return dict(row)


# build recipient fields from config
@WeLog
def _recipient_fields(config: Config) -> dict:
    return {
        "touser": (
            "" if not config.qywx.touser else "|".join(config.qywx.touser.split(","))
        ),
        "toparty": (
            "" if not config.qywx.toparty else "|".join(config.qywx.toparty.split(","))
        ),
        "totag": (
            "" if not config.qywx.totag else "|".join(config.qywx.totag.split(","))
        ),
    }


# build alert details from annotations
@WeLog
def _build_alert_details(alert: dict) -> str:

    lines = []

    annotations = alert.get("annotations", {})
    starts_at = alert.get("startsAt")
    dt = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        dt = dt.astimezone(ZoneInfo("Asia/Shanghai"))

    for key, value in annotations.items():
        if value:
            lines.append(f"{key}: {value}")

    lines.append(f"告警时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(lines)


# build message base from config
@WeLog
def _message_base(config: Config) -> dict:
    return {
        "agentid": config.qywx.agentid,
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800,
    }


# send message to qywx
@WeLog
def _send(
    wechat: Wechat, access_token: str, timeout: int, data: dict, ctx: str = ""
) -> dict:
    result = wechat.send_message(access_token, timeout, data)
    logger.info(
        f"send success: {ctx}, result={result}"
        if ctx
        else f"send success: result={result}"
    )
    return result


@WeLog
def send_alert(config: Config, payload: dict, msgtype: str = "card", timeout: int = 10):
    wechat = Wechat(config)
    try:
        access_token = wechat.get_access_token(timeout=timeout)
    except Exception:
        logger.exception("get access token failed")
        return

    recipients = _recipient_fields(config)

    if not any(recipients.values()):
        logger.exception("all recipient fields are empty: touser, toparty, totag.")
        return

    if msgtype == "card":

        for alert in payload.get("alerts", []):
            alert_id, alert_title, alert_details = (
                str(uuid.uuid4().hex),
                config.alertmanager.alert_title,
                _build_alert_details(alert),
            )

            save_alert_details(alert_id, alert_title, alert_details, alert)
            logger.info(
                f"save alert details: alert_id={alert_id}, alert_title={alert_title}, alert_details={alert_details}"
            )

            status = alert.get("status", "").lower()
            if status == "resolved":
                data = resolved_entry_card(
                    alert_id,
                    config.alertmanager.resolve_title,
                    alert_details,
                    alert,
                )
            else:
                data = silence_entry_card(alert_id, alert_title, alert_details)
            data.update(_message_base(config))
            data.update(recipients)
            try:
                result = _send(
                    wechat,
                    access_token,
                    timeout,
                    data,
                    f"card alert_id={alert_id} alert_title={alert_title} status={status}",
                )
                response_code = result.get("response_code", "")
                logger.info(
                    f"send alert response_code: alert_id={alert_id}, "
                    f"response_code={response_code[:30] if response_code else 'EMPTY'}..."
                )
                if response_code and status != "resolved":
                    save_response_code(alert_id, response_code)
            except Exception:
                logger.error(f"send failed: {alert_id} {alert_title} {status}")

    elif msgtype == "text":
        content = payload.get("content")
        if content:
            text_content = content
        else:
            parts = [_build_alert_details(a) for a in payload.get("alerts", [])]
            text_content = "\n---\n".join(parts) if parts else ""

        if text_content:
            data = {
                **_message_base(config),
                "msgtype": "text",
                "text": {"content": text_content},
                **recipients,
            }
            data["touser"] = payload.get("touser") or recipients["touser"]
            data["toparty"] = payload.get("toparty") or recipients["toparty"]
            data["totag"] = payload.get("totag") or recipients["totag"]
            try:
                _send(wechat, access_token, timeout, data, "text")
            except Exception:
                logger.error(f"send failed: text {text_content}")
