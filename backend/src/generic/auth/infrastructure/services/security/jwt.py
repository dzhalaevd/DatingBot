import datetime
from typing import (
    Any,
    Literal,
)
import uuid

from fastapi import (
    Response,
)
from jose import (
    jwt,
)

from src.shared import (
    ex,
    load_config,
)

config = load_config().security


class JWTService:
    @staticmethod
    def _create_token(
            uid: str,
            type_: Literal["access", "refresh"],
            jti: str | None = None,
            expiry: datetime.datetime | datetime.timedelta | None = None,
            issued: datetime.datetime | datetime.timedelta | None = None,
            fresh: bool = False,
            csrf: str | bool = True,
            headers: dict[str, Any] = None,
            audience: str | None = None,
            issuer: str | None = None,
            data: dict[str, Any] | None = None,
            not_before: int | datetime.datetime | datetime.timedelta | None = None,
            ignore_errors: bool = True,
    ) -> str:
        """Encode a token"""
        reserved_claims = {
            "fresh",
            "csrf",
            "iat",
            "exp",
            "iss",
            "aud",
            "type",
            "jti",
            "nbf",
            "sub",
        }
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        additional_claims = {}
        if data is not None:
            if not ignore_errors and set(data.keys()).intersection(reserved_claims):
                raise ValueError(f"{reserved_claims} are forbidden in additional claims")
            additional_claims = {k: v for k, v in data.items() if k not in reserved_claims}

        jwt_claims = {"sub": uid, "jti": jti or str(uuid.uuid4()), "type": type_}

        if type_ == "access":
            jwt_claims["fresh"] = fresh  # type: ignore

        if csrf and not isinstance(csrf, str):
            jwt_claims["csrf"] = str(uuid.uuid4())
        elif isinstance(csrf, str):
            jwt_claims["csrf"] = csrf

        if isinstance(issued, datetime.datetime):
            jwt_claims["iat"] = issued.timestamp()  # type: ignore
        elif isinstance(issued, (float, int)):
            jwt_claims["iat"] = issued
        else:
            jwt_claims["iat"] = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()  # type: ignore

        if isinstance(expiry, datetime.datetime):
            jwt_claims["exp"] = expiry.timestamp()  # type: ignore
        elif isinstance(expiry, datetime.timedelta):
            jwt_claims["exp"] = (now + expiry).timestamp()  # type: ignore
        elif isinstance(expiry, (float, int)):
            jwt_claims["exp"] = expiry

        if audience:
            jwt_claims["aud"] = audience
        if issuer:
            jwt_claims["iss"] = issuer

        if isinstance(not_before, datetime.datetime):
            jwt_claims["nbf"] = not_before.timestamp()  # type: ignore
        elif isinstance(not_before, datetime.timedelta):
            jwt_claims["nbf"] = (now + not_before).timestamp()  # type: ignore
        elif isinstance(not_before, (int, float)):
            jwt_claims["nbf"] = not_before  # type: ignore

        payload = {**additional_claims, **jwt_claims}

        return jwt.encode(
            claims=payload, key=config.secret_key, algorithm=config.algorithm, headers=headers
        )

    @staticmethod
    def decode_token(
            token: str,
            audience: str | None = None,
            issuer: str | None = None,
            verify: bool = True,
    ) -> dict[str, Any]:
        """Decode a token"""
        try:
            return jwt.decode(
                token=token,
                key=config.secret_key,
                algorithms=config.algorithm,
                audience=audience,
                issuer=issuer,
                options={"verify_signature": verify},
            )
        except Exception as e:
            raise ex.JWTDecodeError() from e

    @staticmethod
    def create_access_token(
            uid: str,
            fresh: bool = False,
            headers: dict[str, Any] | None = None,
            data: dict[str, Any] | None = None,
            audience: str | None = None,
    ) -> str:
        expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=config.access_expire_time_in_seconds)
        return JWTService._create_token(
            uid=uid,
            type_="access",
            fresh=fresh,
            headers=headers,
            expiry=expiry,
            data=data,
            audience=audience,
        )

    @staticmethod
    def create_refresh_token(
            uid: str,
            headers: dict[str, Any] | None = None,
            data: dict[str, Any] | None = None,
            audience: str | None = None,
    ) -> str:
        expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=config.refresh_expire_time_in_seconds)
        return JWTService._create_token(
            uid=uid,
            type_="refresh",
            headers=headers,
            expiry=expiry,
            data=data,
            audience=audience,
        )

    @staticmethod
    def _get_cookie_config() -> dict[str, Any]:
        return {
            "secure": config.access_token_cookie_secure,
            "httponly": config.access_token_cookie_httponly,
            "samesite": config.access_token_cookie_samesite,
        }

    @staticmethod
    def set_cookies(
            response: Response,
            access_token: str,
            refresh_token: str,
    ) -> None:
        cookie_config = JWTService._get_cookie_config()

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=config.access_expire_time_in_seconds,
            **cookie_config
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=config.refresh_expire_time_in_seconds,
            **cookie_config
        )

    @staticmethod
    def unset_cookies(response: Response) -> None:
        cookie_config = JWTService._get_cookie_config()

        response.delete_cookie(
            key=config.sessions_cookie_name,
            **cookie_config
        )

        response.delete_cookie(
            key="refresh_token",
            **cookie_config
        )
