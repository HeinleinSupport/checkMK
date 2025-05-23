#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Any, TypedDict

from cmk.agent_based.v2 import (
    check_levels,
    CheckResult,
    DiscoveryResult,
    get_average,
    get_rate,
    IgnoreResultsError,
    Metric,
    render,
    Result,
    Service,
    State,
)

Disk = Mapping[str, float]
Section = Mapping[str, Disk]

DISKSTAT_DISKLESS_PATTERN = re.compile("x?[shv]d[a-z]*[0-9]+")
DISKSTAT_DEFAULT_PARAMS = {
    "summary": True,
    "lvm": False,
    "vxvm": False,
    "diskless": False,
}


@dataclass
class NoIOSection:
    message: str = ""


def discovery_diskstat_generic(
    params: Sequence[Mapping[str, Any]],
    section: Iterable[str],
) -> DiscoveryResult:
    item_candidates = list(section)
    # Skip over on empty data
    if not item_candidates:
        return

    modes = params[0]

    if modes["summary"]:
        yield Service(item="SUMMARY")

    for name in item_candidates:
        if "physical" in modes and " " not in name and not DISKSTAT_DISKLESS_PATTERN.match(name):
            yield Service(item=name)

        if modes["lvm"] and name.startswith("LVM "):
            yield Service(item=name)

        if modes["vxvm"] and name.startswith("VxVM "):
            yield Service(item=name)

        if modes["diskless"] and DISKSTAT_DISKLESS_PATTERN.match(name):
            # Sort of partitions with disks - typical in XEN virtual setups.
            # Eg. there are xvda1, xvda2, but no xvda...
            yield Service(item=name)


def compute_rates_multiple_disks(
    disks: Section,
    value_store: MutableMapping[str, Any],
    single_disk_rate_computer: Callable[[Disk, MutableMapping[str, Any], str], Disk],
) -> Section:
    """Compute rates for multiple disks

    Args:
        disks: Dictionary with multiple disks: {'sda': {'read_ios': 7}}
        value_store: value store
        single_disk_rate_computer: function that computes rates for a single disk.
            1. parameter: disk: dictionary with absolute disk stats: {'read_ios': 20}
            2. parameter: value_store
            3. parameter: suffix to use for the value_store key (this value is
                needed because this function is normally called for the
                'SUMMARY' item. in order to distinguish the different
                'read_ios' of multiple disks, the key will be suffixed with the
                disk name before asking get_rate for the values.
            return value: dictionary with relative disk stats: {'read_ios': 1}

    Example:
        >>> from contextlib import suppress
        >>> VALUE_STORE = {}  # normally obtained via get_value_store()
        >>> THIS_TIME = 0  # either read from section or time.time()
        >>> DISKS_ABSOLUTE = {'sda': {'read_ios': 11}, 'sdb': {'read_ios': 22}}
        >>> def single_disk_rate_computer(disk_absolute, value_store, value_store_suffix):
        ...     return compute_rates(  # or use your own function
        ...         disk=disk_absolute,
        ...         value_store=value_store,
        ...         disk_name=value_store_suffix,
        ...         this_time=THIS_TIME)
        >>> with suppress(IgnoreResultsError):
        ...     # first computation will throw error as value_store is empty
        ...     compute_rates_multiple_disks(DISKS_ABSOLUTE, VALUE_STORE, single_disk_rate_computer)
        >>> THIS_TIME = 10
        >>> DISKS_ABSOLUTE = {'sda': {'read_ios': 22}, 'sdb': {'read_ios': 44}}
        >>> compute_rates_multiple_disks(DISKS_ABSOLUTE, VALUE_STORE, single_disk_rate_computer)
        {'sda': {'read_ios': 1.1}, 'sdb': {'read_ios': 2.2}}

    This may be used as input for summarize_disks.
    """
    disks_with_rates = {}
    ignore_res_excpt = None

    for disk_name, disk in disks.items():
        try:
            disks_with_rates[disk_name] = single_disk_rate_computer(
                disk,
                value_store,
                ".%s" % disk_name,
            )
        except IgnoreResultsError as excpt:
            ignore_res_excpt = excpt

    if ignore_res_excpt:
        raise ignore_res_excpt

    return disks_with_rates


