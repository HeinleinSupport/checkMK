#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Reusable per-site LDAP + SAML configuration for the test framework."""

import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from tests.composition.identity.mock_ldap import MockLdapServer
from tests.composition.identity.mock_saml_idp import MockSamlIdp
from tests.testlib.site import Site

LdapBackend = MockLdapServer
SamlIdpBackend = MockSamlIdp

logger = logging.getLogger("identity-tests")

_SITE_HELPER_DIR = Path(__file__).parent / "site_helpers"


def _read_site_helper(name: str) -> str:
    """Return the source of an on-site helper script under ``site_helpers/``."""
    return (_SITE_HELPER_DIR / name).read_text()


LDAP_CONNECTION_ID = "test_ldap"
LDAP_CONNECTION_ID_A = "test_ldap_a"
LDAP_CONNECTION_ID_B = "test_ldap_b"
SAML_CONNECTION_ID = "test_saml"
_HELPER_REL_PATH = "tmp/identity_saml_helper.py"
_SITES_AUTH_HELPER_REL_PATH = "tmp/identity_sites_auth_helper.py"


def read_user_connector(site: Site, user_id: str) -> str | None:
    """Return ``user_id``'s ``connector`` parsed from the site's on-disk ``users.mk``
    (works on a remote where ``site.openapi`` would 401); ``None`` if absent."""
    try:
        content = site.read_file("etc/check_mk/multisite.d/wato/users.mk")
    except Exception:
        return None
    ns: dict[str, object] = {"multisite_users": {}}
    try:
        exec(content, ns)
    except Exception:
        logger.exception("Failed to parse users.mk on %s", site.id)
        return None
    users = ns.get("multisite_users")
    if not isinstance(users, dict):
        return None
    user = users.get(user_id)
    if not isinstance(user, dict):
        return None
    connector = user.get("connector")
    return connector if isinstance(connector, str) else None


def read_user_record(site: Site, user_id: str) -> dict[str, object] | None:
    """Return the full on-disk ``users.mk`` record for ``user_id`` (or ``None``)."""
    try:
        content = site.read_file("etc/check_mk/multisite.d/wato/users.mk")
    except Exception:
        return None
    ns: dict[str, object] = {"multisite_users": {}}
    try:
        exec(content, ns)
    except Exception:
        logger.exception("Failed to parse users.mk on %s", site.id)
        return None
    users = ns.get("multisite_users")
    if not isinstance(users, dict):
        return None
    record = users.get(user_id)
    return record if isinstance(record, dict) else None


def read_user_connection(site: Site, connection_id: str) -> dict[str, object] | None:
    """Return the synced ``user_connections.mk`` entry ``connection_id`` (or ``None``);
    reading it on a remote proves the central-only connector reached it via config sync."""
    try:
        content = site.read_file("etc/check_mk/multisite.d/wato/user_connections.mk")
    except Exception:
        return None
    ns: dict[str, object] = {"user_connections": []}
    try:
        exec(content, ns)
    except Exception:
        logger.exception("Failed to parse user_connections.mk on %s", site.id)
        return None
    connections = ns.get("user_connections")
    if not isinstance(connections, list):
        return None
    for connection in connections:
        if isinstance(connection, dict) and connection.get("id") == connection_id:
            return connection
    return None


_SET_USER_ATTR_HELPER_REL_PATH = "tmp/identity_set_user_attr_helper.py"
_SET_USER_ATTR_HELPER_SCRIPT = _read_site_helper("set_user_attr_helper.py")


@contextmanager
def _staged_set_user_attr_helper(site: Site) -> Iterator[str]:
    """Drop the users.mk attribute helper into the site and remove it on exit."""
    site.write_file(_SET_USER_ATTR_HELPER_REL_PATH, _SET_USER_ATTR_HELPER_SCRIPT)
    try:
        yield site.path(_SET_USER_ATTR_HELPER_REL_PATH).as_posix()
    finally:
        site.delete_file(_SET_USER_ATTR_HELPER_REL_PATH)


def set_user_attribute_on_disk(site: Site, user_id: str, attribute: str, value: object) -> None:
    """Plant ``attribute=value`` on ``user_id``'s on-disk ``users.mk`` record."""
    with _staged_set_user_attr_helper(site) as helper:
        site.check_output(
            ["python3", helper, user_id, attribute],
            input_=json.dumps({"value": value}),
        )


