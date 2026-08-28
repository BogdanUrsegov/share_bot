import secrets
import string
from collections import Counter

from sqlalchemy import delete, select

from bot.database.models import ReferralClick, ReferralLink, User
from bot.database.session import AsyncSessionLocal


_CODE_ALPHABET = string.ascii_letters + string.digits


async def create_referral_link(name: str, price: float | None, viewer_id: int | None) -> ReferralLink:
    async with AsyncSessionLocal() as session:
        while True:
            code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
            exists = await session.scalar(select(ReferralLink.id).where(ReferralLink.code == code))
            if not exists:
                break
        # 0 is used for "no viewer" so deployment over an already-created
        # NOT NULL referral_links.viewer_id column remains compatible.
        link = ReferralLink(code=code, name=name, price=price, viewer_id=viewer_id or 0)
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link


async def get_referral_links() -> list[ReferralLink]:
    async with AsyncSessionLocal() as session:
        result = await session.scalars(select(ReferralLink).order_by(ReferralLink.created_at.desc()))
        return list(result.all())


async def get_referral_link(code: str) -> ReferralLink | None:
    async with AsyncSessionLocal() as session:
        return await session.scalar(select(ReferralLink).where(ReferralLink.code == code.lstrip("#")))


async def get_referral_link_by_name(name: str) -> ReferralLink | None:
    async with AsyncSessionLocal() as session:
        return await session.scalar(select(ReferralLink).where(ReferralLink.name == name))


async def delete_referral_link(code: str) -> bool:
    code = code.lstrip("#")
    async with AsyncSessionLocal() as session:
        link = await session.scalar(select(ReferralLink).where(ReferralLink.code == code))
        if not link:
            return False
        await session.execute(delete(ReferralClick).where(ReferralClick.referral_id == link.id))
        await session.execute(delete(ReferralLink).where(ReferralLink.id == link.id))
        await session.commit()
        return True


async def record_referral_click(
    name: str,
    telegram_id: int,
    language_code: str | None,
    is_premium: bool,
    admin_id: int | str | None,
) -> bool:
    """Record one unique referral acquisition.

    A click counts only when the Telegram user is not already in the users table.
    Admin and the link's configured viewer never count as referral clicks.
    The return value is used by the start handler as the access flag.
    """
    async with AsyncSessionLocal() as session:
        link = await session.scalar(select(ReferralLink).where(ReferralLink.name == name))
        if not link:
            return False

        if str(telegram_id) == str(admin_id) or (
            link.viewer_id not in (None, 0) and telegram_id == link.viewer_id
        ):
            return True

        # A user already registered in the bot is never a referral conversion.
        existing_user = await session.scalar(
            select(User.id).where(User.telegram_id == telegram_id)
        )
        if existing_user is not None:
            return False

        # Also guard the referral table itself against duplicate conversions.
        existing_click = await session.scalar(
            select(ReferralClick.id).where(
                ReferralClick.referral_id == link.id,
                ReferralClick.telegram_id == telegram_id,
            )
        )
        if existing_click is not None:
            return False

        session.add(ReferralClick(
            referral_id=link.id,
            telegram_id=telegram_id,
            language_code=language_code or "unknown",
            is_premium=is_premium,
        ))
        await session.commit()
        return True


async def get_referral_stats(code: str) -> dict | None:
    async with AsyncSessionLocal() as session:
        link = await session.scalar(select(ReferralLink).where(ReferralLink.code == code.lstrip("#")))
        if not link:
            return None
        clicks = (await session.scalars(
            select(ReferralClick)
            .where(ReferralClick.referral_id == link.id)
            .order_by(ReferralClick.created_at.asc())
        )).all()
        countries = Counter(click.language_code or "unknown" for click in clicks)
        total = len(clicks)
        premium = sum(1 for click in clicks if click.is_premium)
        total_cost = float(link.price) * total if link.price is not None else None
        return {
            "link": link,
            "clicks": total,
            "premium": premium,
            "countries": countries,
            "total_cost": total_cost,
        }
