
#include "stdafx.h"

#include "wnx/agent_controller.h"

#include <VersionHelpers.h>
#include <tools/_misc.h>

#include <filesystem>
#include <fstream>
#include <iosfwd>
#include <ranges>

#include "common/cfg_info.h"
#include "common/cfg_yaml.h"
#include "common/cma_yml.h"
#include "common/mailslot_transport.h"
#include "common/wtools.h"
#include "wnx/cfg.h"
#include "wnx/read_file.h"

namespace fs = std::filesystem;
namespace rs = std::ranges;
using namespace std::chrono_literals;
using namespace std::string_literals;

namespace cma::ac {

namespace {
const std::vector g_start_controller_moduses{Modus::service,
                                             Modus::integration};

bool AllowUseController(Modus modus) {
    return rs::find(g_start_controller_moduses, modus) !=
           g_start_controller_moduses.end();
}
const std::vector g_use_special_port_moduses{Modus::app, Modus::integration};

bool UseSpecialPort(Modus modus) {
    return rs::find(g_use_special_port_moduses, modus) !=
           g_use_special_port_moduses.end();
}
}  // namespace

fs::path LegacyPullFile() {
    return fs::path{cfg::GetUserDir()} / kLegacyPullFile;
}

fs::path ControllerFlagFile() {
    return fs::path{cfg::GetUserDir()} / kControllerFlagFile;
}

fs::path TomlConfigFile() {
    return fs::path{cfg::GetUserDir()} / cfg::files::kAgentToml;
}

namespace {
std::pair<fs::path, fs::path> ServiceName2TargetName() {
    return {fs::path{cfg::GetRootDir()} / cfg::files::kAgentCtl,
            GetWorkController()};
}

fs::path CopyControllerToBin() {
    const auto [src, tgt] = ServiceName2TargetName();
    std::error_code ec;
    fs::copy(src, tgt, fs::copy_options::overwrite_existing, ec);
    if (ec.value() == 0) {
        return tgt;
    }
    XLOG::l("error copying controller from '{}' to '{}' [{}]", src, tgt,
            ec.value());

    fs::path tgt_sav{tgt};
    try {
        tgt_sav.replace_extension(".sav");
    } catch (const std::exception &e) {
        XLOG::l("error renaming controller '{}'", e.what());
    }

    fs::rename(tgt, tgt_sav, ec);
    fs::copy(src, tgt, fs::copy_options::overwrite_existing, ec);
    if (ec.value() == 0) {
        return tgt;
    }
    XLOG::l("error copying controller from '{}' to '{}' [{}]", src, tgt,
            ec.value());
    return {};
}

template <type::AnyStringView T>
int ToInt(const T value) noexcept {
    try {
        return std::stoi(value);
    } catch (const std::exception & /*exc*/) {
        return -1;
    }
}

YAML::Node GetControllerNode() {
    return yml::GetNode(cfg::GetLoadedConfig(),
                        std::string{cfg::groups::kSystem},
                        std::string{cfg::vars::kController});
}

uint16_t GetPortFromString(const std::string &str) {
    const auto table = tools::SplitString(str, ":");
    if (table.size() != 2) {
        return 0;
    }

    const auto port = ToInt(table[1]);
    return port > 1'000 && port < 60'000 ? static_cast<uint16_t>(port) : 0U;
}

enum class AddrType {
    mailslot,
    ip,
};

std::string FormatAddressFor(AddrType ff, std::string_view addr) {
    return fmt::format(
        "{}{}{}",
        [](AddrType ff) {
            switch (ff) {
                case AddrType::mailslot:
                    return kCmdMailSlotPrefix;
                case AddrType::ip:
                    return kCmdIpPrefix;
            }
            // unreachable
            return kCmdIpPrefix;
        }(ff),
        kCmdPrefixSeparator, addr);
}

std::string GetConfiguredAgentChannel(Modus modus) {
    const auto controller_config = GetControllerNode();
    auto result =
        cfg::GetVal(controller_config, cfg::vars::kControllerAgentChannel,
                    std::string{cfg::defaults::kControllerAgentChannelDefault});

    if (tools::IsEqual(result,
                       cfg::defaults::kControllerAgentChannelMailSlot)) {
        return FormatAddressFor(
            AddrType::mailslot,
            mailslot::BuildMailSlotNameStem(modus, ::GetCurrentProcessId()));
    }

    if (UseSpecialPort(modus)) {
        result = fmt::format("localhost:{}", kWindowsInternalExePort);
    } else if (GetPortFromString(result) == 0) {
        XLOG::l("Invalid configured agent channel '{}' use default", result);
        return FormatAddressFor(
            AddrType::mailslot,
            mailslot::BuildMailSlotNameStem(modus, ::GetCurrentProcessId()));
    }
    return FormatAddressFor(AddrType::ip, result);
}

bool GetConfiguredForceLegacy() {
    const auto controller_config = GetControllerNode();
    return cfg::GetVal(controller_config, cfg::vars::kControllerForceLegacy,
                       cfg::defaults::kControllerForceLegacy);
}

}  // namespace

uint16_t GetConfiguredAgentChannelPort(Modus modus) {
    return GetPortFromString(GetConfiguredAgentChannel(modus));
}

bool GetConfiguredLocalOnly() {
    const auto controller_config = GetControllerNode();
    return cfg::GetVal(controller_config, cfg::vars::kControllerLocalOnly,
                       cfg::defaults::kControllerLocalOnly);
}

bool GetConfiguredAllowElevated() {
    const auto controller_config = GetControllerNode();
    return cfg::GetVal(controller_config, cfg::vars::kControllerAllowElevated,
                       cfg::defaults::kControllerAllowElevated);
}

bool IsConfiguredEmergencyOnCrash() {
    const auto controller_config = GetControllerNode();
    return cfg::GetVal(controller_config, cfg::vars::kControllerOnCrash,
                       std::string{cfg::defaults::kControllerOnCrashDefault}) ==
           cfg::values::kControllerOnCrashEmergency;
}

bool GetConfiguredCheck() {
    const auto controller_config = GetControllerNode();
    return cfg::GetVal(controller_config, cfg::vars::kControllerCheck,
                       cfg::defaults::kControllerCheck);
}

/// returns true if controller files DOES NOT exist
bool DeleteControllerInBin() {
    const auto [_, tgt] = ServiceName2TargetName();
    std::error_code ec;
    if (!fs::exists(tgt, ec)) {
        return true;
    }

    fs::remove(tgt, ec);
    return !fs::exists(tgt, ec);
}

bool IsRunController(const YAML::Node &node) {
    const auto controller =
        cma::yml::GetNode(node, std::string{cfg::groups::kSystem},
                          std::string{cfg::vars::kController});
    return cfg::GetVal(controller, cfg::vars::kControllerRun, false);
}

bool IsInLegacyMode() {
    std::error_code ec;
    return fs::exists(LegacyPullFile(), ec);
}

fs::path GetController(const fs::path &service) {
    fs::path controller{service};
    controller.replace_filename(cfg::files::kAgentCtl);
    return controller;
}

fs::path GetWorkController() {
    return fs::path{cfg::GetUserBinDir()} / cfg::files::kAgentCtl;
}

bool CreateTomlConfig(const fs::path &toml_file) {
    constexpr std::string_view text{
        "# Controlled by Check_MK Agent Bakery.\n"
        "# This file is managed via WATO, do not edit manually or you\n"
        "# lose your changes next time when you update the agent.\n\n"};
    auto port =
        cfg::GetVal(cfg::groups::kGlobal, cfg::vars::kPort, cfg::kMainPort);
    const auto pull_port = fmt::format("pull_port = {}\n", port);
    const auto only_from =
        cfg::GetInternalArray(cfg::groups::kGlobal, cfg::vars::kOnlyFrom);
    std::string allowed_ip;
    if (!only_from.empty()) {
        allowed_ip = "allowed_ip = ["s;
        for (const auto &a : only_from) {
            allowed_ip += "\"" + a + "\"" + ",\n ";
        }
        allowed_ip.pop_back();
        allowed_ip.pop_back();
        allowed_ip.pop_back();
        allowed_ip += "]\n";
    }
    auto controller_config = GetControllerNode();
    auto detect_proxy =
        fmt::format("{} = {}\n", cfg::vars::kControllerDetectProxy,
                    cfg::GetVal(controller_config,
                                cfg::vars::kControllerDetectProxy, false));
    auto valid_api_cert =
        fmt::format("{} = {}\n", cfg::vars::kControllerValidApiCert,
                    cfg::GetVal(controller_config,
                                cfg::vars::kControllerValidApiCert, false));
    try {
        std::ofstream ofs(toml_file);
        ofs << text << pull_port << allowed_ip << detect_proxy
            << valid_api_cert;
    } catch (const std::exception &e) {
        XLOG::l("Failed to create TOML config with exception {}", e.what());
        return false;
    }
    return true;
}

std::wstring BuildCommandLine(const fs::path &controller) {
    auto only_from =
        cfg::GetInternalArray(cfg::groups::kGlobal, cfg::vars::kOnlyFrom);
    auto agent_channel = GetConfiguredAgentChannel(GetModus());

    return controller.wstring() +
           wtools::ConvertToUtf16(fmt::format(" -vv {} {} {}",   //
                                              kCmdLineAsDaemon,  // daemon
                                              kCmdLineChannel, agent_channel));
}
std::optional<uint32_t> StartAgentController() {
    XLOG::l.i("starting controller");
    if (!AllowUseController(GetModus())) {
        return {};
    }

    if (!::IsWindows7OrGreater()) {
        XLOG::l(
            "The agent controller is not compatible with this Windows version. "
            "You can disable using the agent controller by configuring the "
            "Checkmk rule set \"Windows agent controller\" for this host.");
        return false;
    }
    auto killed_count = wtools::KillProcessesByDir(cfg::GetUserBinDir());
    XLOG::d.i("killed {} processes in '{}'", killed_count,
              wtools::ToUtf8(cfg::GetUserBinDir()));
    auto controller_name = CopyControllerToBin();
    if (controller_name.empty()) {
        XLOG::l("can't copy controller");
        return {};
    }

    CreateTomlConfig(TomlConfigFile());

    wtools::AppRunner ar;
    if (GetModus() == Modus::integration) {
        if (const auto env_value = tools::win::GetEnv(L"DEBUG_HOME_DIR"s);
            env_value.empty()) {
            XLOG::d.i("Set DEBUG_HOME_DIR to '{}'",
                      wtools::ToUtf8(cfg::GetUserDir()));
            tools::win::SetEnv(L"DEBUG_HOME_DIR"s, cfg::GetUserDir());
        } else {
            XLOG::d.i("Use DEBUG_HOME_DIR as '{}'", wtools::ToUtf8(env_value));
        }
    }
    const auto cmdline = BuildCommandLine(controller_name);

    if (auto proc_id = ar.goExecAsController(cmdline); proc_id != 0) {
        XLOG::l.i("Agent controller '{}' started pid [{}]",
                  wtools::ToUtf8(cmdline), proc_id);
        return proc_id;
    }
    XLOG::l("Agent controller '{}' failed to start", controller_name);
    return {};
}

// TODO(sk): make public API and replace all Trailing/trim with this one
void TrimRight(std::string &s, std::string_view chars) {
    if (const auto end = s.find_last_not_of(chars); end != std::string::npos) {
        s.erase(end + 1);
    }
}

namespace {
std::string RunAgentControllerWithParam(std::string_view param) {
    auto work_controller = GetWorkController();
    if (std::error_code ec; !fs::exists(work_controller, ec)) {
        XLOG::l("There is no controller '{}' ec=[{}]", work_controller,
                ec.value());
        return {};
    }
    auto result = wtools::RunCommand(work_controller.wstring() + L" " +
                                     wtools::ConvertToUtf16(param));
    TrimRight(result, "\n\r");
    return result;
}
}  // namespace

std::string DetermineAgentCtlVersion() {
    return RunAgentControllerWithParam(kCmdLineVersion);
}

std::string DetermineAgentCtlStatus() {
    return RunAgentControllerWithParam(kCmdLineStatus);
}

bool KillAgentController() {
    if (!AllowUseController(GetModus())) {
        return false;
    }

    if (auto killed = wtools::KillProcessesByDir(cfg::GetUserBinDir())) {
        XLOG::t.i("killed [{}] controllers", killed);
    }

    // Idiotic loop below mirrors idiotic Windows architecture.
    // MS: Even if process killed, the executable may be for some time busy.
    // And can't be deleted.
    bool success = false;
    for (int i = 0; i < 20; ++i) {
        if (DeleteControllerInBin()) {
            XLOG::l.i("Controller is deleted");
            success = true;
            break;
        }
        XLOG::d("error deleting controller");
        std::this_thread::sleep_for(200ms);
    }
    std::error_code ec;
    fs::remove(TomlConfigFile(), ec);
    return success;
}

namespace {
void CreateLegacyFile() {
    std::ofstream ofs(wtools::ToStr(LegacyPullFile()));
    ofs << "Created by Windows agent";
}
const std::string g_legacy_pull_text{"File '{}'  {}, legacy pull mode {}"};

bool ConditionallyCreateLegacyFile(const fs::path &marker,
                                   std::string_view message) {
    bool created{false};
    if (!IsControllerFlagFileExists()) {
        CreateLegacyFile();
        created = true;
    }
    XLOG::l.i(g_legacy_pull_text, marker, message, created ? "ON" : "OFF");

    return created;
}
}  // namespace

/// Creates file in agent-user dir to satisfy controller requirements
/// marker is used to determine status of the OS
/// marker will be deleted
bool CreateLegacyModeFile(const fs::path &marker) {
    constexpr auto uninstall_allowed_delay = 10s;
    std::error_code ec;
    if (!fs::exists(marker, ec)) {
        return ConditionallyCreateLegacyFile(
            marker, "is absent, assuming fresh install");
    }

    const auto timestamp = fs::last_write_time(marker, ec);
    if (ec) {
        return ConditionallyCreateLegacyFile(marker,
                                             "is strange, assuming bad file");
    }

    if (const auto age = std::chrono::duration_cast<std::chrono::seconds>(
            fs::_File_time_clock::now().time_since_epoch() -
            timestamp.time_since_epoch());
        age > uninstall_allowed_delay) {
        return ConditionallyCreateLegacyFile(
            marker, "is too old, assuming fresh install");
    }

    const auto data = tools::ReadFileInString(marker.wstring());
    if (!data.has_value()) {
        return ConditionallyCreateLegacyFile(marker,
                                             "is bad, assuming fresh install");
    }

    if (const auto reinstall_new =
            (*data).starts_with(kCmkAgentMarkerNewDeprecated) ||
            (*data).starts_with(kCmkAgentMarkerLatest);
        reinstall_new) {
        XLOG::l.i("File '{}' is from 2.1+ legacy pull mode  N/A", marker);
        return false;
    }
    return ConditionallyCreateLegacyFile(marker, "is from 2.0 or earlier");
}

void CreateControllerFlagFile() {
    std::ofstream ofs(wtools::ToStr(ControllerFlagFile()));
    ofs << "Created by Windows agent";
}

bool IsControllerFlagFileExists() {
    std::error_code ec;
    return fs::exists(ControllerFlagFile(), ec);
}

void CreateArtifacts(const fs::path &marker, bool controller_exists) noexcept {
    std::error_code ec;
    ON_OUT_OF_SCOPE(fs::remove(marker, ec));
    if (!controller_exists) {
        return;
    }
    if (GetConfiguredForceLegacy()) {
        XLOG::l.i(g_legacy_pull_text, marker,
                  " is ignored, configured to always create file", "ON");
        CreateLegacyFile();
    } else if (!IsControllerFlagFileExists()) {
        CreateLegacyModeFile(marker);
    }
    CreateControllerFlagFile();
}

}  // namespace cma::ac
