#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from dataclasses import asdict, dataclass

from cmk.gui import site_config
from cmk.gui.config import active_config
from cmk.gui.http import Request
from cmk.gui.i18n import _
from cmk.gui.logged_in import user
from cmk.gui.main_menu import MainMenuRegistry
from cmk.gui.main_menu_types import MainMenuItem
from cmk.gui.utils.urls import makeuri
from cmk.shared_typing.main_menu import (
    NavItemIdEnum,
    NavItemShortcut,
    NavItemVueApp,
    NavVueAppIdEnum,
)


@dataclass(frozen=True, kw_only=True)
class ChangesMenuItem:
    activate_changes_url: str
    user_has_activate_foreign: bool
    user_name: str


def _hide_menu() -> bool:
    if not user.may("wato.activate"):
        return True
    return (
        site_config.is_distributed_setup_remote_site(active_config.sites)
        and not active_config.wato_enabled
    )


def _get_changes_app(request: Request) -> NavItemVueApp:
    return NavItemVueApp(
        id=NavVueAppIdEnum.cmk_activate_changes,
        data=asdict(
            ChangesMenuItem(
                activate_changes_url=makeuri(
                    request,
                    addvars=[("mode", "changelog")],
                    filename="wato.py",
                ),
                user_has_activate_foreign=user.may("wato.activateforeign"),
                user_name=user.ident,
            )
        ),
    )


def register(mega_menu_registry: MainMenuRegistry) -> None:
    mega_menu_registry.register(
        MainMenuItem(
            id=NavItemIdEnum.changes,
            title=_("Changes"),
            sort_index=17,
            topics=None,
            shortcut=NavItemShortcut(key="n", alt=True),
            hide=_hide_menu,
            get_vue_app=_get_changes_app,
            hint=_("Activate configured changes to see in monitoring"),
        )
    )
