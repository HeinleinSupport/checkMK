#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Fixtures providing LDAP + SAML backends for composition tests.

Layered as:

* ``identity_directory`` — the static directory contents (users, etc.).
* ``ldap_server`` — the in-process :class:`MockLdapServer` LDAP backend.
* ``saml_idp`` — the in-process :class:`MockSamlIdp` SAML IdP backend; it
  knows the directory users directly.
* ``distributed_sites_with_identity`` — the central + two remote sites
  after LDAP+SAML are configured on the central and propagated to the
  remotes via config sync. The sites themselves are reused from the
  parent ``composition`` fixtures.

The backends run in-process, so the identity tests need no Docker daemon
or external services.
"""

from collections.abc import Iterator
from typing import Protocol

import pytest

from tests.composition.identity.directory import (
    default_directory,
    Directory,
    two_ldap_directories,
)
from tests.composition.identity.mock_ldap import MockLdapServer
from tests.composition.identity.mock_saml_idp import MockSamlIdp
from tests.composition.identity.site_setup import (
    configure_distributed_identity_providers,
)
from tests.testlib.site import Site

LdapBackend = MockLdapServer
SamlIdpBackend = MockSamlIdp


class InteractivePauser(Protocol):
    def __call__(self, *sites: Site, saml_connection_id: str) -> None: ...


def _noop_pauser(*sites: Site, saml_connection_id: str) -> None:
    del sites, saml_connection_id


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--interactive",
        action="store_true",
        default=False,
        help=(
            "Identity tests only: after setting up LDAP, SAML IdP, and the site(s), "
            "pause the test and print connection details so the site can be poked at "
            "from a browser. Press Enter on stdin to let the assertions run."
        ),
    )


@pytest.fixture(scope="session")
def identity_directory() -> Directory:
    return default_directory()


@pytest.fixture(scope="session")
def ldap_server(identity_directory: Directory) -> Iterator[LdapBackend]:
    """The in-process mock LDAP backend."""
    with MockLdapServer(directory=identity_directory) as server:
        yield server


@pytest.fixture(scope="session")
def saml_idp(identity_directory: Directory) -> Iterator[SamlIdpBackend]:
    """The in-process mock SAML IdP backend."""
    with MockSamlIdp(directory=identity_directory) as idp:
        yield idp


@pytest.fixture(scope="session")
def distributed_sites_with_identity(
    central_site: Site,
    remote_site: Site,
    remote_site_2: Site,
    ldap_server: LdapBackend,
    saml_idp: SamlIdpBackend,
) -> Iterator[tuple[Site, Site, Site, str]]:
    """Yield ``(central, remote_1, remote_2, saml_connection_id)``; setup runs on
    the central only and the remotes inherit it via config sync (CMK-33812)."""
    with configure_distributed_identity_providers(
        central_site=central_site,
        remote_sites=[remote_site, remote_site_2],
        ldap=ldap_server,
        idp=saml_idp,
    ) as saml_id:
        yield central_site, remote_site, remote_site_2, saml_id


@pytest.fixture
def two_ldap_backends() -> Iterator[tuple[LdapBackend, LdapBackend]]:
    """Two LDAP backends with distinct single-user directories (``alice`` / ``dave``),
    each serving its entries so an *active* connection's sync imports them."""
    dir_a, dir_b = two_ldap_directories()
    with (
        MockLdapServer(dir_a, name="mock-ldap-a", serve_entries=True) as ldap_a,
        MockLdapServer(dir_b, name="mock-ldap-b", serve_entries=True) as ldap_b,
    ):
        yield ldap_a, ldap_b


@pytest.fixture
def interactive_pause(
    request: pytest.FixtureRequest,
    ldap_server: LdapBackend,
    saml_idp: SamlIdpBackend,
    identity_directory: Directory,
) -> InteractivePauser:
    """Under ``--interactive``, print connection URLs/credentials and block on stdin
    before the assertions run; otherwise a no-op so tests can call it unconditionally."""
    if not request.config.getoption("--interactive"):
        return _noop_pauser

    capmanager = request.config.pluginmanager.getplugin("capturemanager")

    def _pause(*sites: Site, saml_connection_id: str) -> None:
        lines: list[str] = ["", "=" * 78, "Identity test interactive pause", "", "Sites:"]
        for site in sites:
            lines.append(f"  {site.id:<24} {site.internal_url}")
            lines.append(f"    cmkadmin password: {site.admin_password}")
        lines.append("")
        lines.append(f"SAML connection id: {saml_connection_id}")
        lines.append("")
        lines.append("Keycloak (IdP):")
        lines.append(f"  Admin console: {saml_idp.base_url}/admin/")
        lines.append(f"  Realm:         {saml_idp.realm_url}")
        lines.append(f"  Metadata:      {saml_idp.metadata_url}")
        lines.append(f"  Login:         {saml_idp.ADMIN_USER} / {saml_idp.ADMIN_PASSWORD}")
        lines.append("")
        lines.append("LDAP:")
        lines.append(f"  URL:           {ldap_server.host_url}")
        lines.append(f"  Bind DN:       {ldap_server.directory.admin_dn}")
        lines.append(f"  Bind password: {ldap_server.directory.admin_password}")
        lines.append("  Directory users (LDAP/SAML login credentials):")
        for user in identity_directory.users:
            lines.append(f"    {user.uid} / {user.password}")
        lines.append("")
        lines.append("=" * 78)
        lines.append("Press Enter to continue (the test assertions will then run)...")

        capmanager.suspend_global_capture(in_=True)
        try:
            print("\n".join(lines))
            input()
        finally:
            capmanager.resume_global_capture()

    return _pause
