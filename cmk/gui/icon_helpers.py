#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.gui.type_defs import DynamicIcon, IconNames, StaticIcon
from cmk.shared_typing.main_menu import (
    DefaultIcon,
    EmblemIcon,
    UserIcon,
)
from cmk.shared_typing.main_menu import DynamicIcon as SharedDynamicIcon


def migrate_to_static_icon(icon: SharedDynamicIcon | None) -> StaticIcon | None:
    if not icon:
        return None

    if isinstance(icon, EmblemIcon):
        return StaticIcon(IconNames[icon.icon.id.replace("-", "_")], emblem=icon.emblem)

    return StaticIcon(IconNames[icon.id.replace("-", "_")])


def migrate_to_dynamic_icon(
    icon: str | StaticIcon | DynamicIcon | SharedDynamicIcon | None,
) -> SharedDynamicIcon | None:
    if not icon:
        return None

    if isinstance(icon, UserIcon) or isinstance(icon, DefaultIcon) or isinstance(icon, EmblemIcon):
        return icon

    if isinstance(icon, str):
        return DefaultIcon(id=IconNames[icon.replace("-", "_")])

    if isinstance(icon, StaticIcon):
        default_icon = DefaultIcon(id=icon.icon)
        if icon.emblem:
            return EmblemIcon(icon=default_icon, emblem=icon.emblem)

        return default_icon

    if icon["icon"]:
        default_icon = DefaultIcon(id=IconNames[icon["icon"].replace("-", "_")])
        if icon["emblem"]:
            return EmblemIcon(icon=default_icon, emblem=icon["emblem"])

        return default_icon

    return None
