#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    SingleChoice,
    SingleChoiceElement,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic

_VALID_VALUES = frozenset(("auto", "xinetd", "systemd", "no_service"))


def migrate(value: object) -> Mapping[str, object]:
    if isinstance(value, dict) and "type" in value:
        return value
    if isinstance(value, str) and value in _VALID_VALUES:
        return {"type": value}
    raise ValueError(f"Unexpected value: {value!r}")


def _parameter_form_super_server() -> Dictionary:
    return Dictionary(
        title=Title("Checkmk agent network service (Linux)"),
        help_text=Help(
            "The Checkmk agent does not listen on its own for incoming network connections"
            " on Linux systems. By default, it makes use of so called super servers, which"
            " listen on the network and dispatch incoming requests to applications like"
            " the Checkmk agent. Baked agent packages come with service configurations for"
            " systemd and xinetd, preferring systemd. If you want to choose a specific super"
            " server, you can configure this rule. Optionally disable service installation"
            " completely, e.g. if you connect to the agent via SSH.\n"
            "Please note: The configured/determined service configuration will only get"
            " activated if the super server is compatible to a possibly configured IP restriction"
            ' rule set. See rule set "Allowed agent access via IP address".'
        ),
        elements={
            "type": DictElement(
                required=True,
                parameter_form=SingleChoice(
                    elements=[
                        SingleChoiceElement(
                            name="auto",
                            title=Title(
                                "Prefer systemd, fallback to xinetd if xinetd is available"
                            ),
                        ),
                        SingleChoiceElement(
                            name="xinetd",
                            title=Title("Install and activate xinetd service"),
                        ),
                        SingleChoiceElement(
                            name="systemd",
                            title=Title("Install and activate systemd service"),
                        ),
                        SingleChoiceElement(
                            name="no_service",
                            title=Title("Don't install Checkmk service"),
                        ),
                    ],
                    prefill=DefaultValue("auto"),
                ),
            ),
        },
        migrate=migrate,
    )


rule_spec_super_server = AgentConfig(
    name="super_server",
    title=Title("Checkmk agent network service (Linux)"),
    topic=Topic.LINUX,
    parameter_form=_parameter_form_super_server,
)
