#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from dataclasses import asdict, dataclass

from cmk.gui import site_config
from cmk.gui.config import active_config
from cmk.gui.http import Request
from cmk.gui.i18n import _l
from cmk.gui.logged_in import LoggedInUser, user
from cmk.gui.main_menu import MainMenuRegistry
from cmk.gui.main_menu_types import ConfigurableMainMenuItem, MainMenuItem, MainMenuLinkItem
from cmk.gui.utils.urls import makeuri, makeuri_contextless
from cmk.shared_typing.main_menu import (
    ColorEnum,
    NavItemBadge,
    NavItemBadgeEnum,
    NavItemIdEnum,
    NavItemShortcut,
    NavItemType,
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
                    delvars="start_url",
                ),
                user_has_activate_foreign=user.may("wato.activateforeign"),
                user_name=user.ident,
            )
        ),
    )


def get_activate_changes_full_page_url(request: Request) -> str:
    return makeuri_contextless(
        request,
        vars_=[("mode", "changelog")],
        filename="wato.py",
    )


def get_activate_changes_nav_item_instance(
    item: ConfigurableMainMenuItem, user: LoggedInUser
) -> MainMenuItem | MainMenuLinkItem:
    if user.attributes.get("navbar_changes_action") == "full_page":
        return MainMenuLinkItem(
            id=item.id,
            title=item.title,
            sort_index=item.sort_index,
            shortcut=item.shortcut,
            badge=item.badge,
            hint=item.hint,
            url=None,
            get_url=get_activate_changes_full_page_url,
            target="main",
        )

    return MainMenuItem(
        id=item.id,
        title=item.title,
        sort_index=item.sort_index,
        shortcut=item.shortcut,
        badge=item.badge,
        hint=item.hint,
        hide=_hide_menu,
        get_vue_app=_get_changes_app,
    )


def register(mega_menu_registry: MainMenuRegistry) -> None:
    mega_menu_registry.register(
        ConfigurableMainMenuItem(
            id=NavItemIdEnum.changes,
            title=_l("Changes"),
            sort_index=17,
            shortcut=NavItemShortcut(key="n", alt=True),
            type=NavItemType.configurable,
            get_item_instance=get_activate_changes_nav_item_instance,
            badge=NavItemBadge(
                mode=NavItemBadgeEnum.num_pending_changes,
                color=ColorEnum.warning,
                url="ajax_sidebar_get_number_of_pending_changes.py",
                interval_in_seconds=3,
            ),
            hint=_l("Activate pending changes"),
        )
    )
