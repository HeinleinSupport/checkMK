#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Remove the given users from ``users.mk`` in place.

Written to the site and executed with its own Python (``python3 <file>``);
not imported by the test process.
"""

import sys
from typing import Any

from cmk.ccc import store
from cmk.utils import paths

# Remove the given users from users.mk in place; the site reloads it. Used to
# clean up users an LDAP sync imported on a remote (no openapi access there).
cfg_path = paths.omd_root / "etc/check_mk/multisite.d/wato/users.mk"


def _load() -> dict[str, Any]:
    ns: dict[str, Any] = {"multisite_users": {}}
    if cfg_path.exists():
        exec(cfg_path.read_text(), ns)
    return dict(ns.get("multisite_users", {}))


users = _load()
for user_id in sys.argv[1:]:
    users.pop(user_id, None)

cfg_path.parent.mkdir(parents=True, exist_ok=True)
store.save_to_mk_file(cfg_path, key="multisite_users", value=users)
