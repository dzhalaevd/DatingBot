from utils.yoomoney.request import (
    send_request,
)

AUTH_APP_URL = (
    "https://yoomoney.ru/oauth/authorize?client_id={client_id}&response_type=code"
    "&redirect_uri={redirect_uri}&scope={permissions}"
)

GET_TOKEN_URL = (
    "https://yoomoney.ru/oauth/token?code={code}&client_id={client_id}&"
    "grant_type=authorization_code&redirect_uri={redirect_uri}"
)


async def authorize_app(client_id, redirect_uri, app_permissions: list[str, ...]):
    formatted_auth_app_url = AUTH_APP_URL.format(
        client_id=client_id,
        redirect_uri=redirect_uri,
        permissions="%20".join(app_permissions),
    )
    response = await send_request(formatted_auth_app_url, response_without_data=True)

    print(f"Перейдите по URL и подтвердите доступ для приложения\n{response.url}")
    code = input("Введите код в консоль >  ").strip()

    get_token_url = GET_TOKEN_URL.format(
        code=code, client_id=client_id, redirect_uri=redirect_uri
    )
    _, data = await send_request(get_token_url)

    access_token = data.get("access_token")
    if not access_token:
        return print(f"Не удалось получить токен. {data.get('error', '')}")

    return print(f"Ваш токен — {access_token}. Сохраните его в безопасном месте!")
