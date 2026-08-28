import os
import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.utils.referrals import (
    create_referral_link,
    delete_referral_link,
    get_referral_link,
    get_referral_links,
    get_referral_stats,
)

router = Router()
ADMIN_ID = os.getenv("ADMIN_ID")
NAME_RE = re.compile(r"^[a-z0-9]+$")


def _is_admin(user_id: int) -> bool:
    return str(user_id) == str(ADMIN_ID)


def _help(command: str | None = None) -> str:
    if command == "create":
        return (
            "📌 <b>/ref_create</b>\n\n"
            "Создание реферальной ссылки.\n\n"
            "<code>/ref_create &lt;name&gt; &lt;price|-&gt; &lt;viewer_id&gt;</code>\n\n"
            "name — только латиница и цифры в нижнем регистре.\n"
            "price — стоимость перехода, вещественное число, либо <code>-</code>.\n"
            "viewer_id — Telegram ID единственного дополнительного пользователя, который может смотреть статистику."
        )
    if command == "stats":
        return "📊 <b>/ref_stats</b> <code>&lt;link_id&gt;</code>\nПример: <code>/ref_stats #A7k3X9</code>"
    if command == "delete":
        return "🗑 <b>/ref_delete</b> <code>&lt;link_id&gt;</code>\nПример: <code>/ref_delete #A7k3X9</code>"
    return (
        "🔗 <b>Реферальные команды</b>\n\n"
        "<code>/ref_create &lt;name&gt; &lt;price|-&gt; &lt;viewer_id&gt;</code> — создать ссылку\n"
        "<code>/ref_list</code> — список ссылок\n"
        "<code>/ref_stats &lt;link_id&gt;</code> — статистика\n"
        "<code>/ref_delete &lt;link_id&gt;</code> — удалить ссылку"
    )


@router.message(Command("ref_create"))
async def ref_create(message: Message):
    if not _is_admin(message.from_user.id):
        return await message.answer("❌ Недостаточно прав.")

    args = message.text.split()[1:]
    if len(args) != 3:
        return await message.answer(_help("create"))

    name, price_raw, viewer_raw = args
    if not NAME_RE.fullmatch(name):
        return await message.answer("❌ name должен содержать только строчные латинские буквы и цифры.\n\n" + _help("create"))

    if price_raw == "-":
        price = None
    else:
        try:
            price = float(price_raw)
            if price < 0:
                raise ValueError
        except ValueError:
            return await message.answer("❌ price должен быть вещественным числом или <code>-</code>.\n\n" + _help("create"))

    try:
        viewer_id = int(viewer_raw)
        if viewer_id <= 0:
            raise ValueError
    except ValueError:
        return await message.answer("❌ viewer_id должен быть Telegram ID.\n\n" + _help("create"))

    link = await create_referral_link(name, price, viewer_id)
    me = await message.bot.get_me()
    url = f"https://t.me/{me.username}?start=ad_{link.name}"
    await message.answer(
        "✅ <b>Ссылка создана</b>\n\n"
        f"ID: <code>#{link.code}</code>\n"
        f"Ссылка: <code>{url}</code>\n"
        f"Цена перехода: <code>{'-' if price is None else price}</code>\n"
        f"Viewer ID: <code>{viewer_id}</code>"
    )


@router.message(Command("ref_list"))
async def ref_list(message: Message):
    if not _is_admin(message.from_user.id):
        return await message.answer("❌ Недостаточно прав.")
    links = await get_referral_links()
    if not links:
        return await message.answer("🔗 Реферальных ссылок пока нет.")

    me = await message.bot.get_me()
    lines = ["🔗 <b>Реферальные ссылки</b>"]
    for link in links:
        url = f"https://t.me/{me.username}?start=ad_{link.name}"
        lines.append(
            f"\n<b>#{link.code}</b> — <code>{link.name}</code>\n"
            f"{url}\n"
            f"Цена: <code>{'-' if link.price is None else link.price}</code> | Viewer: <code>{link.viewer_id}</code>"
        )
    await message.answer("\n".join(lines))


@router.message(Command("ref_stats"))
async def ref_stats(message: Message):
    args = message.text.split()[1:]
    if len(args) != 1:
        return await message.answer(_help("stats"))

    link = await get_referral_link(args[0])
    if not link:
        return await message.answer("❌ Реферальная ссылка не найдена.")
    if not (_is_admin(message.from_user.id) or message.from_user.id == link.viewer_id):
        return await message.answer("❌ У вас нет доступа к статистике этой ссылки.")

    stats = await get_referral_stats(link.code)
    me = await message.bot.get_me()
    url = f"https://t.me/{me.username}?start=ad_{link.name}"
    countries = stats["countries"]
    country_text = "\n".join(f"  {country}: {count}" for country, count in countries.most_common()) or "  —"
    total_cost = "-" if stats["total_cost"] is None else f"{stats['total_cost']:.2f}"
    price = "-" if link.price is None else f"{link.price:.2f}"

    await message.answer(
        "📊 <b>Статистика реферальной ссылки</b>\n\n"
        f"ID: <code>#{link.code}</code>\n"
        f"Ссылка: <code>{url}</code>\n\n"
        f"Переходов: <code>{stats['clicks']}</code>\n"
        f"Premium: <code>{stats['premium']}</code>\n"
        f"Цена перехода: <code>{price}</code>\n"
        f"Итоговая стоимость: <code>{total_cost}</code>\n\n"
        f"🌍 <b>Страны / language_code:</b>\n{country_text}"
    )


@router.message(Command("ref_delete"))
async def ref_delete(message: Message):
    if not _is_admin(message.from_user.id):
        return await message.answer("❌ Недостаточно прав.")
    args = message.text.split()[1:]
    if len(args) != 1:
        return await message.answer(_help("delete"))
    if await delete_referral_link(args[0]):
        await message.answer(f"✅ Ссылка <code>{args[0]}</code> удалена.")
    else:
        await message.answer("❌ Реферальная ссылка не найдена.")


@router.message(Command("ref"))
async def ref_help(message: Message):
    await message.answer(_help())
