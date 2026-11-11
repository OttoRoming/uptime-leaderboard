import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

import asyncpg as pg

type IPAddress = IPv4Address | IPv6Address


_conn: pg.Connection


@dataclass
class StatusCheck:
    id: UUID
    hostname: str
    success: bool
    reboot: bool
    uptime: timedelta
    created_at: datetime


async def init() -> None:
    global _conn
    _conn = await pg.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
    )


@asynccontextmanager
async def transaction() -> AsyncGenerator[None]:
    async with _conn.transaction():
        yield


async def add_status_check(
    hostname: str, success: bool, reboot: bool, uptime: timedelta | None
) -> StatusCheck:
    row = await _conn.fetchrow(
        """
        insert into status_checks (hostname, success, reboot, uptime)
        values ($1, $2, $3, $4)
        returning *;
    """,
        hostname,
        success,
        reboot,
        uptime,
    )
    assert row is not None

    return StatusCheck(**dict(row))


async def get_last_successful_status_check(hostname: str) -> StatusCheck | None:
    row = await _conn.fetchrow(
        """
        select *
        from status_checks
        where hostname = $1 and success = true
        order by created_at desc
        limit 1;
    """,
        hostname,
    )

    return StatusCheck(**dict(row)) if row else None
