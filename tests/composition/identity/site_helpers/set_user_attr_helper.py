#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Plant an attribute on one user's on-disk ``users.mk`` record.

Written to the site and executed with its own Python (``python3 <file>``);
not imported by the test process.
"""

import json
import sys
from typing import Any

from cmk.ccc import store
from cmk.utils import paths

# Plant an attribute on one user's users.mk record in place; the site reloads it.
cfg_path = paths.omd_root / "etc/check_mk/multisite.d/wato/users.mk"


def _load() -> dict[str, Any]:
    ns: dict[str, Any] = {"multisite_users": {}}
    if cfg_path.exists():
        exec(cfg_path.read_text(), ns)
    return dict(ns.get("multisite_users", {}))


user_id = sys.argv[1]
attribute = sys.argv[2]
value = json.loads(sys.stdin.read())["value"]

users = _load()
if user_id not in users:
    raise SystemExit(f"user {user_id!r} not present in users.mk")
record = dict(users[user_id])
record[attribute] = value
users[user_id] = record

cfg_path.parent.mkdir(parents=True, exist_ok=True)
store.save_to_mk_file(cfg_path, key="multisite_users", value=users)
