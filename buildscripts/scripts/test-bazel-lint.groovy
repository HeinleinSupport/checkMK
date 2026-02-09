#!groovy

/// file: test-bazel-lint.groovy

void main() {
    def test_jenkins_helper = load("${checkout_dir}/buildscripts/scripts/utils/test_helper.groovy");

    dir("${checkout_dir}") {
        test_jenkins_helper.execute_test([
            name: "test-bazel-lint",
            cmd: "bazel run //:buildifier.check | tee bazel-lint.txt 2>&1",
            output_file: "bazel-lint.txt",
        ]);

        test_jenkins_helper.analyse_issues("BAZELLINT", "bazel-lint.txt");
    }
}

return this;
