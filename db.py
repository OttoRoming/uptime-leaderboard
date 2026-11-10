import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

import asyncpg as pg

type IPAddress = IPv4Address | IPv6Address


ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

conn: pg.Connection


@dataclass
class StatusCheck:
    id: UUID
    hostname: str
    unreachable: bool
    reboot: bool
    uptime: timedelta
    created_at: datetime


async def init() -> None:
    global conn
    conn = await pg.connect(
        user="uptime",
        password="shushing_face",
        database="leaderboard",
        host="db",
    )


async def transaction() -> AsyncIterator[None]:
    async with conn.transaction():
        yield


async def add_status_check(
    hostname: str, unreachable: bool, reboot: bool, uptime: timedelta
) -> StatusCheck:
    row = await conn.fetchrow(
        """
        insert into status_checks (hostname, unreachable, reboot, uptime)
        values ($1, $2, $3, $4)
        returning *;
    """,
        hostname,
        unreachable,
        reboot,
        uptime,
    )
    assert row is not None

    return row
