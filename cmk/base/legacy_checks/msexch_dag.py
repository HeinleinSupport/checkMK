#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example Output:
# <<<msexch_dag:sep(58)>>>
# RunspaceId                       : d58353f4-f868-43b2-8404-25875841a47b
# Identity                         : Mailbox Database 1\S0141KL
# Name                             : Mailbox Database 1\S0141KL
# DatabaseName                     : Mailbox Database 1
# Status                           : Mounted
# MailboxServer                    : S0141KL
# ActiveDatabaseCopy               : s0141kl
# ActivationSuspended              : False
# ActionInitiator                  : Unknown
# ErrorMessage                     :
# ErrorEventId                     :
# ExtendedErrorInfo                :
# SuspendComment                   :
# SinglePageRestore                : 0
# ContentIndexState                : Healthy
# ContentIndexErrorMessage         :
# CopyQueueLength                  : 0
# ReplayQueueLength                : 0
# LatestAvailableLogTime           :
# LastCopyNotificationedLogTime    :
# LastCopiedLogTime                :
# LastInspectedLogTime             :
# LastReplayedLogTime              :
# LastLogGenerated                 : 0
# LastLogCopyNotified              : 0
# LastLogCopied                    : 0
# LastLogInspected                 : 0
# LastLogReplayed                  : 0
# LogsReplayedSinceInstanceStart   : 0
# LogsCopiedSinceInstanceStart     : 0
# LatestFullBackupTime             : 22.10.2014 21:55:12
# LatestIncrementalBackupTime      :
# LatestDifferentialBackupTime     :
# LatestCopyBackupTime             :
# SnapshotBackup                   : True
# SnapshotLatestFullBackup         : True
# SnapshotLatestIncrementalBackup  :
# SnapshotLatestDifferentialBackup :
# SnapshotLatestCopyBackup         :
# LogReplayQueueIncreasing         : False
# LogCopyQueueIncreasing           : False
# OutstandingDumpsterRequests      : {}
# OutgoingConnections              :
# IncomingLogCopyingNetwork        :
# SeedingNetwork                   :
# ActiveCopy                       : True
#
# RunspaceId                       : d58353f4-f868-43b2-8404-25875841a47b
# Identity                         : Mailbox Database 2\S0141KL
# Name                             : Mailbox Database 2\S0141KL
# DatabaseName                     : Mailbox Database 2
# Status                           : Healthy
# MailboxServer                    : S0141KL
# ActiveDatabaseCopy               : s0142kl
# ActivationSuspended              : False
# ActionInitiator                  : Unknown
# ErrorMessage                     :
# ErrorEventId                     :
# ExtendedErrorInfo                :
# SuspendComment                   :
# SinglePageRestore                : 0
# ContentIndexState                : Healthy
# ContentIndexErrorMessage         :
# CopyQueueLength                  : 0
# ReplayQueueLength                : 0
# LatestAvailableLogTime           : 15.12.2014 13:26:34
# LastCopyNotificationedLogTime    : 15.12.2014 13:26:34
# LastCopiedLogTime                : 15.12.2014 13:26:34
# LastInspectedLogTime             : 15.12.2014 13:26:34
# LastReplayedLogTime              : 15.12.2014 13:26:34
# LastLogGenerated                 : 2527253
# LastLogCopyNotified              : 2527253
# LastLogCopied                    : 2527253
# LastLogInspected                 : 2527253
# LastLogReplayed                  : 2527253
# LogsReplayedSinceInstanceStart   : 15949
# LogsCopiedSinceInstanceStart     : 15945
# LatestFullBackupTime             : 13.12.2014 19:06:54
# LatestIncrementalBackupTime      :
# LatestDifferentialBackupTime     :
# LatestCopyBackupTime             :
# SnapshotBackup                   : True
# SnapshotLatestFullBackup         : True
# SnapshotLatestIncrementalBackup  :
# SnapshotLatestDifferentialBackup :
# SnapshotLatestCopyBackup         :
# LogReplayQueueIncreasing         : False
# LogCopyQueueIncreasing           : False
# OutstandingDumpsterRequests      : {}
# OutgoingConnections              :
# IncomingLogCopyingNetwork        :
# SeedingNetwork                   :
# ActiveCopy                       : False

from cmk.agent_based.legacy.v0_unstable import check_levels, LegacyCheckDefinition
from cmk.agent_based.v2 import StringTable

check_info = {}


def parse_msexch_dag(string_table: StringTable) -> StringTable:
    return string_table


check_info["msexch_dag"] = LegacyCheckDefinition(
    name="msexch_dag",
    parse_function=parse_msexch_dag,
)

