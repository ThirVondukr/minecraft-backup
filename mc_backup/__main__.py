import asyncio

import dotenv

from mc_backup._backup import MinecraftBackup
from mc_backup._rcon import MinecraftClient
from mc_backup.settings import AppSettings


async def main() -> None:
    dotenv.load_dotenv()

    settings = AppSettings()  # type: ignore[call-arg]
    while True:
        async with MinecraftClient(
            password=settings.rcon_password,
            host=settings.rcon_host,
            port=settings.rcon_port,
        ) as rcon:
            await rcon.send("/save-off")
            backup = MinecraftBackup(
                rcon=rcon,
                server_path=settings.server_path,
                backup_path=settings.backup_destination,
            )
            await backup.backup()

        await asyncio.sleep(settings.backup_interval.total_seconds())


if __name__ == "__main__":
    asyncio.run(main())
