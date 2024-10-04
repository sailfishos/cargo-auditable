Name:           cargo-auditable
Version:        0.6.4
Release:        1
Summary:        A tool to embed auditing information in ELF sections of rust binaries
License:        (Apache-2.0 OR MIT) AND Unicode-DFS-2016 AND (0BSD OR MIT OR Apache-2.0) AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND (Apache-2.0 OR Apache-2.0 WITH LLVM-exception OR MIT) AND (Apache-2.0 OR MIT OR Zlib) AND (Apache-2.0 OR MIT OR Zlib) AND (MIT OR Unlicense) AND (Apache-2.0 OR Zlib OR MIT) AND MIT
Group:          Development/Languages/Rust
URL:            https://github.com/sailfishos-mirror/cargo-auditable
Source:        %{name}-%{version}.tar.xz

# We can't dep on cargo-packaging because we would create a dependency loop.
# BuildRequires:  cargo-packaging
BuildRequires:  cargo
BuildRequires:  zstd
Requires:       rust
Requires:       cargo

%description
Know the exact crate versions used to build your Rust executable.
Audit binaries for known bugs or security vulnerabilities in production,
at scale, with zero bookkeeping. This works by embedding data about
the dependency tree in JSON format into a dedicated linker section
of the compiled executable.

%define TARGET_DIR ./%{name}/target

%prep
%autosetup -a1 -n %{name}-%{version}/%{name}

%build
%ifarch %arm32
%global sb2_target armv7-unknown-linux-gnueabihf
%endif
%ifarch %arm64
%global sb2_target aarch64-unknown-linux-gnu
%endif
%ifarch %ix86
%global sb2_target i686-unknown-linux-gnu
%endif

# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
export SB2_RUST_TARGET_TRIPLE=%{sb2_target}
export RUST_HOST_TARGET=%{sb2_target}
export RUST_TARGET=%{sb2_target}
export TARGET=%{sb2_target}
export HOST=%{sb2_target}
export CROSS_COMPILE=%{sb2_target}

unset LIBSSH2_SYS_USE_PKG_CONFIG
export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now -C debuginfo=2 -C incremental=false"
cargo build --offline --locked --release --jobs 1 --target %{sb2_target} --verbose

%install
install -D -d -m 0755 %{buildroot}%{_bindir}
install -m 0755 target/%{sb2_target}/release/cargo-auditable %{buildroot}%{_bindir}/cargo-auditable

%files
%{_bindir}/cargo-auditable