_METRICS_TO_BE_AVERAGED = {
    "utilization",
    "latency",
    "read_latency",
    "write_latency",
    "queue_length",
}


def combine_disks(disks: Iterable[Disk]) -> Disk:
    # In summary mode we add up the throughput values, but
    # we average the other values for disks that have a throughput
    # > 0. Note: This is not very precise. Strictly spoken
    # we would need to do the summarization directly in the
    # parse function. But there we do not have information about
    # the physical multipath devices and would add up the traffic
    # of the paths with the traffice of the device itself....

    combined_disk: defaultdict[str, float] = defaultdict(float)
    # We do not set these settings explictly because some
    # devices may not provide all of them.
    # "read_ios"                   : 0.0,
    # "write_ios"                  : 0.0,
    # "read_throughput"            : 0.0,
    # "write_throughput"           : 0.0,
    # "utilization"                : 0.0,
    # "latency"                    : 0.0,
    # "average_request_size"       : 0.0,
    # "average_wait"               : 0.0,
    # "average_read_wait"          : 0.0,
    # "average_read_request_size"  : 0.0,
    # "average_write_wait"         : 0.0,
    # "average_write_request_size" : 0.0,
    # "queue_length"               : 0.0,
    # "read_ql"                    : 0.0,
    # "write_ql"                   : 0.0,
    n_contributions: defaultdict[str, int] = defaultdict(int)

    for disk in disks:
        for key, value in disk.items():
            combined_disk[key] += value
            n_contributions[key] += 1

    for key in combined_disk:
        if key.startswith("ave") or key in _METRICS_TO_BE_AVERAGED:
            combined_disk[key] /= n_contributions[key]

    return combined_disk


def summarize_disks(disks: Iterable[tuple[str, Disk]]) -> Disk:
    # we do not use a dictionary as input because we want to be able to have the same disk name
    # multiple times (cluster mode)
    # skip LVM devices for summary
    return combine_disks(disk for device, disk in disks if not device.startswith("LVM "))


class MetricSpecs(TypedDict, total=False):
    scale_by: float
    value_scale: float
    levels_key: str
    levels_scale: float
    render_func: Callable[[float], str]
    label: str
    in_service_output: bool


_METRICS: tuple[tuple[str, MetricSpecs], ...] = (
    (
        "utilization",
        {"render_func": render.percent, "scale_by": 100.0},
    ),
    (
        "read_throughput",
        {
            "render_func": render.iobandwidth,
            "label": "Read",
            "in_service_output": True,
        },
    ),
    (
        "write_throughput",
        {
            "render_func": render.iobandwidth,
            "label": "Write",
            "in_service_output": True,
        },
    ),
    (
        "average_wait",
        {
            "render_func": render.timespan,
        },
    ),
    (
        "average_read_wait",
        {
            "render_func": render.timespan,
        },
    ),
    (
        "average_write_wait",
        {
            "render_func": render.timespan,
        },
    ),
    (
        "queue_length",
        {
            "render_func": lambda x: "%.2f" % x,
            "label": "Average queue length",
        },
    ),
    (
        "read_ql",
        {
            "render_func": lambda x: "%.2f" % x,
            "label": "Average read queue length",
        },
    ),
    (
        "write_ql",
        {
            "render_func": lambda x: "%.2f" % x,
            "label": "Average write queue length",
        },
    ),
    (
        "read_ios",
        {
            "render_func": lambda x: "%.2f/s" % x,
            "label": "Read operations",
        },
    ),
    (
        "write_ios",
        {
            "render_func": lambda x: "%.2f/s" % x,
            "label": "Write operations",
        },
    ),
    (
        "latency",
        {
            "render_func": render.timespan,
            "in_service_output": True,
        },
    ),
    (
        "read_latency",
        {
            "render_func": render.timespan,
        },
    ),
    (
        "write_latency",
        {
            "render_func": render.timespan,
        },
    ),
)


