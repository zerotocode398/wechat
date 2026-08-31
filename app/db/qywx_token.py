import time

from app.database import fetch_one, execute
from typing import Union
from app.log import WeLog


@WeLog
def db_get_token(corp_id: str, corpsecret: str) -> Union[str, None]:
    row = fetch_one(
        """
        SELECT access_token, expires_at
        FROM qywx_token
        WHERE corp_id = ? AND corpsecret = ?
        ORDER BY expires_at DESC
        LIMIT 1
        """,
        (
            corp_id,
            corpsecret,
        ),
    )

    if not row:
        return None

    if row["expires_at"] <= int(time.time()):
        return None

    return row["access_token"]


@WeLog
def db_save_token(corp_id: str, corpsecret: str, access_token: str, expires_in: int):

    expires_at = int(time.time()) + expires_in

    execute(
        "DELETE FROM qywx_token WHERE corp_id = ? AND corpsecret = ?",
        (corp_id, corpsecret),
    )

    execute(
        """
        INSERT INTO qywx_token
        (
            corp_id,
            corpsecret,
            access_token,
            expires_at
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?
        )
        """,
        (corp_id, corpsecret, access_token, expires_at),
    )
