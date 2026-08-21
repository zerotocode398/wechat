# 自定义的错误码都在此包中

# 处理正常响应码
WXSuccess: int = 0

# 企业微信应用无效的 Token
WXErrorInvalidToken: int = 10001

# 校验企业微信消息请求中的字段 msg_signature 与 [token, timestamp, nonce, echostr]加密 失败
WXErrorInvalidSignature: int = 10002

# 企业微信应用无效的 EncodingAESKey
WXErrorInvalidAESKey: int = 10003

# 对 echostr 进行 base64 解码，在使用 AES-CBC 解密过程中失败
WXErrorEncodeEchoStr: int = 10004

# 去除 echostr 中的随机字符串[random(16B) + msg_len(4B) + msg + receiveid]
WXErrorDeleteRandom: int = 10005

# 企业微信无效的 CropID
WXErrorInvalidCropID: int = 10006

# 配置文件解析失败
WXErrorInvalidConfigPath: int = 10007

# 解析企业微信 postdata数据
WXErrorPostXMLData: int = 10008

# 加密企业回复的消息异常
WXErrorEncodeReplyMsg: int = 10009

# 获取企业微信应用AccessToken异常
WXErrorAccessToken: int = 10010

# redis set key err
RedisErrorSetKey: int = 10011

# redis key is None
RedisKeyIsNone: int = 10012

# redis get key ttl err
RedisErrorTTLKey: int = 10013

# redis ping error
RedisErrorConn: int = 10015

# Alarm 未提供 agentid
AlarmErrorAgentId: int = 10016

# Alarm 未提供 secret
AlarmErrorSecret: int = 10017

# Alarm 未提供 receiver
AlarmErrorReceiver: int = 10018

# Alarm receiver 缺少touser、toparty、totag
AlarmErrorToAim: int = 10019

# Alarm touser、toparty、totag 类型错误
AlarmErrorReceiverType: int = 10020

# 不支持的消息格式类型
InvaildMsgType: int = 10021


code_description = {
    0: "成功",
    10001: "无效的 token",
    10002: "msg_signature 未校验通过",
    10003: "无效的 encodingAESKey ",
    10004: "echostr 解密失败",
    10005: "echostr 剔除随机字符串异常",
    10006: "无效的 cropid",
    10007: "配置文件解析异常",
    10008: "解析 postdata 异常",
    10009: "加密企业回复消息异常",
    10010: "获取企业微信应用 AccessToken 异常",
    10011: "Redis 设置 key 异常",
    10012: "Redis 获取 key 的 value 异常",
    10013: "Redis 获取 key 的 ttl 异常",
    10015: "Redis 连接异常",
    10016: "未提供企业微信 agentid",
    10017: "未提供企业微信 secret",
    10018: "未提供企业企业微信接收人",
    10019: "touser 不能为空",
    10020: "多个 touser 以英文逗号分割",
    10021: "不支持的消息类型, msgtype 可选 text | markdown | template_card",
}


class CustomException(Exception):
    def __init__(self, code: int):
        """
        Args:
            code: 异常码
            msg: 异常信息
        """
        self.code = code
        self.code_description = code_description.get(int(code), "Unknown Error")

    def __str__(self) -> str:
        """
        Returns: 异常日志
        """
        return f"code: {self.code}, description: {self.code_description}"


def ResponseBody(code: int):
    response_data = {
        "code": code,
        "message": f"{code_description.get(code, 'Unknown Error')}",
    }
    return response_data
