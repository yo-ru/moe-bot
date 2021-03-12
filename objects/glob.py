from typing import TYPE_CHECKING

import config  # imported for indirect use

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from cmyui import AsyncSQLPool, Version

__all__ = ("db", "http", "version")

db: "AsyncSQLPool"
http: "ClientSession"
version: "Version"