import contextlib
import shutil
import tarfile
from collections.abc import AsyncIterator
from datetime import datetime, UTC
from pathlib import Path
from tempfile import TemporaryDirectory

from mc_backup._rcon import MinecraftClient


class MinecraftBackup:
    def __init__(
        self, rcon: MinecraftClient, server_path: Path, backup_path: Path
    ) -> None:
        self._rcon = rcon
        self._server_path = server_path
        self._backup_path = backup_path

    @contextlib.asynccontextmanager
    async def _disable_autosaving(self) -> AsyncIterator[None]:
        await self._rcon.send("/save-off")
        try:
            yield
        finally:
            await self._rcon.send("/save-on")

    async def backup(self) -> None:
        self._backup_path.mkdir(parents=True, exist_ok=True)
        world_dir = self._server_path.joinpath("world")

        with TemporaryDirectory(dir=self._backup_path) as tmp_dir:
            temp_path = Path(tmp_dir).joinpath("tmp")
            async with self._disable_autosaving():
                shutil.copytree(world_dir, temp_path)

            archive_nave = self._archive_name()

            with tarfile.open(
                self._backup_path.joinpath(archive_nave), "w:gz"
            ) as archive:
                archive.add(temp_path, arcname="world")

    def _archive_name(self) -> str:
        now_date = datetime.now(tz=UTC).date()
        count = len(list(self._backup_path.glob(f"{now_date}*.tar.gz")))
        return f"{now_date}-{count + 1}.tar.gz"