def _get_averaged_disk(
    averaging: int,
    disk: Disk,
    value_store: MutableMapping,
    this_time: float,
) -> Generator[Result, None, Disk]:
    """Yield a result indicating averaging and return averaged disk

    Note: this check uses a simple method of averaging: As soon as averaging
    is turned on the actual metrics are *replaced* by the averaged ones. No
    duplication of performance data or check output here. This is because we
    have so many metrics...
    here, a value in seconds must be provided (preferably from the ruleset "diskstat"); note that
    the deprecated ruleset "disk_io" uses minutes for this field and is therefore incompatible
    with this function
    """
    yield Result(
        state=State.OK,
        notice="All values averaged over %s" % render.timespan(averaging),
    )
    return {
        key: get_average(
            value_store=value_store,
            # We add 'check_diskstat_dict' to the key to avoid possible overlap with keys
            # used in check plug-ins. For example, for the SUMMARY-item, the check plug-in
            # winperf_phydisk first computes all rates for all items using 'metric.item' as
            # key and then summarizes the disks. Hence, for a disk called 'avg', these keys
            # would be the same as the keys used here.
            key="check_diskstat_dict.%s.avg" % key,
            time=this_time,
            value=value,
            backlog_minutes=averaging / 60.0,
        )
        for key, value in list(disk.items())
        if isinstance(value, int | float)
    }


def compute_rates(
    *,
    disk: Disk,
    value_store: MutableMapping[str, Any],
    this_time: float,
    disk_name: str = "",
) -> Disk:
    """Compute rates for a single disk.

    Args:
        disk: Dictionary holding various disk metrics
        value_store: The value_store
        this_time: Monotonic time in seconds
        disk_name: Can be empty when used for a single disk item, if item ==
            'SUMMARIZE' the disk_name must hold the item name of the disk.

    Example:
        >>> from contextlib import suppress
        >>> VALUE_STORE = {} # use the real value_store via get_value_store()
        >>> DISK = {"read_throughput": 60000, "write_throughput": 0}
        >>> with suppress(IgnoreResultsError):
        ...     # first computation will throw error as value_store is empty
        ...     compute_rates(disk=DISK, value_store=VALUE_STORE, this_time=0)
        >>> DISK = {"read_throughput": 61024, "write_throughput": 1024*1024}
        >>> compute_rates(disk=DISK, value_store=VALUE_STORE, this_time=10)
        {'read_throughput': 102.4, 'write_throughput': 104857.6}

    """
    disk_with_rates = {}
    initialized = []
    for key, value in disk.items():
        counter = f"{key}{disk_name}"
        try:
            disk_with_rates[key] = get_rate(
                value_store,
                counter,
                this_time,
                value,
                raise_overflow=True,
            )
        except IgnoreResultsError:
            initialized.append(counter)
    if initialized:
        raise IgnoreResultsError(f"Initialized counters: {', '.join(initialized)}")
    return disk_with_rates


