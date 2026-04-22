from utils.yoomoney.request import (
    send_request,
)
from utils.yoomoney.types import (
    AccountInfo,
    Operation,
    OperationDetails,
    PaymentForm,
    PaymentSource,
)


class YooMoneyWallet:
    def __init__(self, access_token: str):
        self.host = "https://yoomoney.ru"
        self.__headers = dict(Authorization=f"Bearer {access_token}")

    @property
    async def account_info(self) -> AccountInfo:
        url = self.host + "/api/account-info"
        response, data = await send_request(url, headers=self.__headers)
        return AccountInfo.parse_obj(data)

    async def get_operation_details(self, operation_id: str) -> OperationDetails:
        url = self.host + "/api/operation-details"
        response, data = await send_request(
            url, headers=self.__headers, data={"operation_id": operation_id}
        )
        return OperationDetails.parse_obj(data)

    async def get_operation_history(
            self, label: str | None = None
    ) -> list[Operation, ...]:
        """
        Получение последних 30 операций.

        На 10.03.2023 API yoomoney напросто игнорирует указанные в документации параметры

        https://yoomoney.ru/docs/payment-buttons/using-api/forms?lang=ru#parameters
        """
        history_url = self.host + "/api/operation-history"
        response, data = await send_request(history_url, headers=self.__headers)
        if operations := data.get("operations"):
            parsed = [Operation.parse_obj(operation) for operation in operations]
            if label:
                parsed = [operation for operation in parsed if operation.label == label]
            return parsed

    async def create_payment_form(
            self,
            amount_rub: int,
            unique_label: str,
            success_redirect_url: str | None = None,
            payment_source: PaymentSource = PaymentSource.BANK_CARD,
    ) -> PaymentForm:
        account_info = await self.account_info
        quickpay_url = "https://yoomoney.ru/quickpay/confirm.xml?"
        params = {
            "receiver": account_info.account,
            "quickpay-form": "button",
            "paymentType": payment_source,
            "sum": amount_rub,
            "successURL": success_redirect_url,
            "label": unique_label,
        }
        params = {k: v for k, v in params.items() if v}
        response = await send_request(
            quickpay_url, response_without_data=True, params=params
        )

        return PaymentForm(
            link_for_customer=str(response.url), payment_label=unique_label
        )

    async def check_payment_on_successful(self, label: str) -> bool:
        need_operations = await self.get_operation_history(label=label)
        return bool(need_operations) and need_operations.pop().status == "success"

    async def revoke_token(self) -> None:
        url = self.host + "/api/revoke"
        response = await send_request(
            url=url, response_without_data=True, headers=self.__headers
        )
        print(
            f"Запрос на отзыв токена завершен с кодом {response.status} "
            "https://yoomoney.ru/docs/wallet/using-api/authorization/revoke-access-token#response"
        )
