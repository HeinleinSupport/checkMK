#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
This check performs HTTP requests with some advanced features like
a) Detecting, populating and submitting HTML forms
b) Accepts and uses cookies
c) Follos HTTP redirects
d) Extends HTTP headers
"""

import argparse
import enum
import html.parser
import http.cookiejar
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "hosts",
        type=str,
        nargs="+",
        metavar="HOSTS",
        help="The IP addresses or hostnames of the hosts to contact",
    )
    parser.add_argument(
        "--port",
        type=int,
        metavar="PORT",
        help="TCP port, default: 80 without TLS, 443 with TLS",
    )
    parser.add_argument(
        "--uri",
        type=str,
        metavar="URI",
        default="/",
        help="URL string to query, '/' by default",
    )
    parser.add_argument(
        "--tls_configuration",
        type=TLSConfig,
        default="no_tls",
        help="Configure TLS usage",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        metavar="TIMEOUT",
        default=10,
        help="HTTP connect timeout in seconds, 10 s by default",
    )
    parser.add_argument(
        "--expected_regex",
        type=str,
        metavar="REGEX",
        help="Expected regular expression in the HTML response after form submission",
    )
    parser.add_argument(
        "--form_name",
        type=str,
        metavar="NAME",
        help="Name of the form to fill, must match with the contents of the 'name' attribute",
    )
    parser.add_argument(
        "--query_params",
        type=str,
        metavar="QUERYPARAMS",
        help="Keys/Values of form fields to be popuplated",
    )
    parser.add_argument(
        "--levels",
        type=int,
        nargs=2,
        metavar="THRESOLDS",
        help="Multiple Hosts: Lower warning and critical threshold for number of successful resulsts",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: let Python exceptions come through",
    )
    return parser.parse_args(argv)


class TLSConfig(enum.Enum):
    OFF = "no_tls"
    ON = "tls_standard"
    NO_CERT_VALID = "tls_no_cert_valid"

    @property
    def use_tls(self) -> bool:
        return self is not TLSConfig.OFF

    @property
    def validate_server_cert(self):
        return self is not TLSConfig.NO_CERT_VALID

    @property
    def port(self) -> int:
        return 80 if self is TLSConfig.OFF else 443


def debug(
    msg: str,
    debug_enabled: bool,
) -> None:
    if debug_enabled:
        sys.stderr.write("%s\n" % msg)


class HostResult(Exception):
    def __init__(self, result: tuple[int, str]) -> None:
        super().__init__()
        self.result = result


def new_state(rc: int, s: str) -> None:
    raise HostResult((rc, s))


def output_check_result(s: str) -> None:
    sys.stdout.write("%s\n" % s)


def get_base_url(
    *,
    tls: bool,
    host: str,
    port: int,
) -> str:
    if not tls and port == 443:
        tls = True

    proto = "https" if tls else "http"
    if (proto == "http" and port == 80) or (proto == "https" and port == 443):
        portspec = ""
    else:
        portspec = ":%d" % port

    return f"{proto}://{host}{portspec}"


# TODO: Refactor to requests
def init_http(validate_server_cert: bool) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(
        urllib.request.HTTPRedirectHandler(),
        urllib.request.HTTPHandler(debuglevel=0),
        urllib.request.HTTPSHandler(
            debuglevel=0,
            context=(
                None if validate_server_cert else ssl._create_unverified_context()  # nosec B323 # BNS:501305 # TODO & FIXME: Do *NOT* use private functions of ssl module!
            ),
        ),
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    )


def open_url(  # type: ignore[no-untyped-def]
    *,
    client: urllib.request.OpenerDirector,
    url: str,
    timeout: int | None,
    debug_enabled: bool,
    method: str = "GET",
    data=None,
):
    if method == "GET" and data is not None:
        # Add the query string to the url in this case
        start = "&" if "?" in url else "?"
        url += start + urllib.parse.urlencode(data)
        data = None

    try:
        if data:
            debug("POST %s" % url, debug_enabled)
            # Py3:
            # Encode a dict or sequence of two-element tuples into a URL query string.
            data = urllib.parse.urlencode(data, encoding="utf8")
            debug("  => %s" % data, debug_enabled)
            # Py3:
            # POST data should be bytes, an iterable of bytes, or a file object.
            # It cannot be of type str.
            fd = client.open(url, data.encode("utf8"), timeout)  # will be a POST
        else:
            debug("GET %s" % url, debug_enabled)
            fd = client.open(url, timeout=timeout)  # GET
    except urllib.error.HTTPError as e:
        new_state(2, "Unable to open %s : [%d] %s" % (url, e.code, e))

    except urllib.error.URLError as e:
        new_state(2, f"Unable to open {url} : {e.reason}")

    except TimeoutError as e:
        new_state(2, f"Unable to open {url} : {e}")

    real_url = fd.geturl()
    code = fd.getcode()
    content = fd.read()

    encoding = fd.headers.get_content_charset()
    if encoding:
        content = content.decode(encoding)

    debug("CODE: %s RESPONSE:" % code, debug_enabled)
    debug(
        "\n".join(
            ["    %02d %s" % (index + 1, line) for index, line in enumerate(content.split("\n"))]
        ),
        debug_enabled,
    )
    return real_url, content


class FormParser(html.parser.HTMLParser):
    def __init__(self, debug_enabled: bool = False) -> None:
        self.forms: dict = {}
        self.current_form = None
        self.debug_enabled = debug_enabled
        super().__init__()

    # CPython screwed up the removal of the error() method from ParserBase,
    # so we have to keep this until we use Python 3.10.
    def error(self, message):
        raise AssertionError(message)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "form":
            name = attrs.get("name", "unnamed-%d" % (len(self.forms) + 1))
            self.forms[name] = {
                "attrs": dict(attrs),
                "elements": {},
            }
            self.current_form = self.forms[name]
        elif tag == "input":
            if self.current_form is None:
                debug("Ignoring form field out of form tag", self.debug_enabled)
            elif "name" in attrs:
                self.current_form["elements"][attrs["name"]] = attrs.get("value", "")
            else:
                debug("Ignoring form field without name %r" % attrs, self.debug_enabled)

    def handle_endtag(self, tag):
        if tag == "form":
            self.current_form = None


# Parse XML to find all form elements
# One form found and no form_name given, use that one
# Loop all forms for the given form_name, use the matching one
# otherwise raise an exception
def parse_form(content: str, form_name: str):  # type: ignore[no-untyped-def]
    parser = FormParser()
    parser.feed(content)
    forms = parser.forms
    num_forms = len(forms)

    if num_forms == 0:
        new_state(2, "Found no form element in HTML code")

    elif num_forms == 1 and form_name is not None and form_name in forms:
        new_state(
            2,
            f'Found one form with name "{list(forms.keys())[0]}" but expected name "{form_name}"',
        )

    elif num_forms == 1:
        form = forms[list(forms.keys())[0]]

    elif form_name is None:
        new_state(
            2,
            "No form name provided but found multiple forms (Names: %s)" % ", ".join(forms.keys()),
        )

    else:
        form = forms.get(form_name)
        if form is None:
            new_state(
                2,
                'Found no form with name "{}" (Available: {})'.format(
                    form_name, ", ".join(forms.keys())
                ),
            )

    return form


def update_form_vars(form_elem, params: Mapping[str, str]):  # type: ignore[no-untyped-def]
    v = form_elem["elements"].copy()
    v.update(params)
    return v


def raise_host_state(
    *,
    client: urllib.request.OpenerDirector,
    base_url: str,
    args: argparse.Namespace,
    params: Mapping[str, str],
) -> None:
    # Perform first HTTP request to fetch the page containing the form(s)
    real_url, body = open_url(
        client=client,
        url=base_url + args.uri,
        timeout=args.timeout,
        debug_enabled=args.debug,
    )

    form = parse_form(body, args.form_name)

    # Get all fields and prefilled values from that form
    # Put the values of the given query params in these forms
    form_vars = update_form_vars(form, params)

    # Issue a HTTP request with those parameters
    # Extract the form target and method
    method = form["attrs"].get("method", "GET").upper()
    target = form["attrs"].get("action", real_url)
    if target[0] == "/":
        # target is given as absolute path, relative to hostname
        target = base_url + target
    elif target[0] != "":
        # relative URL
        target = "{}/{}".format("/".join(real_url.rstrip("/").split("/")[:-1]), target)

    real_url, content = open_url(
        client=client,
        url=target,
        method=method,
        data=form_vars,
        timeout=args.timeout,
        debug_enabled=args.debug,
    )

    # If a expect_regex is given, check wether or not it is present in the response
    if (expected_regex := args.expected_regex) is not None:
        matches = re.search(expected_regex, content)
        if matches is not None:
            new_state(0, 'Found expected regex "%s" in form response' % expected_regex)
        else:
            new_state(2, 'Expected regex "%s" could not be found in form response' % expected_regex)
    else:
        new_state(0, "Form has been submitted")


def check_host_states(  # type: ignore[no-untyped-def]
    states,
    levels: tuple[int, int] | None,
) -> tuple[int, str]:
    failed = []
    success = []
    for pair in sorted(states.items()):
        if pair[1][0] == 0:
            success.append(pair)
        else:
            failed.append(pair)
    num_success = len(success)
    num_failed = len(failed)

    if states:
        max_state = max(state for state, _output in states.values())
    else:
        max_state = 0

    if levels:
        warn, crit = levels
        if num_success <= crit:
            sum_state = 2
        elif num_success <= warn:
            sum_state = 1
        else:
            sum_state = 0
    else:
        sum_state = max_state

    txt = "%d succeeded, %d failed" % (num_success, num_failed)
    if failed:
        txt += " (%s)" % ", ".join([f"{n}: {msg[1]}" for n, msg in failed])
    return sum_state, txt


def _decode_query_params(encoded_params: str) -> Mapping[str, str]:
    return dict(parts.split("=", 1) for parts in encoded_params.split("&"))


def main(argv: Sequence[str] | None = None) -> tuple[int, str]:
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    multiple = len(args.hosts) > 1

    try:
        client = init_http(args.tls_configuration.validate_server_cert)

        states: dict[str, tuple[int, str]] = {}
        for host in args.hosts:
            base_url = get_base_url(
                tls=args.tls_configuration.use_tls,
                host=host,
                port=args.port if args.port is not None else args.tls_configuration.port,
            )
            try:
                raise_host_state(
                    client=client,
                    base_url=base_url,
                    args=args,
                    params=_decode_query_params(args.query_params) if args.query_params else {},
                )
            except HostResult as e:
                states[host] = e.result

        if multiple:
            return check_host_states(
                states,
                (args.levels[0], args.levels[1]) if args.levels else None,
            )
        return next(iter(states.values()))

    except Exception as e:
        if args.debug:
            raise
        return 3, "Exception occured: %s\n" % e


if __name__ == "__main__":
    exitcode, info = main()
    output_check_result(info)
    sys.exit(exitcode)
