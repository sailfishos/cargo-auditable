%define __rustflags -Clink-arg=-Wl,-z,relro,-z,now -C debuginfo=2 -C incremental=false
%define __cargo CARGO_FEATURE_VENDORED=1 RUSTFLAGS="%{__rustflags}" cargo

Name:           cargo-auditable
Version:        0.6.4
Release:        1
Summary:        A tool to embed auditing information in ELF sections of rust binaries
License:        (Apache-2.0 OR MIT) AND Unicode-DFS-2016 AND (0BSD OR MIT OR Apache-2.0) AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND (Apache-2.0 OR Apache-2.0 WITH LLVM-exception OR MIT) AND (Apache-2.0 OR MIT OR Zlib) AND (Apache-2.0 OR MIT OR Zlib) AND (MIT OR Unlicense) AND (Apache-2.0 OR Zlib OR MIT) AND MIT
Group:          Development/Languages/Rust
URL:            https://github.com/sailfishos-mirror/cargo-auditable
Source0:        %{name}-%{version}.tar.zst
Source1:        vendor.tar.zst
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

# RUST START
mkdir -p "%TARGET_DIR"
rm -f "%TARGET_DIR"/.env

%ifarch %arm32
%define SB2_TARGET armv7-unknown-linux-gnueabihf
%endif
%ifarch %arm64
%define SB2_TARGET aarch64-unknown-linux-gnu
%endif
%ifarch %ix86
%define SB2_TARGET i686-unknown-linux-gnu
%endif

# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
{
  echo "export SB2_RUST_TARGET_TRIPLE=%SB2_TARGET"
  echo "export RUST_HOST_TARGET=%SB2_TARGET"

  echo "export RUST_TARGET=%SB2_TARGET"
  echo "export TARGET=%SB2_TARGET"
  echo "export HOST=%SB2_TARGET"
  echo "export SB2_TARGET=%SB2_TARGET"
  echo "export CARGO_HOME=%TARGET_DIR/cargo"
}  >> "%TARGET_DIR"/.env

%ifarch %arm32 %arm64
# This should be define...
echo "export CROSS_COMPILE=%SB2_TARGET" >> "%TARGET_DIR"/.env

# This avoids a malloc hang in sb2 gated calls to execvp/dup2/chdir
# during fork/exec. It has no effect outside sb2 so doesn't hurt
# native builds.
echo "export SB2_RUST_EXECVP_SHIM=\"/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env\"" >> "%TARGET_DIR"/.env
echo "export SB2_RUST_USE_REAL_EXECVP=Yes" >> "%TARGET_DIR"/.env
echo "export SB2_RUST_USE_REAL_FN=Yes" >> "%TARGET_DIR"/.env
%endif
# RUST END

%autosetup -a1

%build
source "%TARGET_DIR"/.env
unset LIBSSH2_SYS_USE_PKG_CONFIG
%{__cargo} build --manifest-path %{_builddir}/%{name}/Cargo.toml --jobs 4 --offline --release

%install
install -D -d -m 0755 %{buildroot}%{_bindir}
install -m 0755 %{_builddir}/%{name}/target/%{SB2_TARGET}/release/cargo-auditable %{buildroot}%{_bindir}/cargo-auditable

%files
%{_bindir}/cargo-auditable