def read_central_authentication_connections(
    central_site: Site,
) -> dict[str, list[tuple[str, object]]]:
    """Return ``{site_id: authentication_connections}`` from the central's ``sites.mk``
    (empty dict if missing/unreadable)."""
    try:
        content = central_site.read_file("etc/check_mk/multisite.d/sites.mk")
    except Exception:
        return {}
    ns: dict[str, object] = {"sites": {}}
    try:
        exec(content, ns)
    except Exception:
        logger.exception("Failed to parse sites.mk on %s", central_site.id)
        return {}
    sites = ns.get("sites")
    if not isinstance(sites, dict):
        return {}
    return {
        site_id: list(cfg.get("authentication_connections", []))
        for site_id, cfg in sites.items()
        if isinstance(cfg, dict)
    }


def clear_remote_pending_changes(*remotes: Site) -> None:
    """Delete every remote's pending-change log so a later central snapshot push
    isn't refused with "pending changes that would get lost" (no openapi override)."""
    for remote in remotes:
        try:
            remote.delete_file(f"var/check_mk/wato/replication_changes_{remote.id}.mk")
        except Exception:
            logger.exception("Failed to clear pending changes on %s", remote.id)


def site_saml_endpoints(
    site: Site, connection_id: str = SAML_CONNECTION_ID
) -> tuple[str, str, str]:
    """Return (checkmk_server_url, sp_entity_id, sp_acs_url) for ``site``, computed
    test-side so the SP can be registered with the IdP before the connection exists."""
    parsed = urlparse(site.internal_url)
    checkmk_server_url = f"{parsed.scheme}://{parsed.netloc}"
    base = site.internal_url.rstrip("/")
    entity_id = f"{base}/saml_metadata.py"
    acs_url = f"{base}/saml_acs.py?acs"
    return checkmk_server_url, entity_id, acs_url


@contextmanager
def configure_ldap_connection(site: Site, ldap: LdapBackend) -> Iterator[None]:
    """Create and tear down an LDAP connection on ``site`` via the REST API.

    ``create_users="on_login"`` stops the sync job from provisioning LDAP-owned
    records that would lock SAML out of the same user; combined with an empty
    ``user_attribute_sync_connections`` this keeps LDAP configured but dormant.
    """
    directory = ldap.directory
    site.openapi.ldap_connection.create(
        LDAP_CONNECTION_ID,
        user_base_dn=directory.users_dn,
        user_search_filter="(objectclass=inetOrgPerson)",
        user_id_attribute="uid",
        group_base_dn=directory.users_dn,
        group_search_filter="(objectclass=organizationalUnit)",
        ldap_server=f"127.0.0.1:{ldap.host_port}",
        bind_dn=directory.admin_dn,
        password=directory.admin_password,
        create_users="on_login",
    )
    try:
        yield
    finally:
        try:
            site.openapi.ldap_connection.delete(LDAP_CONNECTION_ID)
        except Exception:
            logger.exception("Failed to delete LDAP connection on %s", site.id)


@contextmanager
def configure_two_ldap_sync_connections(
    site: Site, ldap_a: LdapBackend, ldap_b: LdapBackend
) -> Iterator[tuple[str, str]]:
    """Create two sync-enabled OpenLDAP connections (one per backend) on ``site``.

    Each connection imports its own directory's users on a userdb sync, so a sync
    pulls in users from both directories. Yields
    ``(connection_id_a, connection_id_b)``. The connections are created on the
    central and reach the remotes via config sync.
    """
    created: list[str] = []
    try:
        for connection_id, ldap in (
            (LDAP_CONNECTION_ID_A, ldap_a),
            (LDAP_CONNECTION_ID_B, ldap_b),
        ):
            directory = ldap.directory
            site.openapi.ldap_connection.create(
                connection_id,
                user_base_dn=directory.users_dn,
                user_search_filter="(objectclass=inetOrgPerson)",
                user_id_attribute="uid",
                group_base_dn=directory.users_dn,
                group_search_filter="(objectclass=organizationalUnit)",
                ldap_server=f"127.0.0.1:{ldap.host_port}",
                bind_dn=directory.admin_dn,
                password=directory.admin_password,
                create_users="on_sync",
                directory_type="open_ldap",
                # Long interval so no periodic background sync fires against the
                # mocks during the test; the test drives one explicit enforced sync.
                sync_interval_minutes=24 * 60,
            )
            created.append(connection_id)
        yield LDAP_CONNECTION_ID_A, LDAP_CONNECTION_ID_B
    finally:
        for connection_id in created:
            try:
                site.openapi.ldap_connection.delete(connection_id)
            except Exception:
                logger.exception(
                    "Failed to delete LDAP connection %s on %s", connection_id, site.id
                )


