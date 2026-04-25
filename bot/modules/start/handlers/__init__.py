from .command import router as command_router
from .callbacks import router as callbacks_router
from aiogram import Router


router = Router()
router.include_routers(command_router, 
                       callbacks_router
                       )


__all__ = ["router"]