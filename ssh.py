import asyncio
import asyncssh
from typing import Literal
from dataclasses import dataclass

@dataclass
class Server:
    hostname: str
    uptime_implementation: Literal["procps-ng", "uutils", "freebsd"]


SERVERS: list[Server] = [
    Server("auriel", "procps-ng"),
    Server("milou", "procps-ng"),
    Server("selene", "procps-ng"),
    Server("shinobu", "procps-ng"),
    Server("shipon", "freebsd"),
    Server("totoro", "procps-ng"),
    Server("volton", "uutils"),
]

async def _report_uptime(uptime: str) -> None:
    print(uptime.split(" "))

async def _status_check_server(server: Server) -> None:
    async with asyncssh.connect(server.hostname) as conn:
        result = await conn.run("uptime")
        assert result.exit_status == 0

        stdout = ""
        if type(result.stdout) is str:
            stdout = result.stdout
        elif type(result.stdout) is bytes:
            stdout = result.stdout.decode("utf-8")

        await _report_uptime(stdout)
            


async def status_check() -> None:
    await asyncio.gather(*[_status_check_server(server) for server in SERVERS])