_SAML_HELPER_SCRIPT = _read_site_helper("saml_connection_helper.py")


def _saml_connection_payload(
    site: Site,
    idp: SamlIdpBackend,
    connection_id: str,
) -> dict[str, object]:
    """Build the on-disk SAMLUserConnectionConfig dict for ``site`` (built directly
    since the REST schema requires https:// but test sites listen on plain HTTP)."""
    checkmk_server_url, entity_id, acs_url = site_saml_endpoints(site, connection_id)
    return {
        "type": "saml2",
        "version": "1.0.0",
        "id": connection_id,
        "name": "Composition test SAML",
        "description": "containerized SAML IdP for composition tests",
        "comment": "",
        "docu_url": "",
        "disabled": False,
        "checkmk_entity_id": entity_id,
        "checkmk_metadata_endpoint": f"{entity_id}?RelayState={connection_id}",
        "checkmk_assertion_consumer_service_endpoint": acs_url,
        "checkmk_server_url": checkmk_server_url,
        "idp_metadata": ["text", idp.fetch_metadata()],
        "connection_timeout": [12, 12],
        "signature_certificate": "builtin",
        # The IdP exports the username as the SAML attribute ``uid``.
        "user_id_attribute_name": "uid",
        "user_alias_attribute_name": "",
        "email_attribute_name": "",
        "contactgroups_mapping": "no_mapping",
        "role_membership_mapping": False,
    }


@contextmanager
def _staged_helper(site: Site) -> Iterator[str]:
    """Drop the SAML helper into the site and remove it on exit."""
    site.write_file(_HELPER_REL_PATH, _SAML_HELPER_SCRIPT)
    try:
        yield site.path(_HELPER_REL_PATH).as_posix()
    finally:
        site.delete_file(_HELPER_REL_PATH)


_SITES_AUTH_HELPER_SCRIPT = _read_site_helper("sites_auth_helper.py")


@contextmanager
def _staged_sites_auth_helper(site: Site) -> Iterator[str]:
    """Drop the sites.mk helper into the site and remove it on exit."""
    site.write_file(_SITES_AUTH_HELPER_REL_PATH, _SITES_AUTH_HELPER_SCRIPT)
    try:
        yield site.path(_SITES_AUTH_HELPER_REL_PATH).as_posix()
    finally:
        site.delete_file(_SITES_AUTH_HELPER_REL_PATH)


@contextmanager
def override_per_site_authentication_connections(
    central_site: Site,
    overrides: dict[str, list[tuple[str, object]]],
) -> Iterator[None]:
    """Temporarily write per-site ``authentication_connections`` (``{site_id: [(kind,
    payload), …]}``) into the central's ``sites.mk``, overriding what each remote
    inherits; popped on exit. The caller activates before/after to propagate."""
    with _staged_sites_auth_helper(central_site) as helper:
        for site_id, entries in overrides.items():
            payload = {
                "authentication_connections": entries,
                "user_attribute_sync_connections": [],
            }
            central_site.check_output(
                ["python3", helper, "set", site_id],
                input_=json.dumps(payload),
            )
            # Mark the remote dirty so the activation pushes a snapshot (a bare
            # sites.mk write records no change); skip the central's own entry.
            if site_id != central_site.id:
                central_site.check_output(["python3", helper, "mark-dirty", site_id])
    try:
        yield
    finally:
        try:
            with _staged_sites_auth_helper(central_site) as helper:
                for site_id in overrides:
                    central_site.check_output(["python3", helper, "clear", site_id])
                    if site_id != central_site.id:
                        central_site.check_output(["python3", helper, "mark-dirty", site_id])
        except Exception:
            logger.exception(
                "Failed to clear per-site authentication_connections overrides on %s",
                central_site.id,
            )


_DELETE_USERS_HELPER_REL_PATH = "tmp/identity_delete_users_helper.py"
_DELETE_USERS_HELPER_SCRIPT = _read_site_helper("delete_users_helper.py")


