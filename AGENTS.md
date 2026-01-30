# AI Agent Instructions

This file provides guidance to AI agents when working with code in this repository.

## Architecture Overview

Checkmk follows a modular architecture with several key components:

### Core Components

- **cmk/base/**: Core monitoring engine, configuration handling, and host management
- **cmk/gui/**: Web interface and user interaction components
- **cmk/checkengine/**: Check execution framework and result processing
- **cmk/fetchers/**: Data fetching mechanisms (SNMP, agent, piggyback, etc.)
- **cmk/plugins/**: Monitoring plugins and check implementations
- **cmk/utils/**: Shared utilities and helper functions
- **cmk/piggyback/**: Piggyback data handling for host relationships
- **cmk/rrd/**: RRD database interactions for metrics storage
- **cmk/ec/**: Event Console for log monitoring and correlation
- ...

### Supporting Components

- **agents/**: Monitoring agents for various platforms (Linux, Windows, etc.)
- **active_checks/**: Active check implementations
- **notifications/**: Notification plugins and handling
- **packages/**: Modular subprojects with individual build systems (see Package Architecture below)
- **omd/**: OMD (Open Monitoring Distribution) packaging and integration
- **tests/**: Comprehensive test suite including unit, integration, and GUI tests

### Package Architecture

The `packages/` directory contains independent subprojects, each with its own `run` script and Bazel targets:

#### Core Python Packages

- **cmk-ccc/**: Core common components (daemon, debugging, site management)
- **cmk-crypto/**: Cryptographic utilities (certificates, passwords, TOTP)
- **cmk-trace/**: OpenTelemetry tracing integration
- **cmk-messaging/**: RabbitMQ messaging infrastructure
- **cmk-werks/**: Work changelog management and CLI tools
- **cmk-mkp-tool/**: MKP (Monitoring Knowledge Package) management
- **cmk-events/**: Event processing and notification handling
- **cmk-plugin-apis/**: API definitions for plugin development

#### Frontend Packages

- **cmk-frontend-vue/**: Modern Vue.js 3 frontend framework
- **cmk-frontend/**: Legacy frontend assets and webpack build
- **cmk-shared-typing/**: TypeScript type definitions shared between vue frontend and backend

#### Infrastructure Packages

- **cmk-agent-receiver/**: FastAPI service for receiving agent data
- **cmk-agent-ctl/**: Rust-based agent controller
- **cmk-livestatus-client/**: Python client for Livestatus queries
- **cmk-relay-protocols/**: Protocol definitions for relay communication

#### Native/Compiled Packages

- **livestatus/**: C++ Livestatus query interface
- **neb/**: Nagios Event Broker module (C++)
- **unixcat/**: Unix socket communication utility (C++)
- **check-cert/**: SSL/TLS certificate checker (Rust)
- **check-http/**: HTTP/HTTPS checker (Rust)
- **mk-oracle/**: Oracle database monitoring (Rust)
- **mk-sql/**: SQL Server monitoring (Rust)

## Important Development Notes

We use Bazel as the primary build system with Make for legacy compatibility.

- Use the bazel skill for all testing and linting tasks, except integration and end-to-end tests, which use make
- Always format, lint and test your code when you are done with a task

<example-legacy-make-tests>
make -C tests test-integration
make -C tests test-composition
make -C tests test-gui-e2e
</example-legacy-make-tests>

## Testing Strategy

### Test Categories

1. **Unit tests**: Fast, isolated component testing (`tests/unit/`)
2. **Integration tests**: Component interaction testing (`tests/integration/`)
3. **Composition tests**: Multi-service integration (`tests/composition/`)
4. **GUI E2E tests**: End-to-end web interface testing (`tests/gui_e2e/`)
5. **Plugin tests**: Monitoring plugin validation (`tests/plugins_*/`)
6. **Agent plugin tests**: Cross-platform agent functionality (`tests/agent-plugin-unit/`)

## Code Structure and Conventions

### Module Organization

- **cmk.base**: Core monitoring functionality, not GUI-dependent
- **cmk.gui**: Web interface and user-facing components
- **cmk.utils**: Shared utilities accessible across components
- **cmk.ec**: Event Console functionality
- Component isolation enforced - GUI cannot import base internals

### Python Standards

- Python 3.12 for main codebase
- Agent plugins: Python 3.4+ compatible, with Python 2.7 auto-conversion
- Type hints required (mypy enforcement)
- Ruff for formatting and linting
- pathlib for file operations
- Context managers for resource handling

## Key Configuration Files

- **pyproject.toml**: Python project configuration, ruff, mypy, pytest settings
- **MODULE.bazel**: Bazel module dependencies and configuration
- **defines.make**: Version and build variable definitions
- **package_versions.bzl**: Centralized version management
- **.bazelrc**: Bazel build configuration
- **constraints.txt**: Python dependency constraints

## Multi-Edition Support

The codebase supports multiple Checkmk editions:

- Checkmk Community: Open source base edition
- Checkmk Pro: Commercial with advanced features
- Checkmk Ultimate: Cloud-native monitoring
- Checkmk Ultimate with multi-tenancy: Multi-tenant MSP edition
- Checkmk Cloud: Hosted solution
