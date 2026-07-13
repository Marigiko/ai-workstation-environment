"""Main entry point for ai-workstation-environment."""

import argparse
import subprocess
import sys
from pathlib import Path

from core.component import Component, discover_components, install_component
from core.config import load_config
from core.detect import detect_all
from core.dotfiles import apply_dotfiles
from core.graph import resolve
from core.logger import log, setup_logger
from core.mcp import MCPManager
from core.state import State


def find_project_root() -> Path:
    """Walk up from CWD or script location to find project root."""
    candidate = Path(__file__).resolve().parent.parent
    if (candidate / "pyproject.toml").exists():
        return candidate
    for p in Path.cwd().parents:
        if (p / "pyproject.toml").exists():
            return p
    return candidate


def cmd_detect(args: argparse.Namespace, root: Path) -> None:
    env = detect_all()
    print(f"OS:              {env.os} ({env.arch})")
    print(f"WSL:             {'yes (v' + str(env.wsl_version) + ')' if env.is_wsl else 'no'}")
    print(f"GPU:             {env.gpu}")
    docker_status = "not found"
    if env.has_docker:
        docker_status = "installed (running)" if env.docker_running else "installed (not running)"
    print(f"Docker:          {docker_status}")
    print(f"Git:             {env.git_version or 'not found'}")
    print(f"Tailscale:       {'installed' if env.has_tailscale else 'not found'}")
    print(f"OpenCode:        {'installed' if env.has_opencode else 'not found'}")
    print(f"Claude Code:     {'installed' if env.has_claude_code else 'not found'}")
    print(f"Zed:             {'installed' if env.has_zed else 'not found'}")
    print(f"Shell:           {env.shell}")
    print(f"Package manager: {env.package_manager}")
    print(f"User:            {env.user}")
    print(f"Hostname:        {env.hostname}")


def cmd_bootstrap(args: argparse.Namespace, root: Path) -> None:
    env = detect_all()
    load_config(root, profile=args.profile)
    state = State(root / ".state")

    log.info("Profile: %s", args.profile or "default")
    log.info("OS: %s | WSL: %s | GPU: %s | Pkg: %s",
             env.os, env.is_wsl, env.gpu, env.package_manager)

    components_dir = root / "components"
    all_components = discover_components(components_dir)

    if args.only:
        selected = {n: c for n, c in all_components.items() if n == args.only}
        if not selected:
            log.error("Component not found: %s", args.only)
            sys.exit(1)
    elif getattr(args, "custom", False):
        selected = _select_components_interactive(all_components, env)
        if not selected:
            log.error("No components selected.")
            sys.exit(1)
    else:
        profile_data = _load_profile(root, args.profile)
        wanted = set(profile_data.get("components", [])) if profile_data else set(all_components)
        selected = {n: c for n, c in all_components.items() if n in wanted}

    comp_list = [{"name": c.name, "depends_on": c.depends_on} for c in selected.values()]
    order = resolve(comp_list)

    installed = failed = skipped = 0
    for name in order:
        comp = selected[name]
        if comp.platforms and env.os not in comp.platforms:
            log.info("Skip %s (platform: %s)", name, env.os)
            skipped += 1
            continue
        if install_component(comp, state, env.os):
            installed += 1
        else:
            failed += 1

    log.info("--- Dotfiles ---")
    dotfiles_dir = root / "dotfiles"
    if dotfiles_dir.exists():
        created, dot_skipped, dot_errors = apply_dotfiles(
            dotfiles_dir, Path.home(), force=args.force,
        )
        log.info("Dotfiles: %d created, %d skipped, %d errors", created, dot_skipped, dot_errors)

    log.info("--- MCP Servers ---")
    mcp = MCPManager(root)
    enabled = mcp.get_enabled_servers()
    log.info("Enabled MCP servers: %s", ", ".join(enabled) if enabled else "none")
    for server_name in enabled:
        mcp.install_server(server_name)

    if args.generate_mcp:
        for tool in ["opencode", "claude-code", "zed", "mimo"]:
            mcp.generate_config(tool)

    print()
    log.info("=== Summary ===")
    log.info("Components: %d installed, %d skipped, %d failed", installed, skipped, failed)
    if failed:
        sys.exit(1)


def cmd_status(args: argparse.Namespace, root: Path) -> None:
    state = State(root / ".state")
    installed = state.list_installed()
    if not installed:
        print("No components installed.")
        return
    print(f"{'Component':<30} {'Version':<15} {'Installed At'}")
    print("-" * 70)
    for name, info in sorted(installed.items()):
        print(f"{name:<30} {info.get('version', '?'):<15} {info.get('installed_at', '?')}")


