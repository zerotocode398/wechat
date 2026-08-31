from fastapi import APIRouter

from . import callback
from . import alert
from . import getips

router = APIRouter()

router.include_router(callback.router)
router.include_router(alert.router)
router.include_router(getips.router)
