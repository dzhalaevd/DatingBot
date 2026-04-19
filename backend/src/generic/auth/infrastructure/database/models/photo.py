from typing import (
    TYPE_CHECKING,
)

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
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


class Photo(models.Model):
    __tablename__ = "photos"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    remote_url: Mapped[str] = mapped_column(String(255), nullable=False)
    change_count: Mapped[int] = mapped_column(Integer, default=0)
    user: Mapped["User"] = relationship("User", back_populates="photos")

    def __repr__(self) -> str:
        return (
            f"<UserPhoto(id={self.id},"
            f" user_id={self.user_id},"
            f" remote_url={self.remote_url},"
            f" change_count={self.change_count},"
            f" created_at={self.created_at},"
            f" updated_at={self.updated_at})>"
        )
