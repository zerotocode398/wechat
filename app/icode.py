# const
app_name = "wealert"
app_version = "1.0.0"

# custom error code
config_file_not_found: int = 10000
config_file_parse_error: int = 10001
base64_aeskey_error: int = 10002
delete_random_error: int = 10003
decrypt_echostr_error: int = 10004
corp_invalid_error: int = 10005
encrypt_request_signature_error: int = 10006
encrypt_reply_msg_error: int = 10007
extract_request_body_error: int = 10008


# wechat error code
access_token_expired_or_invalid: list = [42001, 40014]
corp_invalid: list = [40013, 40001]
ip_access_denied: list = [60020]
invalid_message_type: list = [40008]
card_taskid_invalid: list = [42014]
qywx_error_code = (
    access_token_expired_or_invalid
    + corp_invalid
    # + ip_access_denied
    + invalid_message_type
    + card_taskid_invalid
)

unknown_error: int = 99999
success: int = 0

code_description = {
    0: "Success",
    10000: "no such file or directory",
    10001: "config body invalid",
    10002: "base64 aeskey error",
    42001: "access token expired, please refresh it",
    40014: "access token invalid, please check the access token is valid",
    40013: "corp invalid, please check the corp_id is valid",
    40001: "corpsecret invalid, please check the corpsecret is valid",
    42014: "card taskid has existed or empty or exceed max len , please check the task id is valid",
    60020: "not safety ip, please check output ip is in the whitelist",
    99999: "unknown error",
}


class CustomException(Exception):
    def __init__(self, code: int, msg=None):
        """
        Args:
            code: 异常码
            msg: 异常详细信息
        """
        self.code = code
        self.msg = msg
        self.description = code_description.get(code, "unknown error")

    def __str__(self):
        if self.msg:
            return f"code: {self.code}, " f"error: {self.msg}"

        return f"code: {self.code}, " f"description: {self.description}"
