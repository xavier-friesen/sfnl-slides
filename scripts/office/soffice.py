"""Run LibreOffice (soffice) safely from a script.

Vendored from the official Anthropic pptx skill (snapshot in
`vendor/pptx-official-2026-07-29/`) and adapted, because it solves three things our own
`subprocess.run(["soffice", ...])` call got wrong:

1. **Profile directory.** soffice needs a writable user profile. Without one a sandboxed
   or service account aborts with "User installation could not be completed" and
   converts nothing — silently, from the caller's point of view. `run_soffice` puts a
   throwaway profile in a temp dir per call, which also means two renders can never
   fight over one profile lock. This replaces the hand-rolled
   `-env:UserInstallation` fix with the tested version.
2. **Blocked AF_UNIX sockets.** In some sandboxed VMs `socket(AF_UNIX)` is refused and
   soffice hangs forever instead of failing. On Linux the wrapper preloads a small shim
   that falls back to `socketpair()` and exits once the conversion is done.
3. **Hangs.** Every call gets a timeout, so a wedged soffice cannot stall a build.

Adaptations for this project:

* The binary is RESOLVED (`soffice`, `libreoffice`, plus the standard Windows install
  paths) instead of assuming `soffice` is on PATH — on Windows it usually is not.
* The shim is attempted on Linux only, and only when gcc is present. `socket.AF_UNIX`
  does not exist on every platform, so probing it unguarded raised AttributeError on
  Windows; and a missing compiler now means "run without the shim" rather than a crash.

Usage:
    from soffice import run_soffice, soffice_binary
    result = run_soffice(["--headless", "--convert-to", "pdf", "--outdir", tmp, deck])
"""

from __future__ import annotations

import contextlib
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

DEFAULT_TIMEOUT = 600

# Where the Windows installer puts it. shutil.which finds it only if the user added it
# to PATH, which the installer does not do.
WINDOWS_CANDIDATES = (
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
)


def soffice_binary() -> str | None:
    """Absolute path to soffice, or None when LibreOffice is not installed."""
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    if sys.platform == "win32":
        for candidate in WINDOWS_CANDIDATES:
            if Path(candidate).is_file():
                return candidate
    return None


def get_soffice_env() -> dict:
    """Environment for soffice. Callers building their own argv must ALSO pass
    `-env:UserInstallation=<uri>`; prefer `run_soffice`, which does it for you."""
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "svp"

    shim = _shim_path()
    if shim is not None:
        env["LD_PRELOAD"] = str(shim)

    return env


def run_soffice(
    args: Iterable[str], timeout: int = DEFAULT_TIMEOUT, **kwargs
) -> subprocess.CompletedProcess:
    """Run soffice with a throwaway profile and a timeout."""
    binary = soffice_binary()
    if binary is None:
        raise RuntimeError("LibreOffice (soffice) niet gevonden")

    args = [str(a) for a in args]
    with contextlib.ExitStack() as stack:
        if not any(a.startswith("-env:UserInstallation") for a in args):
            profile = stack.enter_context(
                tempfile.TemporaryDirectory(
                    prefix="lo_profile_", ignore_cleanup_errors=True
                )
            )
            args = [f"-env:UserInstallation={Path(profile).as_uri()}"] + args
        return subprocess.run(
            [binary] + args, env=get_soffice_env(), timeout=timeout, **kwargs
        )


_SHIM_SO = Path(tempfile.gettempdir()) / "lo_socket_shim.so"


def _needs_shim() -> bool:
    """True only on Linux with AF_UNIX actually blocked."""
    if not sys.platform.startswith("linux"):
        return False
    family = getattr(socket, "AF_UNIX", None)
    if family is None:
        return False
    try:
        probe = socket.socket(family, socket.SOCK_STREAM)
        probe.close()
        return False
    except OSError:
        return True


def _shim_path() -> Path | None:
    """Build the shim if it is both needed and buildable, else None."""
    if not _needs_shim():
        return None
    try:
        return _ensure_shim()
    except (subprocess.CalledProcessError, OSError):
        # No gcc, or it failed. Running unshimmed may hang, but refusing to run at all
        # is strictly worse: the caller still has the COM path and qa-only mode.
        return None


