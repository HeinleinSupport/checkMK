#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Set or clear per-site authentication_connections in the central's ``sites.mk``.

Written to the site and executed with its own Python (``python3 <file>``);
not imported by the test process.
"""

import json
import sys
import time
import uuid
from typing import Any

from cmk.ccc import store
from cmk.utils import paths

# The central's sites.mk carries the per-site auth/sync connection settings;
# remotes inherit both at snapshot time (CMK-33812), so we touch only the
# central's own entry.
cfg_path = paths.omd_root / "etc/check_mk/multisite.d/sites.mk"


def _load_sites() -> dict[str, Any]:
    ns: dict[str, Any] = {"sites": {}}
    if cfg_path.exists():
        exec(cfg_path.read_text(), ns)
    return dict(ns.get("sites", {}))


def _coerce_entry(raw: list[object]) -> tuple[object, object]:
    # JSON has no tuples: restore the (kind, payload) tuple the runtime expects.
    kind, payload = raw
    return (kind, payload)


def _mark_dirty(target_site_id: str) -> None:
    # Replace the central's per-remote pending-changes log with one
    # ``edit-sites`` entry so the next activation pushes a snapshot (a bare
    # sites.mk edit records no change). The old file is removed first to drop
    # stale changes the push would reject. Format: ABCAppendStore, repr(dict)
    # entries NUL-separated; force_sync/force_restart skip the domain checks.
    entry: dict[str, object] = {
        "id": str(uuid.uuid4()),
        "action_name": "edit-sites",
        "text": "Per-site authentication_connections override (test helper)",
        "object": None,
        "user_id": "cmkadmin",
        "domains": [],
        "time": time.time(),
        "force_sync": True,
        "force_restart": True,
        "force_apache_reload": False,
        "domain_settings": {},
        "prevent_discard_changes": False,
        "diff_text": None,
    }
    changes_path = paths.var_dir / "wato" / f"replication_changes_{target_site_id}.mk"
    changes_path.parent.mkdir(parents=True, exist_ok=True)
    changes_path.unlink(missing_ok=True)
    with changes_path.open("wb") as f:
        f.write(repr(entry).encode("utf-8") + b"\0")


mode = sys.argv[1]
site_id = sys.argv[2]
if mode == "mark-dirty":
    _mark_dirty(site_id)
    sys.exit(0)
sites = _load_sites()
site_cfg = dict(sites.get(site_id, {}))
if mode == "set":
    payload = json.loads(sys.stdin.read())
    site_cfg["authentication_connections"] = [
        _coerce_entry(e) for e in payload["authentication_connections"]
    ]
    site_cfg["user_attribute_sync_connections"] = list(payload["user_attribute_sync_connections"])
elif mode == "clear":
    site_cfg.pop("authentication_connections", None)
    site_cfg.pop("user_attribute_sync_connections", None)
else:
    raise SystemExit(f"unknown mode: {mode}")
sites[site_id] = site_cfg
store.save_to_mk_file(cfg_path, key="sites", value=sites)
