import requests
from typing import List, Dict, Optional, Tuple
from app.log import logger
from app.config import Config


class Alertmanager:
    def __init__(self, config: Config):
        self.config = config
        self.url = config.alertmanager.url
        self.timeout = config.alertmanager.timeout
        self.auth = self.basic_auth

    @property
    def basic_auth(self):
        auth_cfg = self.config.alertmanager.auth
        if auth_cfg and str(auth_cfg.get("enabled", "")).lower() in (
            "true",
            "1",
        ):
            return (auth_cfg.username, auth_cfg.password)
        return None

    @property
    def probe(self) -> Tuple[bool, Optional[str]]:
        try:
            response = requests.get(
                f"{self.url.rstrip('/')}/-/healthy",
                timeout=2,
                auth=self.auth,
            )
            if response.status_code == 200:
                return True, None
            return (
                False,
                f"check alertmanager health failed, status_code={response.status_code}",
            )
        except requests.Timeout:
            return (
                False,
                f"check alertmanager health timeout(2s), please check network or service status.",
            )
        except requests.RequestException as e:
            return (
                False,
                f"check alertmanager health failed, please check network or service status.",
            )

    def create_silence(
        self,
        matchers: List[Dict],
        starts_at: str,
        ends_at: str,
        created_by: str,
        comment: str,
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:

        url = f"{self.url.rstrip('/')}/api/v2/silences"

        payload = {
            "matchers": matchers,
            "startsAt": starts_at,
            "endsAt": ends_at,
            "createdBy": created_by or "wealert",
            "comment": comment or "",
        }
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                auth=self.auth,
                headers={"Content-Type": "application/json"},
            )

            body_text = (response.text or "")[:500]
            try:
                result = response.json() if response.content else {}
            except ValueError:
                logger.error(
                    f"alertmanager create silence failed: status={response.status_code}, "
                    f"non-json body={body_text}"
                )
                return (
                    False,
                    f"alertmanager response non-json (HTTP {response.status_code})",
                )

            logger.info(
                f"alertmanager create silence success: status={response.status_code}, "
                f"result={result}"
            )

            if response.status_code != 200:
                err = (
                    result.get("message")
                    or result.get("error")
                    or body_text
                    or f"HTTP {response.status_code}"
                )
                return False, f"alertmanager create silence failed: {err}"

            if not isinstance(result, dict):
                return False, "alertmanager response non-json"

            silence_id = result.get("silenceID") or result.get("silenceId")
            if not silence_id:
                logger.warning(
                    f"alertmanager 200 but return silenceID is empty: result={result}"
                )
                return False, "alertmanager return silenceID is empty"

            return True, None
        except requests.Timeout:
            logger.error("alertmanager create silence timeout")
            return False, "alertmanager create silence timeout"
        except requests.RequestException as e:
            logger.error(f"alertmanager create silence failed: {e}")
            return False, f"alertmanager create silence failed: {e}"
        except Exception as e:
            logger.error(f"alertmanager create silence failed: {e}")
            return False, f"alertmanager create silence failed: {e}"
