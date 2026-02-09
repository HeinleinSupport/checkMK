#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from collections.abc import Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    Metric,
    Result,
    Service,
    State,
)
from cmk.plugins.lib.humidity import check_humidity
from cmk.plugins.lib.temperature import check_temperature, TempParamType

type Section = Mapping[str, Mapping[str, str]]


def _compose_item(sensor_id: str, sensor: Mapping[str, str]) -> str:
    num = re.sub("sensor", "", sensor_id)
    return f"{sensor['name']} Sensor {num}" if "name" in sensor else f"Sensor {num}"


def _match_function_or_unit(
    sensor_data: Mapping[str, str], function: str, unit: str | None = None
) -> bool:
    return sensor_data.get("function") == function or (
        unit is not None and sensor_data.get("unit") == unit
    )


def discover_allnet_ip_sensoric_tension(section: Section) -> DiscoveryResult:
    yield from (
        Service(item=_compose_item(sensor, sensor_data))
        for sensor, sensor_data in section.items()
        if _match_function_or_unit(sensor_data, "12")
    )


def check_allnet_ip_sensoric_tension(item: str, section: Section) -> CheckResult:
    sensor_id = "sensor" + re.sub(".+Sensor ", "", item)

    if sensor_id not in section:
        return

    value = float(section[sensor_id]["value_float"])

    yield Result(
        state=State.OK if value == 0 else State.CRIT,
        summary=f"{value:.0f}% of the normal level",
    )
    yield Metric("tension", value, boundaries=(0, 100))


check_plugin_allnet_ip_sensoric_tension = CheckPlugin(
    name="allnet_ip_sensoric_tension",
    service_name="Electric Tension %s",
    sections=["allnet_ip_sensoric"],
    discovery_function=discover_allnet_ip_sensoric_tension,
    check_function=check_allnet_ip_sensoric_tension,
)


def discover_allnet_ip_sensoric_temp(section: Section) -> DiscoveryResult:
    yield from (
        Service(item=_compose_item(sensor, sensor_data))
        for sensor, sensor_data in section.items()
        if _match_function_or_unit(sensor_data, "1", "°C")
    )


def check_allnet_ip_sensoric_temp(
    item: str, params: TempParamType, section: Section
) -> CheckResult:
    sensor_id = "sensor" + re.sub(".+Sensor ", "", item)

    if sensor_id not in section:
        return

    yield from check_temperature(
        float(section[sensor_id]["value_float"]),
        params,
        unique_name=item,
        value_store=get_value_store(),
    )


check_plugin_allnet_ip_sensoric_temp = CheckPlugin(
    name="allnet_ip_sensoric_temp",
    service_name="Temperature %s",
    sections=["allnet_ip_sensoric"],
    discovery_function=discover_allnet_ip_sensoric_temp,
    check_function=check_allnet_ip_sensoric_temp,
    check_ruleset_name="temperature",
    check_default_parameters={"levels": (35.0, 40.0)},
)


def discover_allnet_ip_sensoric_humidity(section: Section) -> DiscoveryResult:
    yield from (
        Service(item=_compose_item(sensor, sensor_data))
        for sensor, sensor_data in section.items()
        if _match_function_or_unit(sensor_data, "2", "%")
    )


def check_allnet_ip_sensoric_humidity(
    item: str, params: Mapping[str, object], section: Section
) -> CheckResult:
    sensor_id = "sensor" + re.sub(".+Sensor ", "", item)
    if sensor_id not in section:
        return

    yield from check_humidity(float(section[sensor_id]["value_float"]), params)


check_plugin_allnet_ip_sensoric_humidity = CheckPlugin(
    name="allnet_ip_sensoric_humidity",
    service_name="Humidity %s",
    sections=["allnet_ip_sensoric"],
    discovery_function=discover_allnet_ip_sensoric_humidity,
    check_function=check_allnet_ip_sensoric_humidity,
    check_ruleset_name="humidity",
    check_default_parameters={
        "levels": (60.0, 65.0),
        "levels_lower": (40.0, 35.0),
    },
)


def discover_allnet_ip_sensoric_pressure(section: Section) -> DiscoveryResult:
    yield from (
        Service(item=_compose_item(sensor, sensor_data))
        for sensor, sensor_data in section.items()
        if _match_function_or_unit(sensor_data, "16", "hpa")
    )


def check_allnet_ip_sensoric_pressure(item: str, section: Section) -> CheckResult:
    sensor_id = "sensor" + re.sub(".+Sensor ", "", item)

    if sensor_id not in section:
        return

    pressure = float(section[sensor_id]["value_float"]) / 1000

    yield Result(state=State.OK, summary=f"{pressure:0.5f} bar")
    yield Metric("pressure", pressure, boundaries=(0, None))


check_plugin_allnet_ip_sensoric_pressure = CheckPlugin(
    name="allnet_ip_sensoric_pressure",
    service_name="Pressure %s",
    sections=["allnet_ip_sensoric"],
    discovery_function=discover_allnet_ip_sensoric_pressure,
    check_function=check_allnet_ip_sensoric_pressure,
)
