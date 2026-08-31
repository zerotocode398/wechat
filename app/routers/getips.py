from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from app.dependencies import get_config
from app.config import Config
from app.log import logger, WeLog
from app.icode import CustomException
from app.api.getips import ips_list

router = APIRouter(prefix="/qywx", tags=["qywx_getips"])


@WeLog
@router.get("/getips")
async def get_out_ip_list(config: Config = Depends(get_config)):
    try:
        ip_list = ips_list(config)
    except CustomException as e:
        return JSONResponse(status_code=400, content={"msg": str(e)})
    return PlainTextResponse("\n".join(ip_list) + "\n")
