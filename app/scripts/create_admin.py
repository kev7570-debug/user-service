import argparse
import asyncio
import getpass

from tortoise import Tortoise

from app.core.security import hash_password
from app.database import TORTOISE_ORM
from app.models.user import User


async def create_admin(email: str, password: str, first_name: str, last_name: str) -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        normalized_email = email.strip().lower()
        if await User.filter(email=normalized_email).exists():
            raise ValueError("A user with this email already exists")
        await User.create(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=normalized_email,
            password_hash=hash_password(password),
            is_admin=True,
        )
    finally:
        await Tortoise.close_connections()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first administrator")
    parser.add_argument("--email", required=True)
    parser.add_argument("--first-name", required=True)
    parser.add_argument("--last-name", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Password (at least 8 characters): ")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")
    asyncio.run(create_admin(args.email, password, args.first_name, args.last_name))


if __name__ == "__main__":
    main()
