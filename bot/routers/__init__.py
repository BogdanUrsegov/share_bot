from aiogram import Router
from bot.modules.start import router as start_router
from bot.modules.admin import router as admin_router
from bot.modules.show import router as show_router
from bot.modules.profile import router as profile_router

router = Router()
router.include_routers(
                        start_router,
                        admin_router,
                        show_router,
                        profile_router
                    )


__all__ = ["router"]