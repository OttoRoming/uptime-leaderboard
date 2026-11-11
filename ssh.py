import asyncio
import json
from datetime import datetime, timedelta

import asyncssh
from asyncssh import SSHClientConnection, SSHClientConnectionOptions

import db
from globals import INTERVAL_SECONDS

CONNECTION_OPTIONS = SSHClientConnectionOptions(connect_timout=f"{INTERVAL_SECONDS}s", login_timeout=f"{INTERVAL_SECONDS}s")

class StatusException(Exception):
    pass

class Server:
    def __init__(self, hostname, os) -> None:
        self.hostname = hostname 
        self.os = os

    async def _run_command(self, conn: SSHClientConnection, command: str) -> str:
        result = await conn.run("uptime")
        assert result.exit_status == 0

        stdout = ""
        if type(result.stdout) is str:
            stdout = result.stdout
        elif type(result.stdout) is bytes:
            stdout = result.stdout.decode("utf-8")

        return stdout


    async def status_check(self) -> None:
        if self.os == "freebsd":
            command = "uptime --libxo json"
        elif self.os == "linux":
            command = "cat /proc/uptime"
        else:
            raise StatusException("Unknown OS")

        try:
            async with asyncssh.connect(self.hostname, options=CONNECTION_OPTIONS) as conn:
                output = await self._run_command(conn, command)
        except asyncssh.TimeoutError as _:
            await db.add_status_check(self.hostname, False, False, None)

        if self.os == "freebsd":
            data = json.loads(output)
            assert data["__version"] == 1
            info = data["uptime-information"]

            uptime = timedelta(
                days=info["days"],
                hours=info["hours"],
                minutes=info["minutes"],
                seconds=info["seconds"],
            )
        elif self.os == "linux":
            seconds = output.split(".")[0]
            uptime = timedelta(seconds=int(seconds))
        else:
            raise StatusException("Unknown OS")

        async with db.transaction():
            # If delta since last check is larger than uptime, a reebot has occurred
            last_check = await db.get_last_successful_status_check(self.hostname)
            if last_check is not None:
                check_delta = datetime.now() - last_check.created_at
                reboot = check_delta.seconds > INTERVAL_SECONDS
            else:
                reboot = False

            await db.add_status_check(self.hostname, True, reboot, uptime)

SERVERS: list[Server] = [
    Server("auriel", "linux"),
    Server("milou", "linux"),
    Server("selene", "linux"),
    Server("shinobu", "linux"),
    Server("shipon", "freebsd"),
    Server("totoro", "linux"),
    Server("volton", "linux"),
]

async def status_check_all() -> None:
    await asyncio.gather(*[server.status_check() for server in SERVERS])

