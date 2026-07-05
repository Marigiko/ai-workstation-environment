"""System detection: OS, WSL, GPU, Docker, Git, Tailscale, etc."""

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Environment:
    os: str = ""                          # linux, darwin, windows
    arch: str = ""                        # x86_64, aarch64
    is_wsl: bool = False
    wsl_version: int = 0
    gpu: str = "none"                     # nvidia, amd, none
    has_docker: bool = False
    docker_running: bool = False
    has_git: bool = False
    git_version: str = ""
    has_tailscale: bool = False
    has_opencode: bool = False
    has_claude_code: bool = False
    has_zed: bool = False
    shell: str = ""
    package_manager: str = ""             # apt, pacman, brew
    home: str = ""
    user: str = ""
    hostname: str = ""
    extras: dict = field(default_factory=dict)


def _run(cmd: list[str], check: bool = False) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return (r.returncode, r.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return (1, "")


def detect_os() -> str:
    s = platform.system().lower()
    if s == "linux":
        return "linux"
    if s == "darwin":
        return "darwin"
    return s


def detect_wsl() -> tuple[bool, int]:
    try:
        ver = Path("/proc/version").read_text().lower()
        if "microsoft" in ver:
            if "wsl2" in ver:
                return (True, 2)
            return (True, 1)
    except (FileNotFoundError, PermissionError):
        pass
    return (False, 0)


def detect_gpu() -> str:
    rc, out = _run(["lspci"])
    if rc == 0:
        low = out.lower()
        if "nvidia" in low:
            return "nvidia"
        if "amd" in low or "radeon" in low:
            return "amd"
    if Path("/dev/nvidia0").exists():
        return "nvidia"
    if shutil.which("nvidia-smi"):
        rc2, _ = _run(["nvidia-smi"])
        if rc2 == 0:
            return "nvidia"
    return "none"


def detect_docker() -> tuple[bool, bool]:
    if not shutil.which("docker"):
        return (False, False)
    rc, _ = _run(["docker", "info"])
    return (True, rc == 0)


def detect_git() -> tuple[bool, str]:
    if not shutil.which("git"):
        return (False, "")
    rc, out = _run(["git", "--version"])
    if rc == 0 and "git version" in out:
        return (True, out.split("git version ")[-1])
    return (True, "unknown")


def detect_package_manager() -> str:
    if shutil.which("pacman"):
        return "pacman"
    if shutil.which("apt-get"):
        return "apt"
    if shutil.which("brew"):
        return "brew"
    return "unknown"


def detect_shell() -> str:
    shell = os.environ.get("SHELL", "")
    if shell:
        return Path(shell).name
    if os.name == "nt":
        return "powershell"
    return "unknown"


def detect_all() -> Environment:
    has_docker, docker_running = detect_docker()
    has_git, git_version = detect_git()
    is_wsl, wsl_ver = detect_wsl()

    return Environment(
        os=detect_os(),
        arch=platform.machine(),
        is_wsl=is_wsl,
        wsl_version=wsl_ver,
        gpu=detect_gpu(),
        has_docker=has_docker,
        docker_running=docker_running,
        has_git=has_git,
        git_version=git_version,
        has_tailscale=shutil.which("tailscale") is not None,
        has_opencode=shutil.which("opencode") is not None,
        has_claude_code=shutil.which("claude") is not None,
        has_zed=shutil.which("zed") is not None,
        shell=detect_shell(),
        package_manager=detect_package_manager(),
        home=str(Path.home()),
        user=os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        hostname=platform.node(),
    )
