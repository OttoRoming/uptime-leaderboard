import asyncio

import asyncssh


class Server:
    def __init__(self, hostname, uptime_implementation) -> None:
        self.hostname = hostname 
        self.uptime_implementation = uptime_implementation 

    async def _report_uptime(self, uptime: str) -> None:
        print(uptime.split(" "))

    async def status_check(self) -> None:
        async with asyncssh.connect(self.hostname) as conn:
            result = await conn.run("uptime")
            assert result.exit_status == 0

            stdout = ""
            if type(result.stdout) is str:
                stdout = result.stdout
            elif type(result.stdout) is bytes:
                stdout = result.stdout.decode("utf-8")

            await self._report_uptime(stdout)



SERVERS: list[Server] = [
    Server("auriel", "procps-ng"),
    Server("milou", "procps-ng"),
    Server("selene", "procps-ng"),
    Server("shinobu", "procps-ng"),
    Server("shipon", "freebsd"),
    Server("totoro", "procps-ng"),
    Server("volton", "uutils"),
]

async def status_check_all() -> None:
    await asyncio.gather(*[server.status_check() for server in SERVERS])

