import datetime
from typing import (
    TYPE_CHECKING,
)

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
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

if TYPE_CHECKING:
    from .user import (
        User,
    )


# class Gender(enum.Enum):
#     M = "male"
#     W = "female"
#     N = "other"
#
#
# class InterestedIn(enum.Enum):
#     M = "men"
#     W = "women"
#     N = "everyone"
#
#
# class Hobby(enum.Enum):
#     SPORTS = "sports"
#     MUSIC = "music"
#     TRAVEL = "travel"
#     READING = "reading"
#     COOKING = "cooking"
#     MOVIES = "movies"
#     GAMING = "gaming"
#     ART = "art"
#     TECHNOLOGY = "technology"
#     OUTDOORS = "outdoors"


class Profile(models.Model):
    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=true())
    birthdate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    interested_in: Mapped[str] = mapped_column(nullable=False)
    hobbies: Mapped[list[str]] = mapped_column(JSON)
    user: Mapped["User"] = relationship("User", back_populates="profile")

    @property
    def age(self) -> int:
        today = datetime.date.today()
        born = self.birthdate.date()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def __repr__(self) -> str:
        return (
            f"<Profile(id={self.id},"
            f" user_id={self.user_id},"
            f" first_name={self.first_name},"
            f" gender={self.gender},"
            f" city={self.city},"
            f" is_active={self.is_active},"
            f" birthdate={self.birthdate})>"
        )