def _ensure_shim() -> Path:
    if _SHIM_SO.exists():
        return _SHIM_SO
    if shutil.which("gcc") is None:
        raise OSError("gcc niet beschikbaar om de socket-shim te bouwen")

    src = Path(tempfile.gettempdir()) / "lo_socket_shim.c"
    src.write_text(_SHIM_SOURCE)
    try:
        subprocess.run(
            ["gcc", "-shared", "-fPIC", "-o", str(_SHIM_SO), str(src), "-ldl"],
            check=True,
            capture_output=True,
            timeout=120,
        )
    finally:
        src.unlink(missing_ok=True)
    return _SHIM_SO


_SHIM_SOURCE = r"""
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>

static int (*real_socket)(int, int, int);
static int (*real_socketpair)(int, int, int, int[2]);
static int (*real_listen)(int, int);
static int (*real_accept)(int, struct sockaddr *, socklen_t *);
static int (*real_close)(int);
static int (*real_read)(int, void *, size_t);

/* Per-FD bookkeeping (FDs >= 1024 are passed through unshimmed). */
static int is_shimmed[1024];
static int peer_of[1024];
static int wake_r[1024];            /* accept() blocks reading this */
static int wake_w[1024];            /* close()  writes to this      */
static int listener_fd = -1;        /* FD that received listen()    */

__attribute__((constructor))
static void init(void) {
    real_socket     = dlsym(RTLD_NEXT, "socket");
    real_socketpair = dlsym(RTLD_NEXT, "socketpair");
    real_listen     = dlsym(RTLD_NEXT, "listen");
    real_accept     = dlsym(RTLD_NEXT, "accept");
    real_close      = dlsym(RTLD_NEXT, "close");
    real_read       = dlsym(RTLD_NEXT, "read");
    for (int i = 0; i < 1024; i++) {
        peer_of[i] = -1;
        wake_r[i]  = -1;
        wake_w[i]  = -1;
    }
}

/* ---- socket ---------------------------------------------------------- */
int socket(int domain, int type, int protocol) {
    if (domain == AF_UNIX) {
        int fd = real_socket(domain, type, protocol);
        if (fd >= 0) return fd;
        /* socket(AF_UNIX) blocked - fall back to socketpair(). */
        int sv[2];
        if (real_socketpair(domain, type, protocol, sv) == 0) {
            if (sv[0] >= 0 && sv[0] < 1024) {
                is_shimmed[sv[0]] = 1;
                peer_of[sv[0]]    = sv[1];
                int wp[2];
                if (pipe(wp) == 0) {
                    wake_r[sv[0]] = wp[0];
                    wake_w[sv[0]] = wp[1];
                }
            }
            return sv[0];
        }
        errno = EPERM;
        return -1;
    }
    return real_socket(domain, type, protocol);
}

/* ---- listen ---------------------------------------------------------- */
int listen(int sockfd, int backlog) {
    if (sockfd >= 0 && sockfd < 1024 && is_shimmed[sockfd]) {
        listener_fd = sockfd;
        return 0;
    }
    return real_listen(sockfd, backlog);
}

/* ---- accept ---------------------------------------------------------- */
int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen) {
    if (sockfd >= 0 && sockfd < 1024 && is_shimmed[sockfd]) {
        /* Block until close() writes to the wake pipe. */
        if (wake_r[sockfd] >= 0) {
            char buf;
            real_read(wake_r[sockfd], &buf, 1);
        }
        errno = ECONNABORTED;
        return -1;
    }
    return real_accept(sockfd, addr, addrlen);
}

/* ---- close ----------------------------------------------------------- */
int close(int fd) {
    if (fd >= 0 && fd < 1024 && is_shimmed[fd]) {
        int was_listener = (fd == listener_fd);
        is_shimmed[fd] = 0;

        if (wake_w[fd] >= 0) {              /* unblock accept() */
            char c = 0;
            write(wake_w[fd], &c, 1);
            real_close(wake_w[fd]);
            wake_w[fd] = -1;
        }
        if (wake_r[fd] >= 0) { real_close(wake_r[fd]); wake_r[fd]  = -1; }
        if (peer_of[fd] >= 0) { real_close(peer_of[fd]); peer_of[fd] = -1; }

        if (was_listener)
            _exit(0);                        /* conversion done - exit */
    }
    return real_close(fd);
}
"""


if __name__ == "__main__":
    result = run_soffice(sys.argv[1:])
    sys.exit(result.returncode)
