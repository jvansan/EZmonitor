import bcrypt
import logging
import datetime
from dataclasses import dataclass, field
from typing import List

import asyncpg
import asyncpg.pool

log = logging.getLogger('tornado.application')

# data access types
@dataclass
class Website:
    id: int
    name: str
    url: str
    port: int = 443
    lastchecked: datetime.datetime = None
    results: list = field(default_factory=list)


@dataclass
class Result:
    id: int
    website_id: int
    alive: bool
    run_at: datetime.datetime
    backed_up: bool
    peername: str
    certificate_issuer: str
    certificate_start_date: datetime.datetime = None
    certificate_end_date: datetime.datetime = None


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
    lastchecked TIMESTAMP
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
    certificate_start_date TIMESTAMP,
    certificate_end_date TIMESTAMP,
    PRIMARY KEY (id, website_id),
    FOREIGN KEY (website_id) REFERENCES website(id)
        ON DELETE CASCADE
    )
""",
"""
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    email TEXT,
    password BYTEA
)
"""
]


async def create_pool(user: str = "postgres", password: str = "", 
                  host: str = "localhost", port: int = 5432, 
                  db : str = "test") -> asyncpg.pool.Pool:
    pool = await asyncpg.create_pool(user=user, password=password, host=host,
                                     port=port, database=db)
    return pool


async def connect(user: str = "postgres", password: str = "", 
                  host: str = "localhost", port: int = 5432, 
                  db : str = "test") -> asyncpg.pool.Pool:
    conn = await asyncpg.connect(user=user, password=password, host=host,
                                     port=port, database=db)
    return conn


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


async def get_one_server(conn: asyncpg.Connection, name: str) -> Website:
    sql = """
        select *
        from website
        where name = $1
    """
    ws = await conn.fetchrow(sql, name)
    return objectify_result(ws, [])


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


async def set_result(conn: asyncpg.Connection, results: dict) -> None:
    sql1 = """insert into website_result(
        website_id, alive, run_at, backed_up, peername, certificate_issuer,
        certificate_start_date, certificate_end_date
        ) values ($1, $2, $3, $4, $5, $6, $7, $8)
    """
    sql2 = """update website set lastchecked = $1 where id = $2"""
    host_info = results.get("ssl")
    now = datetime.datetime.now()
    idx = results['site'].id 
    if host_info:
        peername = host_info.peername[0]
        issuer = host_info.cert.get_issuer().CN
        cert = host_info.cert.to_cryptography()
        start_date = cert.not_valid_before
        end_date = cert.not_valid_after
    else:
        peername = None
        issuer = None
        start_date = None
        end_date = None

    await conn.execute(sql1,
        idx,
        results.get("alive"),
        now,
        results.get("backed_up"),
        peername,
        issuer,
        start_date,
        end_date
    )
    await conn.execute(sql2, now, idx)


def objectify_result(ws: asyncpg.Record, res: RecordList) -> Website:
    results = [Result(*r) for r in res]
    return Website(*ws, results)


# Adding User with following
async def __add_user(conn: asyncpg.Connection, email: str, password: str) -> None:
    sql = "insert into users(email, password) values ($1, $2)"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    await conn.execute(sql, email, hashed)


async def get_user(conn: asyncpg.Connection, email: str) -> asyncpg.Record:
    sql = "select * from users where email = $1"
    res = await conn.fetchrow(sql, email)
    return res


async def authenticate(conn: asyncpg.Connection, email: str, password: str) -> bool:
    user = await get_user(conn, email)
    if not user:
        return False
    return bcrypt.checkpw(password.encode(), user.get('password'))
