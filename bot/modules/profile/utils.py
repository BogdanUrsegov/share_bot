from bot.database.utils import get_user_stats


def calculate_price(count: int) -> tuple[float, float]:

    # базовая цена
    total_rub = count * 1.5

    # скидки
    if count >= 1000:
        discount = 0.20
    elif count >= 500:
        discount = 0.15
    elif count >= 100:
        discount = 0.10
    elif count >= 50:
        discount = 0.05
    else:
        discount = 0.0

    final_rub = total_rub * (1 - discount)
    
    return round(final_rub, 2), discount


async def show_profile(user_id: int):
    stats = await get_user_stats(user_id)

    photo_count = stats["photo_count"]
    video_count = stats["video_count"]
    balance = stats["balance"]

    return (
        "<b>👤 Профиль</b>\n\n"
        f"🖼 {photo_count} | 🎥 {video_count}\n\n"
        f"💳 <b>Баланс: {balance}</b> 💎"
    )