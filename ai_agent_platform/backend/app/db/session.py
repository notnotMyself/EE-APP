"""Database session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.db.base_class import Base  # noqa: F401


def get_database_url() -> str:
    """
    Get the database URL with proper asyncpg driver prefix.
    Handles Supabase Pooler (Supavisor) connections which require
    statement_cache_size=0 for Transaction mode.
    """
    url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    # Check if using Supabase Pooler (port 6543)
    # Transaction mode pooler requires prepared_statement_cache_size=0
    if ":6543" in url:
        # Add options for Supavisor Transaction mode
        if "?" in url:
            url += "&prepared_statement_cache_size=0"
        else:
            url += "?prepared_statement_cache_size=0"
    
    return url


# Create async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.DEBUG,
    future=True,
    # Disable server-side prepared statements for Supabase Pooler compatibility
    connect_args={"statement_cache_size": 0} if ":6543" in settings.DATABASE_URL else {},
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency to get DB session
async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