def cmd_list(args: argparse.Namespace, root: Path) -> None:
    components_dir = root / "components"
    all_components = discover_components(components_dir)
    if not all_components:
        print("No components found.")
        return
    print(f"{'Component':<30} {'Platforms':<20} {'Installed'}")
    print("-" * 65)
    for name, comp in sorted(all_components.items()):
        platforms = ", ".join(comp.platforms) if comp.platforms else "all"
        is_installed = "yes" if comp.check() else "no"
        print(f"{name:<30} {platforms:<20} {is_installed}")


def cmd_mcp_list(args: argparse.Namespace, root: Path) -> None:
    mcp = MCPManager(root)
    servers = mcp.list_servers()
    if not servers:
        print("No MCP servers found.")
        return
    print(f"{'Server':<25} {'Enabled':<10} {'Priority':<15} Description")
    print("-" * 80)
    for s in servers:
        enabled = "yes" if s["enabled"] else "no"
        print(f"{s['name']:<25} {enabled:<10} {s['priority']:<15} {s['description']}")


def cmd_mcp_enable(args: argparse.Namespace, root: Path) -> None:
    mcp = MCPManager(root)
    if mcp.enable(args.server):
        print(f"Enabled: {args.server}")
    else:
        sys.exit(1)


def cmd_mcp_disable(args: argparse.Namespace, root: Path) -> None:
    mcp = MCPManager(root)
    if mcp.disable(args.server):
        print(f"Disabled: {args.server}")
    else:
        sys.exit(1)


def cmd_mcp_install(args: argparse.Namespace, root: Path) -> None:
    mcp = MCPManager(root)
    if mcp.install_server(args.server):
        print(f"Installed: {args.server}")
    else:
        sys.exit(1)


def cmd_mcp_generate(args: argparse.Namespace, root: Path) -> None:
    mcp = MCPManager(root)
    if mcp.generate_config(args.tool):
        print(f"Generated config for: {args.tool}")
    else:
        sys.exit(1)


def cmd_update(args: argparse.Namespace, root: Path) -> None:
    """Update the workstation environment (git pull + re-bootstrap)."""
    log.info("Updating ai-workstation-environment...")

    # Check if we're in a git repo
    git_dir = root / ".git"
    if not git_dir.exists():
        log.error("Not a git repository: %s", root)
        sys.exit(1)

    # Get current branch
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=root, capture_output=True, text=True,
    )
    if result.returncode != 0:
        log.error("Failed to get current branch")
        sys.exit(1)
    branch = result.stdout.strip()
    log.info("Current branch: %s", branch)

    # Pull latest changes
    log.info("Pulling latest changes...")
    result = subprocess.run(
        ["git", "pull", "--rebase", "origin", branch],
        cwd=root, capture_output=True, text=True,
    )
    if result.returncode != 0:
        log.error("Git pull failed: %s", result.stderr)
        sys.exit(1)

    if "Already up to date" in result.stdout:
        log.info("Already up to date")
    else:
        log.info("Updated successfully")
        print(result.stdout)

    # Re-run bootstrap
    log.info("Re-running bootstrap...")
    args.command = "bootstrap"
    if not hasattr(args, "only"):
        args.only = None
    if not hasattr(args, "force"):
        args.force = False
    if not hasattr(args, "dry_run"):
        args.dry_run = False
    if not hasattr(args, "generate_mcp"):
        args.generate_mcp = False
    cmd_bootstrap(args, root)


def cmd_update_tools(args: argparse.Namespace, root: Path) -> None:
    """Check for and install updates to installed components."""
    log.info("Checking for component updates...")

    env = detect_all()
    state = State(root / ".state")
    components_dir = root / "components"
    all_components = discover_components(components_dir)
    installed = state.list_installed()

    if not installed:
        log.info("No components installed")
        return

    updated = 0
    for name in installed:
        if name not in all_components:
            log.warning("Component %s not found in registry", name)
            continue

        comp = all_components[name]
        if comp.platforms and env.os not in comp.platforms:
            continue

        # Check if update is available
        log.info("Checking %s...", name)
        if comp.check():
            # Component is installed, try to update
            update_script = comp.path / "update.sh"
            if update_script.exists():
                result = subprocess.run(
                    ["bash", str(update_script)],
                    capture_output=True, text=True, timeout=300,
                )
                if result.returncode == 0:
                    if "updated" in result.stdout.lower():
                        log.info("Updated %s", name)
                        updated += 1
                        # Update state with new version
                        state.record(name, version=comp.metadata.get("version", "unknown"))
                    else:
                        log.info("%s is up to date", name)
                else:
                    log.warning("Update check failed for %s: %s", name, result.stderr)
            else:
                log.info("%s: no update script (manual update required)", name)
        else:
            log.warning("%s: not properly installed, reinstalling...", name)
            install_component(comp, state, env.os)

    log.info("Update complete: %d components updated", updated)


