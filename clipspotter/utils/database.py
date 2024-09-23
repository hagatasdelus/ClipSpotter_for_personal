import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError

from clipspotter.config import async_session, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def db_session() -> AsyncGenerator:
    async with async_session() as session, session.begin():
        try:
            yield session
            await session.commit()
        except asyncio.TimeoutError:
            await session.rollback()
            logger.info("❌ Timeout error in database operation - session")
            raise
        except SQLAlchemyError as e:
            await session.rollback()
            logger.info("❌ SQLAlchemy error in database operation: %s", e)
            raise
        except Exception as e:
            await session.rollback()
            logger.info("❌ General error in database operation: %e", e)
            raise


@asynccontextmanager
async def select_session() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
        except asyncio.TimeoutError:
            logger.info("❌ Timeout error in database operation - select")
            raise
        except SQLAlchemyError as e:
            logger.info("❌ SQLAlchemy error in database operation - select: %e", e)
            raise
        except Exception as e:
            logger.info("❌ General error in database operation - select: %e", e)
            raise
