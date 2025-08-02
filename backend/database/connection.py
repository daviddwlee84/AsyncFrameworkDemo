import os
from typing import Optional
from supabase import create_client, Client
import asyncpg
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.database_url = os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
        )

        self.supabase: Optional[Client] = None
        self.pool: Optional[asyncpg.Pool] = None

    def get_supabase_client(self) -> Client:
        """Get Supabase client for REST API operations"""
        if not self.supabase:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
        return self.supabase

    async def get_db_pool(self) -> asyncpg.Pool:
        """Get PostgreSQL connection pool for direct database operations"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.database_url)
        return self.pool

    async def close_pool(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None


# Global database manager instance
db_manager = DatabaseManager()
