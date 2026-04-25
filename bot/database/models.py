from sqlalchemy import Integer, DateTime, BigInteger, Boolean, Numeric, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    agreement: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    daily_time: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    file_id: Mapped[str] = mapped_column(String, nullable=False)

class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    crypto_invoice_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class UserMedia(Base):
    __tablename__ = "user_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    type_media: Mapped[str] = mapped_column(String, nullable=False)
    file_id: Mapped[str] = mapped_column(String, nullable=False)