#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import abc
from collections.abc import Callable, Sequence
from typing import override

import cmk.ccc.plugin_registry

from cmk.gui.type_defs import PermissionName, RoleName
from cmk.gui.utils.speaklater import LazyString


class PermissionSection(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The identity of a permission section.
        One word, may contain alpha numeric characters"""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def title(self) -> str:
        """Display name representing the section"""
        raise NotImplementedError()

    @property
    def sort_index(self) -> int:
        """Number to sort the sections with"""
        return 50

    # TODO: Is this still needed?
    @property
    def do_sort(self) -> bool:
        """Whether or not to sort the permissions by title in this section"""
        return False


class PermissionSectionRegistry(cmk.ccc.plugin_registry.Registry[type[PermissionSection]]):
    @override
    def plugin_name(self, instance: type[PermissionSection]) -> str:
        return instance().name

    def get_sorted_sections(self) -> list[PermissionSection]:
        return sorted([s() for s in self.values()], key=lambda s: (s.sort_index, s.title))


permission_section_registry = PermissionSectionRegistry()


class Permission(abc.ABC):
    _sort_index = 0

    def __init__(
        self,
        section: type[PermissionSection],
        name: str,
        title: str | LazyString,
        description: str | LazyString,
        defaults: Sequence[RoleName],
    ) -> None:
        self._section = section
        self._name = name
        self._title = title
        self._description = description
        self._defaults = defaults
        self._sort_index = 0

    @property
    def section(self) -> type[PermissionSection]:
        return self._section

    @property
    def permission_name(self) -> str:
        """The identity of a permission (without it's section identity).
        One word, may contain alpha numeric characters"""
        return self._name

    @property
    def title(self) -> str:
        """Display name representing the permission"""
        return str(self._title)

    @property
    def description(self) -> str:
        """Text to explain the purpose of this permission"""
        return str(self._description)

    @property
    def defaults(self) -> Sequence[str]:
        """List of role IDs that have this permission by default"""
        return self._defaults

    @property
    def name(self) -> str:
        """The full identity of a permission (including the section identity)."""
        return ".".join((self.section().name, self.permission_name))

    @property
    def sort_index(self) -> int:
        """Number to sort the permission with"""
        return self._sort_index

    @sort_index.setter
    def sort_index(self, value: int) -> None:
        self._sort_index = value


class PermissionRegistry(cmk.ccc.plugin_registry.Registry[Permission]):
    def __init__(self) -> None:
        super().__init__()
        # TODO: Better make the sorting explicit in the future
        # used as auto incrementing counter to numerate the permissions in
        # the order they have been added.
        self._index_counter = 0

    @override
    def plugin_name(self, instance: Permission) -> str:
        return instance.name

    @override
    def registration_hook(self, instance: Permission) -> None:
        instance._sort_index = self._index_counter
        self._index_counter += 1

    def get_sorted_permissions(self, section: PermissionSection) -> list[Permission]:
        """Returns the sorted permissions of a section respecting the sorting config of the section"""
        permissions = [p for p in self.values() if p.section == section.__class__]

        if section.do_sort:
            return sorted(permissions, key=lambda p: (p.title, p.sort_index))
        return sorted(permissions, key=lambda p: p.sort_index)


permission_registry = PermissionRegistry()


def declare_permission_section(
    name: str, title: str, prio: int = 50, do_sort: bool = False
) -> None:
    cls = type(
        "LegacyPermissionSection%s" % name.title(),
        (PermissionSection,),
        {
            "name": name,
            "title": title,
            "sort_index": prio,
            "do_sort": do_sort,
        },
    )
    permission_section_registry.register(cls)


def declare_permission(
    name: PermissionName,
    title: str | LazyString,
    description: str | LazyString,
    defaults: Sequence[RoleName],
) -> None:
    section_name, permission_name = name.split(".", 1)

    permission_registry.register(
        Permission(
            section=permission_section_registry[section_name],
            name=permission_name,
            title=title,
            description=description,
            defaults=defaults,
        )
    )


_permission_declaration_functions = []


# Some module have a non-fixed list of permissions. For example for
# each user defined view there is also a permission. This list is
# not known at the time of the loading of the module - though. For
# that purpose module can register functions. These functions should
# just call declare_permission(). They are being called in the correct
# situations.
def declare_dynamic_permissions(func: Callable[[], None]) -> None:
    _permission_declaration_functions.append(func)


# This function needs to be called by all code that needs access
# to possible dynamic permissions
def load_dynamic_permissions() -> None:
    for func in _permission_declaration_functions:
        func()
