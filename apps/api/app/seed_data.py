"""One-off script: run pending migrations and seed defaults."""
import asyncio

from app.db.session import SessionLocal
from app.services.seed import seed_defaults


async def main() -> None:
    async with SessionLocal() as db:
        await seed_defaults(db)
    print("Seed data inserted.")


if __name__ == "__main__":
    asyncio.run(main())
