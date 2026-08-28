import os

from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.database.utils import (
    add_user,
    check_user_agreement,
    delete_user_by_telegram_id,
    user_checker,
)
from bot.database.utils.referrals import (
    get_referral_link_by_name,
    get_referral_stats,
    record_referral_click,
)
from bot.modules.start.states import AgreeTerms
from ..keyboards.inline_keyboards import agree_menu, categories_menu


ADMIN_ID = os.getenv("ADMIN_ID")
param_start = os.getenv("START_PARAM")
router = Router()


async def _send_referral_stats(message: types.Message, link, bot: Bot):
    stats = await get_referral_stats(link.code)
    if not stats:
        return
    me = await bot.get_me()
    url = f"https://t.me/{me.username}?start=ad_{link.name}"
    countries = stats["countries"]
    total = stats["clicks"]
    country_text = "\n".join(
        f"  {country}: {count} ({count / total * 100:.1f}%)"
        for country, count in countries.most_common()
    ) if total else "  —"
    price = "-" if link.price is None else f"{float(link.price):.4f}"
    total_cost = "-" if stats["total_cost"] is None else f"{stats['total_cost']:.2f}"
    await message.answer(
        "📊 <b>Статистика реферальной ссылки</b>\n\n"
        f"ID: <code>#{link.code}</code>\n"
        f"Ссылка: <code>{url}</code>\n\n"
        f"Переходов: <code>{total}</code>\n"
        f"Premium: <code>{stats['premium']}</code>\n"
        f"Цена перехода: <code>{price}</code>\n"
        f"Итоговая стоимость: <code>{total_cost}</code>\n\n"
        f"🌍 <b>Страны / language_code:</b>\n{country_text}"
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot, state: FSMContext):
    telegram_id = message.from_user.id
    parts = message.text.split()
    start_param = parts[1] if len(parts) > 1 else None

    # Сначала проверяем наличие пользователя: реферальный переход считается
    # только для нового пользователя, которого ещё нет в БД.
    is_user = await user_checker(telegram_id)
    is_allowed = False
    referral_link = None

    if start_param and start_param.startswith("ad_"):
        referral_name = start_param[3:]
        if referral_name:
            referral_link = await get_referral_link_by_name(referral_name)
            if referral_link:
                is_admin = str(telegram_id) == str(ADMIN_ID)
                is_viewer = referral_link.viewer_id is not None and telegram_id == referral_link.viewer_id

                # Админ и viewer могут открыть ссылку, но никогда не считаются переходом.
                if is_admin or is_viewer:
                    await _send_referral_stats(message, referral_link, bot)
                    return

                if not is_user:
                    is_allowed = await record_referral_click(
                        referral_name,
                        telegram_id,
                        message.from_user.language_code,
                        bool(message.from_user.is_premium),
                        ADMIN_ID,
                    )

    if not is_user:
        ref_id = None

        # Сохраняем прежнюю механику обычных start-параметров.
        if not is_allowed:
            if start_param == param_start:
                is_allowed = True
            elif start_param and start_param.isdigit():
                potential_ref_id = int(start_param)
                if potential_ref_id != telegram_id and await user_checker(potential_ref_id):
                    ref_id = potential_ref_id
                    is_allowed = True

        if is_allowed:
            await state.set_state(AgreeTerms.agree)
            await add_user(telegram_id)
            await bot.send_message(ADMIN_ID, f"👤 Новый пользователь {telegram_id}")

            if ref_id:
                await state.update_data(ref_id=ref_id)
            await message.answer(
                "👇 <i>Нажмите кнопку ниже, чтобы принять <a href=\"https://telegra.ph/Politika-konfidencialnosti-04-01-26\">политику кофиденциальности</a> и <a href=\"https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19\">пользовательское соглашение</a></i>\n\nПродолжая, вы соглашаетесь, что вам исполнилось 18 лет",
                reply_markup=agree_menu,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
    else:
        if await check_user_agreement(telegram_id):
            await message.answer(
                "<b>Добро пожаловать!</b>\n\n"
                "<i>Выбери действие</i> 👇",
                reply_markup=categories_menu)
            await state.clear()
        else:
            await message.answer(
                "👇 <i>Нажмите кнопку ниже, чтобы принять <a href=\"https://telegra.ph/Politika-konfidencialnosti-04-01-26\">политику кофиденциальности</a> и <a href=\"https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19\">пользовательское соглашение</a></i>",
                reply_markup=agree_menu,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )


@router.message(Command("delete_me"))
async def cmd_delete_me(message: types.Message, bot: Bot, state: FSMContext):
    telegram_id = message.from_user.id
    res = await delete_user_by_telegram_id(telegram_id)
    if res[0]:
        await message.answer("✅ Ваш аккаунт и все связанные данные были удалены.")
    else:
        await message.answer("❌ Произошла ошибка при удалении вашего аккаунта. Пожалуйста, попробуйте позже.")


@router.message(Command("policy"))
async def cmd_policy(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer("<a href=\"https://telegra.ph/Politika-konfidencialnosti-04-01-26\">Политика кофиденциальности</a> и <a href=\"https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19\">пользовательское соглашение</a>")


@router.message(Command("support"))
async def cmd_support(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer("Если у вас возникли вопросы или проблемы, пожалуйста, свяжитесь с нашей поддержкой: @pinqblu")
