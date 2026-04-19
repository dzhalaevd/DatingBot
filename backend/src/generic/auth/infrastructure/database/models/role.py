from typing import (
    TYPE_CHECKING,
    Any,
)

from sqlalchemy import (
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


class Role(models.Model):
    __tablename__ = "roles"

    title: Mapped[str] = mapped_column(String(64), unique=True)
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
        }
