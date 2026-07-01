#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final, Literal, override

from cmk.ccc.plugin_registry import Registry
from cmk.gui.utils.loading_transition import LoadingTransition
from cmk.gui.utils.roles import UserPermissions
from cmk.shared_typing.unified_search import ProviderName


@dataclass
class MatchItem:
    title: str
    topic: str
    url: str
    match_texts: Iterable[str]
    loading_transition: LoadingTransition | None = None

    def __post_init__(self) -> None:
        self.match_texts = [match_text.lower() for match_text in self.match_texts]


MatchItems = Iterable[MatchItem]
MatchItemsByTopic = dict[str, MatchItems]


class ABCMatchItemGenerator(ABC):
    def __init__(
        self,
        name: str,
        *,
        provider: Literal["customize", "monitoring", "setup"] = "setup",
    ) -> None:
        self.name: Final[str] = name
        self.provider: Final[ProviderName] = ProviderName(provider)

    @override
    def __hash__(self) -> int:
        return hash(self.name)

    @abstractmethod
    def generate_match_items(self, user_permissions: UserPermissions) -> MatchItems: ...

    @staticmethod
    @abstractmethod
    def is_affected_by_change(change_action_name: str) -> bool: ...

    @property
    @abstractmethod
    def is_localization_dependent(self) -> bool: ...


class MatchItemGeneratorRegistry(Registry[ABCMatchItemGenerator]):
    def __init__(self) -> None:
        super().__init__()
        self._categories_cache: dict[ProviderName, frozenset[str]] = {}

    @override
    def plugin_name(self, instance: ABCMatchItemGenerator) -> str:
        return instance.name

    def provider_for(self, category: str) -> ProviderName | None:
        if category not in self:
            return None

        return self[category].provider

    def categories_for(self, provider: ProviderName) -> frozenset[str]:
        if provider not in self._categories_cache:
            self._categories_cache[provider] = frozenset(
                name for name in self if self.provider_for(name) is provider
            )
        return self._categories_cache[provider]


match_item_generator_registry = MatchItemGeneratorRegistry()
