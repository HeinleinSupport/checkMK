"""Rule to generate MD5 checksums for files in a tar archive."""

def _md5sums_from_archive_impl(ctx):
    ctx.actions.run_shell(
        inputs = [ctx.file.src],
        outputs = [ctx.outputs.out],
        command = "mkdir extracted && " +
                  "tar -C extracted -xf " + ctx.file.src.path + " && " +
                  "cd extracted && " +
                  "md5sum $(find * -type f) > ../" + ctx.outputs.out.path,
    )

md5sums_from_archive = rule(
    implementation = _md5sums_from_archive_impl,
    attrs = {
        "out": attr.output(mandatory = True),
        "src": attr.label(allow_single_file = True, mandatory = True),
    },
)
