#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from zlib import compress

import pytest

from cmk.agent_receiver.agent_receiver.decompression import (
    DecompressionError,
    Decompressor,
)


def test_decompressor_zlib_round_trip() -> None:
    assert Decompressor("zlib")(compress(b"blablub")) == b"blablub"


def test_zlib_decompress_round_trip() -> None:
    assert Decompressor._zlib_decompress(compress(b"blablub")) == b"blablub"  # noqa: SLF001


def test_zlib_decompress_invalid_data() -> None:
    with pytest.raises(DecompressionError):
        Decompressor._zlib_decompress(b"blablub")  # noqa: SLF001
