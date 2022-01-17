import secrets

from .constants import UUID_ALPHABET, UUID_LENGTH


def generate_uuid() -> str:
    """
    Generates and returns a UUID.

    Returns:
        str: The UUID.
    """

    return ''.join(secrets.choice(UUID_ALPHABET) for _ in range(UUID_LENGTH))
