#!groovy

/// file: test-groovy-lint.groovy

void main() {
    def test_jenkins_helper = load("${checkout_dir}/buildscripts/scripts/utils/test_helper.groovy");

    dir("${checkout_dir}") {
        test_jenkins_helper.execute_test([
            name: "test-groovy-lint",
            cmd: "bazel lint //buildscripts/scripts:groovy_files",
        ]);
    }
}

return this;
