import logging
from collections import namedtuple
from typing import List

import asyncpg
import asyncpg.pool

log = logging.getLogger('tornado.application')

# data access types
Website = namedtuple("website", "id name url port lastchecked running results")
Result = namedtuple("result", "id website_id alive run_at backup_up peername certicate_issuer certificate_start_date certificate_end_date")
# Type hinting
WebsiteList = List[Website]
RecordList = List[asyncpg.Record]

TABLE_DEFS = [
"""
CREATE TABLE IF NOT EXISTS website(
    id SERIAL PRIMARY KEY,
    name TEXT,
    url TEXT,
    port INT,
    lastchecked TIMESTAMP,
    running BOOLEAN DEFAULT FALSE
)
""",
"""
CREATE TABLE IF NOT EXISTS website_result(
    id SERIAL,
    website_id INT NOT NULL,
    alive BOOLEAN DEFAULT TRUE,
    run_at TIMESTAMP DEFAULT now(), 
    backed_up BOOLEAN,
    peername TEXT,
    certificate_issuer TEXT,
    certificate_start_date DATE,
    certificate_end_date DATE,
    PRIMARY KEY (id, website_id),
    FOREIGN KEY (website_id) REFERENCES website(id)
        ON DELETE CASCADE
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
    """Create tables if not exist
    
    Args:
        conn (asyncpg.Connection): Postgres connection
    
    """
    for sql in TABLE_DEFS:
        await conn.execute(sql)


async def server_exists(conn: asyncpg.Connection, name: str) -> bool:
    """Check is server is in DB
    
    Args:
        conn (asyncpg.Connection): Postgres connection
        name (str): Server name in Config/DB
    
    Returns:
        bool: Whether server is in DB already
    """
    sql = "select id from website where name = $1"
    res = await conn.fetchval(sql, name)
    return bool(res)

async def get_one_status(conn: asyncpg.Connection, name: str, history: int = 5) -> Website:
    sql1 = """
        select *
        from website
        where name = $1
    """
    sql2 = """
    select *
    from website_result
    where website_id = $1
    limit $2
    """
    ws = await conn.fetchrow(sql1, name)
    if not ws:
        return None
    res = await conn.fetch(sql2, ws[0], history)
    log.debug(f"RESULTS: {ws} - {res}")
    return objectify_result(ws, res)

async def get_all_status(conn: asyncpg.Connection, history: int = 2) -> WebsiteList:
    sql1 = """
    select *
    from website
    """
    sql2 = """
    select *
    from website_result
    where website_id = $1
    limit $2
    """
    results = []
    ws = await conn.fetch(sql1)
    if not ws:
        return None
    for w in ws:
        res = await conn.fetch(sql2, w[0], history)
        results.append(objectify_result(w, res))
    return results

async def add_server(conn: asyncpg.Connection, name: str, url: str, port: int=None) -> None:
    """Add server
    
    Args:
        conn (asyncpg.Connection): Postgres connection
        name (str): Server name in Config/DB
        url: (str): Server URL
        port (Optional, int): 
    """
    sql = "insert into website(name, url, port) values($1, $2, $3)"
    await conn.execute(sql, name, url, port)

def objectify_result(ws: asyncpg.Record, res: RecordList) -> Website:
    results = [Result(*r) for r in res]
    return Website(*ws, results)