# Example:
# disks = { "sda" : {
#       'average_read_request_size'  : 0.0,
#       'average_read_wait'          : 0.0,
#       'average_request_size'       : 40569.90476190476,
#       'average_wait'               : 0.761904761904762,
#       'average_write_request_size' : 40569.90476190476,
#       'average_write_wait'         : 0.0007619047619047619,
#       'read_ios'                   : 0.0,
#       'read_throughput'            : 0.0,
#       'latency'                    : 0.00038095238095238096,
#       'utilization'                : 0.0006153846153846154,
#       'write_ios'                  : 1.6153846153846154,
#       'write_throughput'           : 65536.0,
#       'queue_length'               : 0.0,
#       'read_ql'                    : 0.0,
#       'write_ql'                   : 0.0,
# }}
def check_diskstat_dict_legacy(
    *,
    params: Mapping[str, Any],
    disk: Disk,
    value_store: MutableMapping,
    this_time: float,
) -> CheckResult:
    """Deprecated check_diskstat_dict function with adjusted behaviour

    tldr: Use the new function 'check_diskstat_dict' for new check plugin implementations. Only
    check plugins which relied on the old (previously faulty) behaviour should use this function.

    The original check_diskstat_dict function was not working as expected and was used by multiple
    check plugins. The problem was that the value for 'disk_utilization' was scaled by 100.0 only
    by the render_func and not for the associating metric value.

    There are different approaches to resolve this issue (scale both values by 100.0). Each
    approach must take into account for existing metric data (which at this point is already
    faulty):
        1. Make a metric translation with ScaleBy without touching the 'render_func'
        2. Make a metric translation with Rename and ScaleBy therefore having to introduce a new
        metric name for 'disk_utilization'

    While the second approach was considered to be more correct, 'disk_utilization' is quite a
    central metric name used by at least perfometers, graphs and dashboards. Changing the metric
    name increases the chance to break other parts. Therefore, the first approach was chosen with
    the addition that the existing 'faulty' check plugins use this function and new implementations
    should make use of the correctly behaving function 'check_diskstat_dict'. No new check plugins
    should use this function.

    A list of the affected check plugins can be found by inspecting the translation with the name
    'disk_utilization_check_diskstat_dict'

    """
    # we keep the old behaviour for the utilization metric and scale the metric values via the
    # metric translation (translation_disk_utilization_check_diskstat_dict)
    deprecated_utilization_metric: MetricSpecs = {
        "render_func": lambda x: render.percent(x * 100.0),
    }
    metrics = tuple(
        i if i[0] != "utilization" else ("utilization", deprecated_utilization_metric)
        for i in _METRICS
    )
    yield from _check_diskstat_dict(
        params=params,
        disk=disk,
        value_store=value_store,
        this_time=this_time,
        metrics=metrics,
    )


def check_diskstat_dict(
    *,
    params: Mapping[str, Any],
    disk: Disk,
    value_store: MutableMapping,
    this_time: float,
) -> CheckResult:
    return _check_diskstat_dict(
        params=params, disk=disk, value_store=value_store, this_time=this_time, metrics=_METRICS
    )


def _check_diskstat_dict(
    *,
    params: Mapping[str, Any],
    disk: Disk,
    value_store: MutableMapping,
    this_time: float,
    metrics: Iterable[tuple[str, MetricSpecs]] = _METRICS,
) -> CheckResult:
    if not disk:
        return

    averaging = params.get("average")
    if averaging:
        disk = yield from _get_averaged_disk(averaging, disk, value_store, this_time)

    for key, specs in metrics:
        metric_val = disk.get(key)
        if metric_val is not None:
            metric_val = metric_val * specs.get("scale_by", 1.0)
            levels = params.get(key)
            metric_name = "disk_" + key
            render_func = specs.get("render_func")
            label = specs.get("label") or key.replace("_", " ").capitalize()
            notice_only = not specs.get("in_service_output")

            yield from check_levels(
                metric_val,
                levels_upper=levels,
                metric_name=metric_name,
                render_func=render_func,
                label=label,
                notice_only=notice_only,
            )

    # make sure we have a latency.
    if "latency" not in disk and "average_write_wait" in disk and "average_read_wait" in disk:
        latency = max(disk["average_write_wait"], disk["average_read_wait"])
        levels = params.get("latency")
        yield from check_levels(
            latency,
            levels_upper=levels,
            metric_name="disk_latency",
            render_func=render.timespan,
            label="Latency",
        )

    # All the other metrics are currently not output in the plug-in output - simply because
    # of their amount. They are present as performance data and will shown in graphs.

    # Send everything as performance data now. Sort keys alphabetically
    for key in sorted(set(disk) - {m for m, _ in metrics}):
        value = disk[key]
        if isinstance(value, int | float):
            # Currently the levels are not shown in the perfdata
            yield Metric("disk_" + key, value)
