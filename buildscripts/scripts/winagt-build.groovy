#!groovy

/// file: winagt-build.groovy

void main() {
    check_job_parameters(["VERSION", "SIGN_METHOD"]);

    def windows = load("${checkout_dir}/buildscripts/scripts/utils/windows.groovy");
    def versioning = load("${checkout_dir}/buildscripts/scripts/utils/versioning.groovy");

    def branch_name = versioning.safe_branch_name();
    def branch_version = versioning.get_branch_version(checkout_dir);
    def cmk_vers_rc_aware = versioning.get_cmk_version(branch_name, branch_version, params.VERSION);
    def cmk_version = versioning.strip_rc_number_from_version(cmk_vers_rc_aware);

    def use_azure = (params.SIGN_METHOD == "azure");
    def sign_target = use_azure ? "agent_with_sign_azure" : "agent_with_sign";

    dir("${checkout_dir}") {
        stage("make setversion") {
            bat("make -C agents\\wnx NEW_VERSION='${cmk_version}' setversion")
        }

        def common_creds = [
            usernamePassword(
                credentialsId: 'nexus',
                passwordVariable: 'NEXUS_PASSWORD',
                usernameVariable: 'NEXUS_USERNAME'),
            string(
                credentialsId: "CI_TEST_SQL_DB_ENDPOINT",
                variable:"CI_TEST_SQL_DB_ENDPOINT"),
            string(
                credentialsId: "CI_ORA2_DB_TEST_PASSWORD",
                variable:"CI_ORA2_DB_TEST_PASSWORD"),
            string(
                credentialsId: "CI_ORA_TEST_PASSWORD",
                variable:"CI_ORA_TEST_PASSWORD"),
        ];

        def sign_creds = use_azure ? [
            string(credentialsId: "azure_artifact_signing_endpoint",        variable: "AZURE_ARTIFACT_SIGNING_ENDPOINT"),
            string(credentialsId: "azure_artifact_signing_account",         variable: "AZURE_ARTIFACT_SIGNING_ACCOUNT"),
            string(credentialsId: "azure_artifact_signing_profile",         variable: "AZURE_ARTIFACT_SIGNING_PROFILE"),
            string(credentialsId: "azure_artifact_signing_tenant_id",       variable: "AZURE_ARTIFACT_SIGNING_TENANT_ID"),
            string(credentialsId: "azure_artifact_signing_client_id",       variable: "AZURE_ARTIFACT_SIGNING_CLIENT_ID"),
            string(credentialsId: "azure_artifact_signing_client_secret",   variable: "AZURE_ARTIFACT_SIGNING_CLIENT_SECRET"),
        ] : [
            usernamePassword(
                credentialsId: 'win_sign',
                passwordVariable: 'WIN_SIGN_PASSWORD',
                usernameVariable: ''),
        ];

        withCredentials(common_creds + sign_creds) {
            // The windows.build function will create stages.
            withEnv(["CMK_VERSION=${cmk_version}"]) {
                windows.build(
                    TARGET: sign_target,
                    CREDS: NEXUS_USERNAME + ':' + NEXUS_PASSWORD,
                    CACHE_URL: 'https://artifacts.lan.tribe29.com/repository/omd-build-cache/'
                );
            }
        }

        // YubiKey requires a USB detach after signing; Azure does not.
        if (!use_azure) {
            stage("detach") {
                dir("agents\\wnx") {
                    bat("run.cmd --detach");
                }
            }
        }
    }
}

return this;