def _select_components_interactive(
    all_components: dict[str, Component], env
) -> dict[str, Component]:
    """Interactive component selection. Returns filtered component dict."""
    print("\n=== AI Workstation — Custom Installation ===\n")
    print("Select components to install (toggle with number, 'a' for all, 'd' done):\n")

    names = sorted(all_components.keys())
    selected = set()

    while True:
        for i, name in enumerate(names, 1):
            comp = all_components[name]
            mark = "[x]" if name in selected else "[ ]"
            installed = " (installed)" if comp.check() else ""
            optional = " [optional]" if comp.optional else ""
            print(f"  {i:>2}. {mark} {name:<25} {comp.description[:40]}{installed}{optional}")
        print()
        raw = input("Toggle (number/a/d): ").strip().lower()

        if raw == "d":
            break
        elif raw == "a":
            selected = set(names)
        elif raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(names):
                name = names[idx]
                if name in selected:
                    selected.discard(name)
                else:
                    selected.add(name)
        else:
            print("Invalid input. Use number, 'a' (all), or 'd' (done).")

    return {n: c for n, c in all_components.items() if n in selected}
    if not profile:
        return {}
    profile_path = root / "profiles" / f"{profile}.yaml"
    if not profile_path.exists():
        log.warning("Profile not found: %s", profile)
        return {}
    import yaml
    with open(profile_path) as f:
        return yaml.safe_load(f) or {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="awe",
        description="AI Workstation Environment",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--profile", default=None, help="Profile to apply")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("detect", help="Detect system environment")

    boot = sub.add_parser("bootstrap", help="Run full bootstrap")
    boot.add_argument("--profile", default=None, help="Profile to apply")
    boot.add_argument("--only", help="Install only this component")
    boot.add_argument("--custom", action="store_true", help="Interactive component selection")
    boot.add_argument("--force", action="store_true", help="Force overwrite dotfiles")
    boot.add_argument("--dry-run", action="store_true", help="Show what would be done")
    boot.add_argument(
        "--generate-mcp", action="store_true",
        help="Generate MCP configs for AI tools",
    )

    sub.add_parser("status", help="Show installed components")
    sub.add_parser("list", help="List available components")

    mcp_list = sub.add_parser("mcp-list", help="List MCP servers")
    mcp_list.add_argument("--all", action="store_true", help="Show all servers")

    mcp_enable = sub.add_parser("mcp-enable", help="Enable an MCP server")
    mcp_enable.add_argument("server", help="MCP server name")

    mcp_disable = sub.add_parser("mcp-disable", help="Disable an MCP server")
    mcp_disable.add_argument("server", help="MCP server name")

    mcp_install = sub.add_parser("mcp-install", help="Install an MCP server")
    mcp_install.add_argument("server", help="MCP server name")

    mcp_gen = sub.add_parser("mcp-generate", help="Generate MCP config for AI tool")
    mcp_gen.add_argument("tool", choices=["opencode", "claude-code", "zed", "mimo"], help="AI tool")

    sub.add_parser("update", help="Update environment (git pull + re-bootstrap)")
    sub.add_parser("update-tools", help="Check for component updates")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        setup_logger(level="debug")

    root = find_project_root()

    commands = {
        "detect": cmd_detect,
        "bootstrap": cmd_bootstrap,
        "status": cmd_status,
        "list": cmd_list,
        "mcp-list": cmd_mcp_list,
        "mcp-enable": cmd_mcp_enable,
        "mcp-disable": cmd_mcp_disable,
        "mcp-install": cmd_mcp_install,
        "mcp-generate": cmd_mcp_generate,
        "update": cmd_update,
        "update-tools": cmd_update_tools,
    }

    handler = commands.get(args.command)
    if not handler:
        parser.print_help()
        sys.exit(1)

    handler(args, root)


if __name__ == "__main__":
    main()
