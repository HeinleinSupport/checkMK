#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import functools
import logging
from collections.abc import Callable
from pathlib import Path

from cmk.ccc.version import Edition, edition
from cmk.licensing.helper import init_logging


def _get_logger(log_dir: Path) -> logging.Logger:
    return functools.cache(init_logging)(log_dir)


class ActiveMetricSeriesRetrieverRegistry:
    def __init__(self) -> None:
        self.average_metric_series_retriever_function: Callable[[], int | None] | None = None

    def register(self, average_metric_series_retriever_function: Callable[[], int | None]) -> None:
        self.average_metric_series_retriever_function = average_metric_series_retriever_function


active_metric_series_retriever_registry = ActiveMetricSeriesRetrieverRegistry()


def get_average_active_metric_series(omd_root: Path, log_dir: Path) -> int | None:
    if active_metric_series_retriever_registry.average_metric_series_retriever_function is not None:
        try:
            return (
                active_metric_series_retriever_registry.average_metric_series_retriever_function()
            )
        except Exception as e:
            _get_logger(log_dir).error(
                "Error when retrieving the active metric series count (%(error_type)s): %(error)s",
                {"error_type": type(e).__name__, "error": e},
            )
    elif edition(omd_root) in [Edition.ULTIMATE, Edition.ULTIMATEMT, Edition.CLOUD]:
        _get_logger(log_dir).error(
            "There is no registered active metric series function, while it should"
        )
    return None
