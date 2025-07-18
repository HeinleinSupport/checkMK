ARG DISTRO_IMAGE_BASE

# hadolint ignore=DL3006
# Create base image
FROM ${DISTRO_IMAGE_BASE} as base

SHELL ["/bin/bash", "-c"]
ENV \
    PATH="/opt/bin:${PATH}"

ARG ARTIFACT_STORAGE

RUN zypper addrepo -G ${ARTIFACT_STORAGE}/repository/sles15sp4 sles15sp4 \
    && zypper -n --no-gpg-checks in --replacefiles \
    gawk \
    && zypper -n --no-gpg-checks in --replacefiles \
    curl \
    cyrus-sasl-devel \
    enchant-devel \
    git \
    krb5-devel \
    make \
    python \
    python3-devel \
    sudo \
    && zypper clean -a

RUN zypper ref -s \
    && zypper -n in -y --force-resolution \
    apache2-devel \
    bind-utils \
    bison \
    flex \
    freeradius-client-devel \
    freetype2-devel \
    gcc \
    gcc-c++ \
    gd-devel \
    groff \
    gtk-doc \
    intltool \
    iputils \
    jq \
    libXpm-devel \
    libbz2-devel \
    libcurl-devel \
    libevent-devel \
    libexpat-devel \
    libgnutls-devel \
    libjpeg62-devel \
    libltdl7 \
    libmariadb-devel \
    libopenssl-devel \
    libpcap-devel \
    libpng16-devel \
    libtiff-devel \
    libtool \
    libuuid-devel \
    libvpx-devel \
    libxml2-devel \
    libxslt-devel \
    libxmlsec1-1 \
    netcat-openbsd \
    xmlsec1-devel \
    xmlsec1-openssl-devel \
    mariadb-client \
    openldap2-devel \
    openssh \
    pango-devel \
    patch \
    postgresql13-server-devel \
    readline-devel \
    rpcbind \
    rpm-build \
    rpm-devel \
    rsync \
    samba-client \
    sqlite3-devel \
    tar \
    texinfo \
    tk-devel \
    unzip \
    wget \
    vim \
    && zypper clean -a

# krb5-devel installs krb5-config to /usr/lib/mit, but we want it to be found with standard
# values for PATH, so we create a symlink here..
# This is needed and expected by setup.py of pykerberos for properly linking against the needed libs.
RUN ln -sf /usr/lib/mit/bin/krb5-config /usr/bin/

# Install our standard tool chain for building in seperate container
# - gnu-toolchain is needed for compiling all the C++ stuff
# - cmake is needed for e.g. building re2
# - openssl is needed by Python 3.7+
# - python is needed by our build / test chain
FROM base as builder
ARG NEXUS_ARCHIVES_URL
ARG NEXUS_USERNAME
ARG NEXUS_PASSWORD
ARG DISTRO
ARG BRANCH_VERSION
ENV \
    NEXUS_ARCHIVES_URL="${NEXUS_ARCHIVES_URL}" \
    NEXUS_USERNAME="${NEXUS_USERNAME}" \
    NEXUS_PASSWORD="${NEXUS_PASSWORD}" \
    DISTRO="${DISTRO}" \
    BRANCH_VERSION="${BRANCH_VERSION}"

# Copy over stuff that's needed by lots of scripts (has to be copied to context before)
COPY \
    .bazelversion \
    package_versions.bzl \
    defines.make \
    /opt/

COPY \
    build_lib.sh \
    Check_MK-pubkey.gpg \
    /opt/

COPY install-gnu-toolchain.sh /opt/
RUN /opt/install-gnu-toolchain.sh

COPY install-valgrind.sh /opt/
RUN /opt/install-valgrind.sh

COPY install-cmake.sh /opt/
RUN /opt/install-cmake.sh

COPY install-protobuf-cpp.sh /opt/
RUN /opt/install-protobuf-cpp.sh

COPY install-openssl.sh /opt/
RUN /opt/install-openssl.sh

COPY install-python.sh /opt/
RUN /opt/install-python.sh

# install GDB after Python as it requires shared object files, see CMK-15854
COPY install-gdb.sh /opt/
RUN /opt/install-gdb.sh

COPY install-rust-cargo.sh /opt/
RUN /opt/install-rust-cargo.sh

# Now shrink all the binaries and libraries we produced to build a small image
# in the next step
COPY strip_binaries /opt/
RUN /opt/strip_binaries /opt

# Run this AFTER strip_binaries!!
COPY install-bazel.sh /opt/
RUN /opt/install-bazel.sh

### Actual Build Image ###
FROM base

# Copy our standard tool chain for building
COPY --from=builder /opt /opt

ARG DISTRO
ARG DISTRO_MK_FILE
ARG BRANCH_VERSION
ENV \
    DISTRO="${DISTRO}" \
    BRANCH_VERSION="${BRANCH_VERSION}"

# Set symlinks
RUN /opt/install-gnu-toolchain.sh link-only
RUN /opt/install-valgrind.sh link-only
RUN /opt/install-cmake.sh link-only
RUN /opt/install-protobuf-cpp.sh --link-only
RUN /opt/install-python.sh link-only
RUN /opt/install-bazel.sh link-only
RUN /opt/install-rust-cargo.sh link-only

# Install non cached dependencies
COPY "${DISTRO_MK_FILE}" /opt/
COPY install-cmk-dependencies.sh /opt/
RUN /opt/install-cmk-dependencies.sh

COPY install-patchelf.sh /opt/
RUN /opt/install-patchelf.sh

# The /etc/fstab does not exist in the base image we use. A missing fstab prevents OMD from
# using a tmpfs for /omd/sites/[site]/tmp, which we want to have during our tests. We can
# simply solve this by pre-creating the empty file here.
RUN touch /etc/fstab

ENV RUSTUP_HOME=/opt/rust/rustup

COPY ci.bazelrc /etc/
RUN <<EOF cat >> /etc/ci.bazelrc
common:ci --@//bazel/cmk/distro="sles-15sp4"
common:ci --action_env=DISTRO=${DISTRO}
common:ci --action_env=BRANCH_VERSION=${BRANCH_VERSION}
common:ci --action_env=RUSTUP_HOME=${RUSTUP_HOME}
# We encountered false cache hits with remote caching due to environment variables
# not being propagated to external dependeny builds
# In that case "--host_action_env=..." (in addition to "--action_env") might help
# Currently we don't use any external dependencies though.
common:ci --host_action_env=DISTRO=${DISTRO}
common:ci --host_action_env=BRANCH_VERSION=${BRANCH_VERSION}
common:ci --host_action_env=RUSTUP_HOME=${RUSTUP_HOME}
EOF

ARG VERS_TAG
RUN echo "${VERS_TAG}" > /version.txt

LABEL \
    com.checkmk.image_type="build-image"

COPY entrypoint.sh /opt/
ENTRYPOINT ["/opt/entrypoint.sh"]
