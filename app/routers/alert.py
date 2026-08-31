from enum import Enum

from fastapi import APIRouter, Depends, Query, Body
from app.dependencies import get_config
from app.config import Config
from app.api.alert import send_alert
from fastapi.responses import JSONResponse
from app.log import logger


class MsgType(str, Enum):
    card = "card"
    text = "text"


router = APIRouter(prefix="/qywx", tags=["qywx_alert"])


@router.post("/alert")
async def receive_alert(
    payload: dict = Body(...),
    msgtype: MsgType = Query(default=MsgType.card),
    config: Config = Depends(get_config),
):
    try:
        send_alert(config, payload, msgtype=msgtype.value)
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": str(e)})

    return JSONResponse(status_code=200, content={"code": 200, "msg": "ok"})
