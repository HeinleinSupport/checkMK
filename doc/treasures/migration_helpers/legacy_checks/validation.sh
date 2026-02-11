#!/usr/bin/bash

# Validation script for migrating legacy checks to modern plugins
# This is convenient when using LLMs to assist with the migration, as
# the agent otherwise will keep
# a) forgetting to run some of the validation steps
# b) keep coming up with new commands that need approval

cd "$(git rev-parse --show-toplevel)" || exit $?

# shellcheck disable=SC2046  # we want word splitting here
bazel run //:format $(git diff --name-only) || exit $?

bazel lint --fix //cmk/... || exit $?

# run mypy on more than the changed files. Takes longer, but coming back later takes even more time.
bazel build --config=mypy //cmk/... || exit $?

# at least exclude gui. Only collecting what we need keeps failing :-/
bazel test //tests/unit:repo --test_arg=--ignore --test_arg=tests/unit/cmk/gui || exit $?

make -C tests test-plugins-consistency
