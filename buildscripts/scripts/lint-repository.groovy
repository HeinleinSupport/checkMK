#!groovy

/// file: lint-repository.groovy

void main() {
    def test_jenkins_helper = load("${checkout_dir}/buildscripts/scripts/utils/test_helper.groovy");

    dir("${checkout_dir}") {
        test_jenkins_helper.execute_test([
            name       : "lint-repository",
            cmd        : "scripts/lint.sh",
            output_file: "results.sarif",
        ]);
        test_jenkins_helper.analyse_issues("SARIF", "results.sarif");
    }
}

return this;
