#!/bin/sh

set +e
bazel lint --machine --fixes=false //... -- >lint.txt 2>&1
exit_code=$?
set -e
bazel run //scripts:sarif_preparse -- --root="$(bazel info workspace)"/bazel-bin --output "$(bazel info workspace)/results.sarif" || true
exit $exit_code
