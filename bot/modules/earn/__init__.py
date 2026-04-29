from .handlers.callbacks import router as callbacks_router
from .handlers.messages import router as messages_router
from aiogram import Router


router = Router()
router.include_routers(callbacks_router, messages_router)


__all__ = [
    "router"
]