from .handlers import router as profile_router
from aiogram import Router


router = Router()
router.include_routers(profile_router)


__all__ = [
    "router"
]