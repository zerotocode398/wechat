from app.log import logger, WeLog
from app.config import Config
from app.client.wechat import Wechat
from typing import Optional


@WeLog
def ips_list(config: Config, timeout: int = 2) -> Optional[list]:
    wechat = Wechat(config)
    try:
        access_token = wechat.get_access_token(timeout=timeout)
    except Exception:
        logger.exception("get access token failed")
        return

    return wechat.ips(access_token, timeout=timeout)
