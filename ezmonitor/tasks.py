import logging
import socket
import time
from collections import namedtuple
from datetime import datetime

import asyncpg
import idna
from OpenSSL import SSL
from tornado import gen, httpclient

from ezmonitor import db

HostInfo = namedtuple('HostInfo', 'cert hostname peername', defaults=(None, None, None))
log = logging.getLogger('tornado.application')

# Example tasks
# Both sync and async tasks work
async def tick(seconds=3):
    log.warn("TICK")
    await gen.sleep(seconds)
    log.warn("FINISHED")


def block_tick(seconds=3):
    log.warn("LONG TICK")
    time.sleep(seconds)
    log.warn("FINSIHED")


async def run_checks(pool: asyncpg.pool.Pool, server_config: dict) -> None:
    conn = await pool.acquire()
    site = await db.get_one_server(conn, server_config['name'])
    results = {"site": site}
    for job in server_config.get("jobs"):
        if job == "check_alive":
            results['alive'] = await check_alive(site)
        elif job == "check_ssl":
            results['ssl'] = get_certificate(site.url, site.port)
        elif job == "check_backup":
            log.warn(f"{job} - Not implemented")
        else:
            log.error(f"Unsupported job - {job}")
    log.debug(results)
    await report_results(conn, results)
    await pool.release(conn)


async def report_results(conn: asyncpg.Connection, results: dict) -> None:
    db.set_result(conn, results)
    # TODO: add notifications


async def check_alive(site: db.Website) -> bool:
    url = f"http://{site.url}"
    response = await httpclient.AsyncHTTPClient().fetch(url, validate_cert=False)
    return response.code == 200


def get_certificate(hostname: str, port: int) -> HostInfo:
    hostname_idna = idna.encode(hostname)
    sock = socket.socket()

    sock.connect((hostname, port))
    peername = sock.getpeername()
    ctx = SSL.Context(SSL.SSLv23_METHOD) # most compatible
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    sock_ssl.close()
    sock.close()

    return HostInfo(cert=cert, peername=peername, hostname=hostname)
