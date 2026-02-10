#!groovy

/// file: test-bazel-lint.groovy

void main() {
    def test_jenkins_helper = load("${checkout_dir}/buildscripts/scripts/utils/test_helper.groovy");
    def versioning = load("${checkout_dir}/buildscripts/scripts/utils/versioning.groovy");
    def safe_branch_name = versioning.safe_branch_name();
    def container_safe_branch_name = safe_branch_name.replace(".", "-");

    dir("${checkout_dir}") {
        test_jenkins_helper.execute_test([
            name: "test-bazel-lint",
            cmd: "bazel run //:buildifier.check | tee bazel-lint.txt 2>&1",
            output_file: "bazel-lint.txt",
            container_name: "ubuntu-2404-${container_safe_branch_name}-latest",
        ]);

        test_jenkins_helper.analyse_issues("BAZELLINT", "bazel-lint.txt");
    }
}

return this;
