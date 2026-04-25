from bot.database.models import PaymentRecord, User, Media
from bot.database.session import AsyncSessionLocal
from sqlalchemy import func, select

async def all_info() -> dict:
    async with AsyncSessionLocal() as session:
        # 1. Пользователи
        total_users = await session.scalar(select(func.count(User.id))) or 0

        # 2. Заказы
        total_orders = await session.scalar(select(func.count(PaymentRecord.id))) or 0

        # 3. Оплаченные заказы
        paid_count, paid_sum = (await session.execute(
            select(
                func.count(PaymentRecord.id),
                func.coalesce(func.sum(PaymentRecord.amount), 0)
            ).where(PaymentRecord.status == 'paid')
        )).one()

        # 4. Медиафайлы (фото и видео)
        photo_count, video_count = (await session.execute(
            select(
                func.count().filter(Media.type == "photo"),
                func.count().filter(Media.type == "video")
            )
        )).one()

        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "paid_orders_count": paid_count,
            "paid_orders_sum": float(paid_sum),
            "total_photos": photo_count,
            "total_videos": video_count
        }