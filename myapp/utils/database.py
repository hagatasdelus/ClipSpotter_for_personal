from myapp.app import async_session
from sqlalchemy.exc import SQLAlchemyError
import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager


@asynccontextmanager
async def db_session() -> AsyncGenerator:
    async with async_session() as session, session.begin():
        try:
            yield session
            await session.commit()
        except asyncio.TimeoutError:
            await session.rollback()
            print("❌ Timeout error in database operation - session")
            raise
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"❌ SQLAlchemy error in database operation: {e}")
            raise
        except Exception as e:
            await session.rollback()
            print(f"❌ General error in database operation: {e}")
            raise


@asynccontextmanager
async def select_session() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
        except asyncio.TimeoutError:
            print(f"❌ Timeout error in database operation - select")
            raise
        except SQLAlchemyError as e:
            print(f"❌ SQLAlchemy error in database operation - select: {e}")
            raise
        except Exception as e:
            print(f"❌ General error in database operation - select: {e}")
            raise
