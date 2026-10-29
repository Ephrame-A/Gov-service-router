"""Create the first administrator without using the public registration API."""

import argparse
import asyncio
from getpass import getpass

from sqlalchemy import select

from app.auth import get_jwt_secret, hash_password
from app.db.models import User
from app.db.session import async_session


async def create_admin(email: str, password: str) -> None:
    get_jwt_secret()
    async with async_session() as session:
        existing = await session.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ValueError("An account with that email already exists")
        session.add(User(email=email, password_hash=hash_password(password), role="admin"))
        await session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an administrator account")
    parser.add_argument("email", help="Administrator email address")
    args = parser.parse_args()
    password = getpass("New admin password (at least 12 characters): ")
    confirmation = getpass("Confirm password: ")
    if len(password) < 12 or password != confirmation:
        parser.error("Passwords must match and contain at least 12 characters")
    asyncio.run(create_admin(args.email.strip().lower(), password))
    print("Administrator account created")


if __name__ == "__main__":
    main()
