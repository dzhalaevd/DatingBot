from datetime import (
    datetime,
)
from typing import (
    Literal,
)

from pydantic import (
    BaseModel,
    Field,
)


class OperationDetails(BaseModel):
    """
    Детальная информация об операции из истории.

    https://yoomoney.ru/docs/wallet/user-account/operation-details
    """

    error: str | None
    operation_id: str
    status: str
    pattern_id: str | None
    direction: Literal["in"] | Literal["out"]
    amount: int
    amount_due: int | None
    fee: int | None
    operation_datetime: datetime = Field(alias="datetime")
    title: str
    sender: int | None
    recipient: str | None
    recipient_type: str | None
    message: str | None
    comment: str | None
    label: str | None
    details: str | None
    operation_type: str = Field(alias="type")
