from fastapi import APIRouter, Request, Depends, Query
from app.dependencies import get_config
from app.api.callback import SignCallback, CallbackEvent, ReplyMsg
from app.config import Config
from fastapi.responses import JSONResponse, PlainTextResponse
from app.icode import CustomException
from app.log import WeLog, logger

router = APIRouter(prefix="/qywx", tags=["qywx_callback"])


@router.get("/callback")
@WeLog
async def verify_url(
    msg_signature: str = Query(..., description="企业微信加密签名"),
    timestamp: str = Query(..., description="时间戳"),
    nonce: str = Query(..., description="随机数"),
    echostr: str = Query(..., description="加密的随机字符串"),
    config: Config = Depends(get_config),
):
    args = {
        "signature": msg_signature,
        "timestamp": timestamp,
        "nonce": nonce,
        "echo": echostr,
    }

    logger.info(f"qywx callback verify: {args}.")
    impl_callback = SignCallback(config, **args)

    try:
        if not impl_callback.verify_signature:
            return JSONResponse(
                status_code=400,
                content={"code": 400, "msg": "signature verification failed"},
            )
        xml = impl_callback.verify_corpid
    except CustomException as e:
        return JSONResponse(
            status_code=400,
            content={"msg": str(e)},
        )

    logger.info("qywx callback verify success.")
    return PlainTextResponse(content=xml.decode("utf-8"))


@router.post("/callback")
@WeLog
async def receive_event(
    request: Request,
    msg_signature: str = Query(..., description="企业微信加密签名"),
    timestamp: str = Query(..., description="时间戳"),
    nonce: str = Query(..., description="随机数"),
    config: Config = Depends(get_config),
):
    args = {
        "signature": msg_signature,
        "timestamp": timestamp,
        "nonce": nonce,
        "body": await request.body(),
    }

    logger.info(f"qywx callback received: {args['body'].decode('utf-8')}")
    impl_callback = CallbackEvent(config, **args)

    try:
        reply_xml = impl_callback.reply_content
    except CustomException as e:
        return JSONResponse(
            status_code=400,
            content={"msg": str(e)},
        )

    impl_replyBody = ReplyMsg(config)

    try:
        encrypted_reply = impl_replyBody.reply_encrypt(reply_xml)
        decrypted_reply_text = encrypted_reply.decode("utf-8")
        reply_signature = impl_replyBody.reply_signature(
            args["nonce"], decrypted_reply_text
        )
        reply_body = impl_replyBody.reply_body(
            decrypted_reply_text, reply_signature, args["nonce"]
        )
    except CustomException as e:
        return JSONResponse(
            status_code=400,
            content={"msg": str(e)},
        )

    logger.info("qywx callback reply success.")
    return PlainTextResponse(content=reply_body)
