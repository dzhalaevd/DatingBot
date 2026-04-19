from dataclasses import (
    dataclass,
)


@dataclass(frozen=True, slots=True)
class PaymentSource:
    BANK_CARD = "AC"
    YOOMONEY_WALLET = "PC"


@dataclass(frozen=True, slots=True)
class PaymentForm:
    link_for_customer: str
    payment_label: str
