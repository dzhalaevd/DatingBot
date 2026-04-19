import datetime

from sqlalchemy import (
    BIGINT,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    String,
    false,
    text,
    true,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from . import (
    models,
)
from .photo import (
    Photo,
)
from .profile import (
    Profile,
)
from .role import (
    Role,
)


class User(models.Model):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmation_code: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=true())
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=false())
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    language: Mapped[str] = mapped_column(String(2), default=text("'ru'"))

    logins: Mapped["UserLoginModel"] = relationship(
        "UserLoginModel",
        back_populates="user",
        lazy="selectin",
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=True)
    role: Mapped["Role"] = relationship(
        back_populates="users",
        lazy="selectin",
    )

    photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="user", lazy="selectin")
    profile: Mapped["Profile"] = relationship("Profile", uselist=False, back_populates="user", lazy="selectin")

    @property
    def days_since_created(self) -> int:
        return (datetime.datetime.now() - self.created_at).days


class UserLoginModel(models.Model):
    __tablename__ = "user_logins"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    user: Mapped["User"] = relationship("User", back_populates="logins")
    ip_address: Mapped[str] = mapped_column(String(128), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(256))
