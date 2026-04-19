from pydantic import (
    BaseModel,
    Field,
)


class BalanceDetails(BaseModel):
    total: int
    available: int
    deposition_pending: int | None
    blocked: int | None
    debt: int | None
    hold: int | None


class LinkedCard(BaseModel):
    pan_fragment: str
    card_type: str = Field(None, alias="type")


class AccountInfo(BaseModel):
    """
    Получение информации о состоянии счета пользователя.

    https://yoomoney.ru/docs/wallet/user-account/account-info
    """

    account: str  # номер счета
    balance: int  # баланс счета
    currency: str  # код валюты счета
    account_status: str
    account_type: str
    balance_details: BalanceDetails | None
    cards_linked: list[LinkedCard, ...] | None
