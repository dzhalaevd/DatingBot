from fastapi import (
    HTTPException,
    status,
)

from src.shared import (
    ex,
)


class InvalidTokenError(HTTPException):
    """Custom error when provided token is invalid"""

    def __init__(
            self,
            status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
            message: str = "Invalid token"
    ):
        detail = {"code": ex.AuthExceptionCodes.INVALID_PROVIDED_TOKEN, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class TokenExpiredError(HTTPException):
    """Custom error when provided token is expired"""

    def __init__(
            self,
            status_code: int = status.HTTP_401_UNAUTHORIZED,
            message: str = "Token expired"
    ):
        detail = {"code": "TOKEN_EXPIRED", "message": message}
        super().__init__(status_code=status_code, detail=detail)


class InvalidSignatureError(HTTPException):
    """Custom error when provided signature is invalid"""

    def __init__(
            self,
            status_code: int = status.HTTP_401_UNAUTHORIZED,
            message: str = "Invalid signature",
    ):
        detail = {"code": ex.AuthExceptionCodes.INVALID_SIGNATURE, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class MissingTokenError(HTTPException):
    """Custom error when no token is provided"""

    def __init__(
            self,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            message: str = "Exception raised when no token can be parsed from request",
    ):
        detail = {"code": ex.AuthExceptionCodes.INVALID_PROVIDED_TOKEN, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class UserAlreadyExistsError(HTTPException):
    """Custom error when user already created."""

    def __init__(
            self,
            status_code: int = status.HTTP_409_CONFLICT,
            message: str = "User with provided data already exists",
    ) -> None:
        detail = {"code": ex.AuthExceptionCodes.USER_ALREADY_EXISTS, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class UserDeactivatedError(HTTPException):
    """Custom error when user deactivated."""

    def __init__(
            self,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            message: str = "Your account is deactivated"
    ):
        detail = {"code": ex.AuthExceptionCodes.USER_DEACTIVATED, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class PasswordIncorrectError(HTTPException):
    """Custom error when provided password is incorrect."""

    def __init__(
            self,
            status_code: int = status.HTTP_401_UNAUTHORIZED,
            message: str = "Invalid username or password",
    ) -> None:
        detail = {"code": ex.AuthExceptionCodes.PROVIDED_PASSWORD_INCORRECT, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundError(HTTPException):
    """Custom error when user not found."""

    def __init__(
            self,
            status_code: int = status.HTTP_404_NOT_FOUND,
            message: str = "User is not exists",
    ) -> None:
        detail = {"code": ex.AuthExceptionCodes.NOT_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class RoleNotFoundError(HTTPException):
    """Custom error when role not found"""

    def __init__(
            self,
            status_code: int = status.HTTP_404_NOT_FOUND,
            message: str = "Role is not exists",
    ):
        detail = {"code": ex.AuthExceptionCodes.NOT_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class CredentialsError(HTTPException):
    """Custom error when credentials are invalid or missing."""

    def __init__(
            self,
            status_code: int = status.HTTP_401_UNAUTHORIZED,
            message: str = "Could not validate credentials",
    ) -> None:
        detail = {"code": ex.AuthExceptionCodes.CREDENTIALS_INVALID, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class OldPasswordIncorrectError(HTTPException):
    """Custom error when old password is incorrect."""

    def __init__(
            self,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            message: str = "Old password is incorrect",
    ):
        detail = {"code": ex.AuthExceptionCodes.OLD_PASSWORD_INVALID, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class ProfileNotFoundError(HTTPException):
    """Custom error when profile does not exist."""

    def __init__(
            self,
            status_code: int = status.HTTP_404_NOT_FOUND,
            message: str = "Profile does not exist",
    ):
        detail = {"code": ex.AuthExceptionCodes.NOT_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)
