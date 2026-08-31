import time
from typing import Optional, Dict

from app.database import fetch_one, fetch_all, execute
from app.log import logger


SESSION_TTL_SECONDS = 30 * 60


def create_session(
    alert_id: str,
    duration_part: str,
    duration_display: str,
    origin: str,
    from_user: str,
) -> int:
    expire_pending_sessions(from_user)

    execute(
        """
        INSERT INTO silence_session
        (alert_id, duration_part, duration_display, origin, from_user, status)
        VALUES (?, ?, ?, ?, ?, 'awaiting_reason')
        """,
        (alert_id, duration_part, duration_display, origin, from_user),
    )

    row = fetch_one(
        """
        SELECT id FROM silence_session
        WHERE from_user = ? AND status = 'awaiting_reason'
        ORDER BY id DESC LIMIT 1
        """,
        (from_user,),
    )
    session_id = row["id"] if row else 0
    logger.info(
        f"silence_session created: id={session_id}, alert_id={alert_id}, "
        f"duration={duration_display}, user={from_user}"
    )
    return session_id


def get_pending_session(from_user: str) -> Optional[Dict]:
    expire_pending_sessions(from_user)

    row = fetch_one(
        """
        SELECT id, alert_id, duration_part, duration_display, origin,
               from_user, created_at
        FROM silence_session
        WHERE from_user = ? AND status = 'awaiting_reason'
        ORDER BY id DESC LIMIT 1
        """,
        (from_user,),
    )
    if not row:
        return None

    created_at_str = str(row["created_at"])
    try:
        created_ts = time.mktime(time.strptime(created_at_str, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        created_ts = 0

    if created_ts and (time.time() - created_ts) > SESSION_TTL_SECONDS:
        close_session(row["id"], status="expired")
        return None

    return dict(row)


def close_session(session_id: int, status: str = "closed") -> None:
    execute(
        "UPDATE silence_session SET status = ? WHERE id = ?",
        (status, session_id),
    )


def expire_pending_sessions(from_user: str) -> None:
    """关闭该用户所有超时的待处理会话（>30 分钟未回复）"""
    rows = fetch_all(
        """
        SELECT id, created_at FROM silence_session
        WHERE from_user = ? AND status = 'awaiting_reason'
        ORDER BY id DESC
        """,
        (from_user,),
    )
    if not rows:
        return

    now_ts = time.time()
    for row in rows:
        created_at_str = str(row["created_at"])
        try:
            created_ts = time.mktime(
                time.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            )
        except ValueError:
            continue

        if created_ts and (now_ts - created_ts) > SESSION_TTL_SECONDS:
            close_session(row["id"], status="expired")
