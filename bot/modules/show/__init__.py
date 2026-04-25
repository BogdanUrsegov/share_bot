from .handlers.callbacks import router as show_callbacks_router
from aiogram import Router


router = Router()
router.include_routers(show_callbacks_router)


__all__ = [
    "router"
]