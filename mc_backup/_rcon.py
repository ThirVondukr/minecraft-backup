# Code vendored from https://github.com/MrReacher/async-mcrcon

import asyncio
import struct
from asyncio import StreamReader, StreamWriter
from types import TracebackType
from typing import Self


class ClientError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class MinecraftClient:
    def __init__(self, host: str, port: int, password: str) -> None:
        self.host = host
        self.port = port
        self.password = password

        self._authenticated = False
        self._reader: StreamReader | None = None
        self._writer: StreamWriter | None = None

    async def __aenter__(self) -> Self:
        if not self._writer:
            self._reader, self._writer = await asyncio.open_connection(
                self.host, self.port
            )
            await self._authenticate()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._writer:
            self._writer.close()

    async def _authenticate(self) -> None:
        if not self._authenticated:
            await self._send(3, self.password)
            self._authenticated = True

    async def _read_data(self, legnth: int) -> bytes:
        if not self._reader:
            raise ValueError

        data = b""
        while len(data) < legnth:
            data += await self._reader.read(legnth - len(data))

        return data

    async def _send(self, typen: int, message: str) -> str:
        if not self._writer:
            msg = "Not connected."
            raise ClientError(msg)

        out = struct.pack("<li", 0, typen) + message.encode("utf8") + b"\x00\x00"
        out_len = struct.pack("<i", len(out))
        self._writer.write(out_len + out)

        in_len = struct.unpack("<i", await self._read_data(4))
        in_payload = await self._read_data(in_len[0])

        in_id, in_type = struct.unpack("<ii", in_payload[:8])
        in_data, in_padd = in_payload[8:-2], in_payload[-2:]

        if in_padd != b"\x00\x00":
            msg = "Incorrect padding."
            raise ClientError(msg)
        if in_id == -1:
            msg = "Incorrect password."
            raise InvalidPasswordError(msg)

        return in_data.decode("utf8")

    async def send(self, cmd: str) -> str:
        result = await self._send(2, cmd)
        await asyncio.sleep(0.003)  # unsure about this
        return result
