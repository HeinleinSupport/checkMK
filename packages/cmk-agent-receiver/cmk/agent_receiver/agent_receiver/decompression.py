#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from enum import Enum
from zlib import decompress
from zlib import error as zlibError


class DecompressionError(Exception): ...


class Decompressor(Enum):
    ZLIB = "zlib"

    def __call__(self, data: bytes) -> bytes:
        return {Decompressor.ZLIB: Decompressor._zlib_decompress}[self](data)

    @staticmethod
    def _zlib_decompress(data: bytes) -> bytes:
        try:
            return decompress(data)
        except zlibError as e:
            raise DecompressionError(f"Decompression with zlib failed: {e}") from e
