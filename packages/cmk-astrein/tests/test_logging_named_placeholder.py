#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import ast
from pathlib import Path

from cmk.astrein.checker_simple_patterns import LoggingNamedPlaceholderChecker
from cmk.astrein.framework import CheckerError


def _check_logging(
    code: str,
    file_path: Path = Path("/repo/packages/cmk-astrein/cmk/astrein/foo.py"),
    repo_root: Path = Path("/repo"),
) -> list[CheckerError]:
    checker = LoggingNamedPlaceholderChecker(file_path, repo_root, code)
    return checker.check(ast.parse(code))


def test_logging_rejects_positional_placeholder() -> None:
    errors = _check_logging('logger.info("%s unknown", foo)')
    assert len(errors) == 1
    assert "named `%(name)s` placeholders" in errors[0].message


def test_logging_rejects_multiple_positional_placeholders() -> None:
    errors = _check_logging('logger.warning("%s and %s", a, b)')
    assert len(errors) == 1


def test_logging_rejects_positional_with_flags_width_precision() -> None:
    errors = _check_logging('logger.error("value=%-5.2f", x)')
    assert len(errors) == 1


def test_logging_rejects_non_string_conversion() -> None:
    errors = _check_logging('logger.debug("%d items", n)')
    assert len(errors) == 1


def test_logging_rejects_positional_in_log_method() -> None:
    errors = _check_logging('logger.log(logging.INFO, "%s", x)')
    assert len(errors) == 1


def test_logging_rejects_mixed_named_and_positional() -> None:
    errors = _check_logging('logger.info("%(a)s %s", {"a": a}, b)')
    assert len(errors) == 1


def test_logging_allows_named_placeholder() -> None:
    assert _check_logging('logger.info("%(thing)s unknown", {"thing": foo})') == []


def test_logging_allows_multiple_named_placeholders() -> None:
    assert _check_logging('logger.warning("%(a)s and %(b)s", {"a": a, "b": b})') == []


def test_logging_allows_named_placeholder_with_flags_width_precision() -> None:
    assert _check_logging('logger.error("value=%(value)-5.2f", {"value": x})') == []


def test_logging_allows_named_placeholder_with_literal_percent() -> None:
    assert _check_logging('logger.info("%(pct)s%% done", {"pct": p})') == []


def test_logging_allows_message_without_format_args() -> None:
    assert _check_logging('logger.info("just a plain message")') == []


def test_logging_allows_percent_text_without_format_args() -> None:
    # No format args -> "%s" is literal text, not a placeholder.
    assert _check_logging('logger.info("ratio is 50% saturated")') == []


def test_logging_allows_log_method_without_format_args() -> None:
    assert _check_logging('logger.log(logging.INFO, "plain message")') == []


def test_logging_ignores_non_constant_message() -> None:
    # A variable message cannot be inspected statically.
    assert _check_logging("logger.info(msg, x)") == []


def test_logging_ignores_warn_method() -> None:
    # `logger.warn` is not a checked method: ruff's logging rules already reject it in
    # favour of `logger.warning`.
    assert _check_logging('warnings.warn("%s deprecated", DeprecationWarning)') == []


def test_logging_ignores_non_logging_method() -> None:
    assert _check_logging('obj.send("%s", x)') == []


def test_logging_respects_suppression_comment() -> None:
    code = 'logger.info("%s", foo)  # astrein: disable=logging-named-placeholder'
    assert _check_logging(code) == []


def test_logging_skips_excluded_top_level_dir() -> None:
    assert (
        _check_logging(
            'logger.info("%s", foo)',
            file_path=Path("/repo/cmk/base/config.py"),
        )
        == []
    )


def test_logging_skips_excluded_sibling_package() -> None:
    assert (
        _check_logging(
            'logger.info("%s", foo)',
            file_path=Path("/repo/packages/cmk-ec/cmk/ec/main.py"),
        )
        == []
    )


def test_logging_enforced_for_astrein_package() -> None:
    errors = _check_logging(
        'logger.info("%s", foo)',
        file_path=Path("/repo/packages/cmk-astrein/cmk/astrein/lsp.py"),
    )
    assert len(errors) == 1


def test_logging_enforced_for_force_included_path_below_excluded_prefix() -> None:
    # cmk/ is excluded, but this file is force-included via _INCLUDED_PATHS.
    errors = _check_logging(
        'logger.info("%s", foo)',
        file_path=Path("/repo/cmk/update_config/plugins/actions/validate_mk_files.py"),
    )
    assert len(errors) == 1