#   .--dbcopy--------------------------------------------------------------.
#   |                      _ _                                             |
#   |                   __| | |__   ___ ___  _ __  _   _                   |
#   |                  / _` | '_ \ / __/ _ \| '_ \| | | |                  |
#   |                 | (_| | |_) | (_| (_) | |_) | |_| |                  |
#   |                  \__,_|_.__/ \___\___/| .__/ \__, |                  |
#   |                                       |_|    |___/                   |
#   +----------------------------------------------------------------------+


def inventory_msexch_dag_dbcopy(info):
    getit = False
    key = "Status"
    for line in info:
        if len(line) == 2:
            if line[0].strip() == "DatabaseName":
                dbname = line[1].strip()
                getit = True
            elif getit and line[0].strip() == key:
                yield dbname, {"inv_key": key, "inv_val": line[1].strip()}
                getit = False


def check_msexch_dag_dbcopy(item, params, info):
    getit = False
    inv_key = params["inv_key"]
    inv_val = params["inv_val"]
    for line in info:
        if len(line) == 2:
            key, val = (i.strip() for i in line)
            if key == "DatabaseName" and val == item:
                getit = True
            elif getit and key == inv_key:
                if val == inv_val:
                    state = 0
                    infotxt = f"{inv_key} is {val}"
                else:
                    state = 1
                    infotxt = f"{inv_key} changed from {inv_val} to {val}"
                return state, infotxt
    return None


check_info["msexch_dag.dbcopy"] = LegacyCheckDefinition(
    name="msexch_dag_dbcopy",
    service_name="Exchange DAG DBCopy for %s",
    sections=["msexch_dag"],
    discovery_function=inventory_msexch_dag_dbcopy,
    check_function=check_msexch_dag_dbcopy,
    check_default_parameters={},
)

# .
#   .--contentindex--------------------------------------------------------.
#   |                      _             _   _           _                 |
#   |       ___ ___  _ __ | |_ ___ _ __ | |_(_)_ __   __| | _____  __      |
#   |      / __/ _ \| '_ \| __/ _ \ '_ \| __| | '_ \ / _` |/ _ \ \/ /      |
#   |     | (_| (_) | | | | ||  __/ | | | |_| | | | | (_| |  __/>  <       |
#   |      \___\___/|_| |_|\__\___|_| |_|\__|_|_| |_|\__,_|\___/_/\_\      |
#   |                                                                      |
#   +----------------------------------------------------------------------+


def inventory_msexch_dag_contentindex(info):
    for line in info:
        if line[0].strip() == "DatabaseName":
            yield line[1].strip(), None


def check_msexch_dag_contentindex(item, _no_params, info):
    getit = False
    for line in info:
        if len(line) == 2:
            key, val = (i.strip() for i in line)
            if key == "DatabaseName" and val == item:
                getit = True
            elif getit and key == "ContentIndexState":
                if val == "Healthy":
                    state = 0
                else:
                    state = 1
                return state, "Status: %s" % val
    return None


check_info["msexch_dag.contentindex"] = LegacyCheckDefinition(
    name="msexch_dag_contentindex",
    service_name="Exchange DAG ContentIndex of %s",
    sections=["msexch_dag"],
    discovery_function=inventory_msexch_dag_contentindex,
    check_function=check_msexch_dag_contentindex,
)

# .
#   .--copyqueue-----------------------------------------------------------.
#   |                                                                      |
#   |           ___ ___  _ __  _   _  __ _ _   _  ___ _   _  ___           |
#   |          / __/ _ \| '_ \| | | |/ _` | | | |/ _ \ | | |/ _ \          |
#   |         | (_| (_) | |_) | |_| | (_| | |_| |  __/ |_| |  __/          |
#   |          \___\___/| .__/ \__, |\__, |\__,_|\___|\__,_|\___|          |
#   |                   |_|    |___/    |_|                                |
#   +----------------------------------------------------------------------+


def inventory_msexch_dag_copyqueue(info):
    for line in info:
        if line[0].strip() == "DatabaseName":
            yield line[1].strip(), {}


def check_msexch_dag_copyqueue(item, params, info):
    getit = False
    for line in info:
        if len(line) == 2:
            key, val = (i.strip() for i in line)
            if key == "DatabaseName" and val == item:
                getit = True
            elif getit and key == "CopyQueueLength":
                yield check_levels(
                    int(val),
                    "length",
                    params["levels"],
                    human_readable_func=str,
                    boundaries=(0, None),
                    infoname="Queue length",
                )
                return


check_info["msexch_dag.copyqueue"] = LegacyCheckDefinition(
    name="msexch_dag_copyqueue",
    service_name="Exchange DAG CopyQueue of %s",
    sections=["msexch_dag"],
    discovery_function=inventory_msexch_dag_copyqueue,
    check_function=check_msexch_dag_copyqueue,
    check_ruleset_name="msexch_copyqueue",
    check_default_parameters={"levels": (100, 200)},
)
