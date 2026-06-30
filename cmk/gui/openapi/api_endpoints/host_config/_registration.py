#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from cmk.gui.openapi.framework.registry import VersionedEndpointRegistry

from .bulk_create_host import ENDPOINT_BULK_CREATE_HOST
from .bulk_delete_host import ENDPOINT_BULK_DELETE_HOST
from .bulk_update_host import ENDPOINT_BULK_UPDATE_HOST
from .create_cluster_host import ENDPOINT_CREATE_CLUSTER_HOST
from .create_host import ENDPOINT_CREATE_HOST
from .delete_host import ENDPOINT_DELETE_HOST
from .list_hosts import ENDPOINT_LIST_HOSTS
from .move_host import ENDPOINT_MOVE_HOST
from .rename_host import ENDPOINT_RENAME_HOST
from .show_host import ENDPOINT_SHOW_HOST
from .update_cluster_nodes import ENDPOINT_UPDATE_CLUSTER_NODES
from .update_host import ENDPOINT_UPDATE_HOST
from .wait_for_rename_completion import ENDPOINT_WAIT_FOR_RENAME_COMPLETION


def register(versioned_endpoint_registry: VersionedEndpointRegistry) -> None:
    versioned_endpoint_registry.register(ENDPOINT_BULK_CREATE_HOST)
    versioned_endpoint_registry.register(ENDPOINT_CREATE_CLUSTER_HOST)
    versioned_endpoint_registry.register(ENDPOINT_CREATE_HOST)
    versioned_endpoint_registry.register(ENDPOINT_LIST_HOSTS)
    versioned_endpoint_registry.register(ENDPOINT_SHOW_HOST)
    versioned_endpoint_registry.register(ENDPOINT_UPDATE_CLUSTER_NODES)
    versioned_endpoint_registry.register(ENDPOINT_UPDATE_HOST)
    versioned_endpoint_registry.register(ENDPOINT_BULK_UPDATE_HOST)
    versioned_endpoint_registry.register(ENDPOINT_DELETE_HOST)
    versioned_endpoint_registry.register(ENDPOINT_BULK_DELETE_HOST)
    versioned_endpoint_registry.register(ENDPOINT_MOVE_HOST)
    versioned_endpoint_registry.register(ENDPOINT_RENAME_HOST)
    versioned_endpoint_registry.register(ENDPOINT_WAIT_FOR_RENAME_COMPLETION)
