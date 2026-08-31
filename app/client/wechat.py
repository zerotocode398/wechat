import requests
import json
from app.log import WeLog, logger
from app.config import Config
from app.icode import CustomException
from app.icode import qywx_error_code, unknown_error
from app.db.qywx_token import db_get_token, db_save_token
from typing import Union


class Wechat:
    def __init__(self, config: Config):
        self.agent_id = config.qywx.agentid
        self.corp_id = config.qywx.corpid
        self.corpsecret = config.qywx.corpsecret
        self.url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?"

    @WeLog
    def verify_access_token_is_valid(self) -> Union[str, None]:
        access_token = db_get_token(self.corp_id, self.corpsecret)
        if access_token is None:
            return None
        return access_token

    @WeLog
    def get_access_token(self, timeout: int) -> str:
        if self.verify_access_token_is_valid() is None:
            logger.info("access token is expired or not found, ready to refresh it.")
            access_token, expires_in = self.refresh_access_token(timeout=timeout)
            db_save_token(
                self.corp_id,
                self.corpsecret,
                access_token,
                expires_in,
            )
            logger.info(f"access token is refreshed and saved to database.")
            return access_token
        return self.verify_access_token_is_valid()

    @WeLog
    def refresh_access_token(self, timeout: int) -> tuple:
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.corpsecret,
        }
        response = json.loads(
            requests.get(url=self.url, params=params, timeout=timeout).text
        )
        if response["errcode"] in qywx_error_code:
            raise CustomException(
                code=response["errcode"],
            )

        elif response["errcode"] not in qywx_error_code and response["errcode"] != 0:
            raise CustomException(
                code=unknown_error,
                msg=response["errmsg"],
            )

        return response["access_token"], response["expires_in"]

    @WeLog
    def send_message(self, access_token: str, timeout: int, data: dict) -> dict:
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        response = json.loads(
            requests.post(
                url=url,
                json=data,
                timeout=timeout,
            ).text
        )
        if response["errcode"] in qywx_error_code:
            raise CustomException(
                code=response["errcode"],
            )

        elif response["errcode"] not in qywx_error_code and response["errcode"] != 0:
            raise CustomException(
                code=unknown_error,
                msg=response["errmsg"],
            )

        return response

    @WeLog
    def update_template_card(
        self, access_token: str, timeout: int, response_code: str, card: dict
    ) -> dict:
        url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/update_template_card"
            f"?access_token={access_token}"
        )
        tc = card.get("template_card", card)
        data = {
            "atall": 1,
            "response_code": response_code,
            "agentid": int(self.agent_id),
            "template_card": tc,
        }
        logger.info(
            f"update_template_card request: {json.dumps(data, ensure_ascii=False)}"
        )
        response = json.loads(
            requests.post(
                url=url,
                json=data,
                timeout=timeout,
            ).text
        )
        if response["errcode"] in qywx_error_code:
            raise CustomException(
                code=response["errcode"],
            )
        elif response["errcode"] not in qywx_error_code and response["errcode"] != 0:
            raise CustomException(
                code=unknown_error,
                msg=response["errmsg"],
            )
        return response

    @WeLog
    def ips(self, access_token: str, timeout: int) -> list:
        url = f"https://qyapi.weixin.qq.com/cgi-bin/get_api_domain_ip?access_token={access_token}"
        response = json.loads(requests.get(url=url, timeout=timeout).text)

        if response["errcode"] == 0 and response["errmsg"] == "ok":
            return response["ip_list"]

        if response["errcode"] in qywx_error_code:
            raise CustomException(code=response["errcode"])

        raise CustomException(code=unknown_error, msg=response["errmsg"])
