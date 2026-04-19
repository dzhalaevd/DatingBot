import hashlib
import hmac
import time

from argon2 import (
    PasswordHasher,
)
from argon2.exceptions import (
    VerifyMismatchError,
)

from src.domain.auth import (
    IPasswordEncoder,
)
from src.shared import (
    load_config,
)

config = load_config().security


class HashService(IPasswordEncoder):
    """
    A class for hashing and verifying passwords and signatures.

    Examples:
        To hash a password:

        >>> hashed_password = HashService.hash_password("my_password")

        To verify a password:

        >>> is_valid_password = HashService.verify_password(password=hashed_password, hashed_password="my_password")

        To verify a Telegram bot API request signature:

        >>> is_valid_signature = HashService.verify_signature(
        ...     telegram_id=12345678,
        ...     signature="abcdefghijklmnopqrstuvwxyz123456",
        ...     timestamp=1633028000,
        ...     nonce=12345
        ... )
    """
    _ph = PasswordHasher()

    @staticmethod
    def hash_password(password: str) -> str:
        return HashService._ph.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            HashService._ph.verify(password, hashed_password)
            return True
        except VerifyMismatchError:
            return False

    @staticmethod
    def verify_signature(
            telegram_id: int,
            signature: str,
            timestamp: int,
            nonce: int,
    ) -> bool:
        current_time = int(time.time())
        time_diff = abs(current_time - timestamp)
        if time_diff > 5 * 60:
            return False
        data_to_verify = f"{telegram_id}{timestamp}{nonce}"
        expected_signature = hmac.new(
            config.signature_secret_key.encode(), data_to_verify.encode(), hashlib.sha256
        ).hexdigest()

        return expected_signature == signature
