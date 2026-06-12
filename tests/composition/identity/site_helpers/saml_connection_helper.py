#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Upsert or delete a SAML ``user_connections.mk`` entry (and its SP signing cert) on disk.

Written to the site and executed with its own Python (``python3 <file>``);
not imported by the test process.
"""

import json
import sys
from typing import Any

from cmk.ccc import store
from cmk.utils import paths

# Bypass UserConnectionConfigFile.save() (boots the WSGI app); write the
# plain ``user_connections = [...]`` file directly, the site reloads it.
cfg_path = paths.omd_root / "etc/check_mk/multisite.d/wato/user_connections.mk"


def _load() -> list[dict[str, Any]]:
    if not cfg_path.exists():
        return []
    # Pre-bind the name: the .mk file may use ``=`` or ``.append(...)`` form.
    ns: dict[str, Any] = {"user_connections": []}
    exec(cfg_path.read_text(), ns)
    return list(ns.get("user_connections", []))


def _materialize_signing_cert(connection_id: str) -> None:
    # The bypassed save() normally writes the SP signing keypair; without it
    # pysaml2 fails to sign the AuthnRequest. write_certificate_files needs a
    # request context we lack, so use the lower-level crypto primitives.
    from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]

    from cmk.ccc.site import omd_site
    from cmk.crypto.certificate import (
        CertificateWithPrivateKey,
        PersistedCertificateWithPrivateKey,
    )
    from cmk.gui.nonfree.pro.saml2_auth._config import signature_certificate_paths

    paths_ = signature_certificate_paths(connection_id).builtin
    if paths_.private.is_file() and paths_.public.is_file():
        return
    bundle = CertificateWithPrivateKey.generate_self_signed(
        common_name="Checkmk SAML2 Service",
        organization=f"Checkmk Site {omd_site()}",
        expiry=relativedelta(days=+90),
        key_size=4096,
    )
    PersistedCertificateWithPrivateKey.persist(bundle, paths_.public, paths_.private)


mode = sys.argv[1]
existing = _load()
if mode == "upsert":
    payload = json.loads(sys.stdin.read())
    existing = [c for c in existing if c.get("id") != payload["id"]]
    existing.append(payload)
    _materialize_signing_cert(payload["id"])
elif mode == "delete":
    target_id = sys.argv[2]
    existing = [c for c in existing if c.get("id") != target_id]
else:
    raise SystemExit(f"unknown mode: {mode}")

cfg_path.parent.mkdir(parents=True, exist_ok=True)
store.save_to_mk_file(cfg_path, key="user_connections", value=existing)