@contextmanager
def _staged_delete_users_helper(site: Site) -> Iterator[str]:
    """Drop the users.mk delete helper into the site and remove it on exit."""
    site.write_file(_DELETE_USERS_HELPER_REL_PATH, _DELETE_USERS_HELPER_SCRIPT)
    try:
        yield site.path(_DELETE_USERS_HELPER_REL_PATH).as_posix()
    finally:
        site.delete_file(_DELETE_USERS_HELPER_REL_PATH)


def delete_users_on_disk(site: Site, user_ids: list[str]) -> None:
    """Remove ``user_ids`` from ``site``'s on-disk ``users.mk`` (best-effort cleanup
    for users an LDAP sync imported on a remote, where openapi is unavailable)."""
    if not user_ids:
        return
    with _staged_delete_users_helper(site) as helper:
        site.check_output(["python3", helper, *user_ids])


@contextmanager
def set_central_authentication_connections(
    central_site: Site,
    saml_connection_id: str,
) -> Iterator[None]:
    """Set ``authentication_connections`` + ``user_attribute_sync_connections`` on the
    central only: SAML is the sole login provider and LDAP sync is gated off so its
    job never claims the user out from under SAML. Remotes inherit both at activation,
    with the per-site ACS URL filled in by the central into each ``sitespecific.mk``."""
    entries: list[tuple[str, object]] = [("saml", {"connection_id": saml_connection_id})]
    payload = {
        "authentication_connections": entries,
        "user_attribute_sync_connections": [],
    }

    with _staged_sites_auth_helper(central_site) as helper:
        central_site.check_output(
            ["python3", helper, "set", central_site.id],
            input_=json.dumps(payload),
        )
    try:
        yield
    finally:
        try:
            with _staged_sites_auth_helper(central_site) as helper:
                central_site.check_output(["python3", helper, "clear", central_site.id])
        except Exception:
            logger.exception(
                "Failed to clear authentication / sync connections on %s", central_site.id
            )


@contextmanager
def configure_saml_connection_for_distributed(
    central_site: Site,
    additional_acs_sites: list[Site],
    idp: SamlIdpBackend,
    connection_id: str = SAML_CONNECTION_ID,
) -> Iterator[str]:
    """Create the central's SAML connection (propagated by config sync) and register
    every site's ACS URL with the IdP. All sites share the central's entity ID; only
    the ACS URL is rewritten per-site at runtime."""
    _, entity_id, central_acs = site_saml_endpoints(central_site, connection_id)
    additional_acs_urls = [site_saml_endpoints(s, connection_id)[2] for s in additional_acs_sites]
    idp.register_service_provider(entity_id, [central_acs, *additional_acs_urls])

    payload = _saml_connection_payload(central_site, idp, connection_id)
    with _staged_helper(central_site) as helper:
        central_site.check_output(
            ["python3", helper, "upsert"],
            input_=json.dumps(payload),
        )
    try:
        yield connection_id
    finally:
        try:
            with _staged_helper(central_site) as helper:
                central_site.check_output(["python3", helper, "delete", connection_id])
        except Exception:
            logger.exception("Failed to delete SAML connection on %s", central_site.id)


@contextmanager
def configure_distributed_identity_providers(
    central_site: Site,
    remote_sites: list[Site],
    ldap: LdapBackend,
    idp: SamlIdpBackend,
) -> Iterator[str]:
    """Wire LDAP + SAML once on the central and activate so config sync propagates
    ``authentication_connections`` + per-site ACS URL to the remotes (CMK-33812);
    no per-remote configuration is needed. Yields the SAML connection ID."""
    with (
        configure_ldap_connection(central_site, ldap),
        configure_saml_connection_for_distributed(
            central_site=central_site,
            additional_acs_sites=remote_sites,
            idp=idp,
        ) as saml_id,
        set_central_authentication_connections(
            central_site=central_site,
            saml_connection_id=saml_id,
        ),
    ):
        central_site.openapi.changes.activate_and_wait_for_completion(
            force_foreign_changes=True,
        )
        try:
            yield saml_id
        finally:
            # Flush central+remote pending changes left by SAML provisioning and
            # the inner cleanup so the testlib connection() teardown's push isn't
            # refused with "pending changes that would get lost" (no override flag).
            try:
                central_site.openapi.changes.activate_and_wait_for_completion(
                    force_foreign_changes=True,
                )
            except Exception:
                logger.exception(
                    "Pre-teardown activate on %s failed; the testlib connection() "
                    "cleanup may surface 'pending changes that would get lost'",
                    central_site.id,
                )
