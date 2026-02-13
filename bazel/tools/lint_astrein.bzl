"""Astrein linter aspect for aspect_rules_lint framework"""

load("@aspect_rules_lint//lint:defs.bzl", "filter_srcs", "noop_lint_action", "output_files", "should_visit")

_MNEMONIC = "AspectRulesLintAstrein"

OUTFILE_FORMAT = "{label}.{mnemonic}.{suffix}"

def astrein_action(ctx, executable, srcs, stdout, exit_code, format, astrein_runfiles):
    """Run astrein linter on source files.

    Args:
        ctx: Bazel context
        executable: The astrein CLI executable
        srcs: Source files to lint
        stdout: Output file for lint results
        exit_code: Optional file to capture exit code (None if fail_on_violation is true)
        format: Output format ("gcc" or "sarif")
        astrein_runfiles: Runfiles of the astrein binary (includes config files)
    """
    if exit_code:
        outputs = [stdout, exit_code]
        command = "{astrein} --checker all --format {format} --output {out} {srcs}; echo $? > {exit_code}".format(
            astrein = executable.path,
            format = format,
            out = stdout.path,
            exit_code = exit_code.path,
            srcs = " ".join([f.path for f in srcs]),
        )
    else:
        outputs = [stdout]
        command = "{astrein} --checker all --format {format} --output {out} {srcs}".format(
            astrein = executable.path,
            format = format,
            out = stdout.path,
            srcs = " ".join([f.path for f in srcs]),
        )

    # Include astrein's runfiles as inputs so Bazel invalidates the cache when they change
    # (e.g. layer checker config)
    all_inputs = depset(direct = srcs, transitive = [astrein_runfiles])

    ctx.actions.run_shell(
        command = command,
        inputs = all_inputs,
        outputs = outputs,
        tools = [executable],
        mnemonic = _MNEMONIC,
        progress_message = "Linting %{label} with astrein (" + format + ")",
    )

def _astrein_aspect_impl(target, ctx):
    if "no-astrein" in ctx.rule.attr.tags:
        return []

    if not should_visit(ctx.rule, ctx.attr._rule_kinds, ctx.attr._filegroup_tags):
        return []

    if not hasattr(ctx.rule.attr, "srcs"):
        return []

    files_to_lint = filter_srcs(ctx.rule)
    py_files = [f for f in files_to_lint if f.extension == "py"]

    outputs, info = output_files(_MNEMONIC, target, ctx)

    if not py_files:
        noop_lint_action(ctx, outputs)
        return [info]

    astrein_runfiles = ctx.attr._astrein_cli[DefaultInfo].default_runfiles.files

    astrein_action(
        ctx,
        ctx.executable._astrein_cli,
        py_files,
        outputs.human.out,
        outputs.human.exit_code,
        "gcc",
        astrein_runfiles,
    )

    astrein_action(
        ctx,
        ctx.executable._astrein_cli,
        py_files,
        outputs.machine.out,
        outputs.machine.exit_code,
        "sarif",
        astrein_runfiles,
    )

    return [info]

def lint_astrein_aspect(binary, rule_kinds = ["py_binary", "py_library", "py_test"], filegroup_tags = ["python", "lint-with-astrein"]):
    return aspect(
        implementation = _astrein_aspect_impl,
        attr_aspects = ["deps"],
        attrs = {
            "_astrein_cli": attr.label(
                default = binary,
                executable = True,
                cfg = "exec",
            ),
            "_filegroup_tags": attr.string_list(
                default = filegroup_tags,
            ),
            "_options": attr.label(
                default = "@aspect_rules_lint//lint:options",
            ),
            "_rule_kinds": attr.string_list(
                default = rule_kinds,
            ),
        },
    )
