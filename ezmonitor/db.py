import asyncpg
import asyncpg.pool

TABLE_DEFS = [
"""
CREATE TABLE IF NOT EXISTS website(
    id SERIAL PRIMARY KEY,
    name TEXT,
    url TEXT,
    port INT,
    lastchecked TIMESTAMP,
    running BOOLEAN
)
""",
"""
CREATE TABLE IF NOT EXISTS website_result(
    website_id INT PRIMARY KEY,
    peername TEXT,
    certificate_issuer TEXT,
    certificate_start_date DATE,
    certificate_end_date DATE
)
"""
]


async def create_pool(user: str = "postgres", password: str = "", 
                  host: str = "localhost", port: int = 5432, 
                  db : str = "test") -> asyncpg.pool.Pool:
    pool = await asyncpg.create_pool(user=user, password=password, host=host,
                                     port=port, database=db)
    return pool


async def setup_tables(conn: asyncpg.Connection) -> None:
    for sql in TABLE_DEFS:
        await conn.execute(sql)