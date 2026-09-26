"""Project Manager for Telegram Bot — manages projects, branches, sessions, worktrees."""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


PROJECTS_DIR = Path(
    os.environ.get(
        "AWE_PROJECTS_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent),
    )
)
STATE_FILE = Path.home() / ".config" / "telegram-bot" / "state.json"


@dataclass
class ProjectState:
    """State for a single project."""
    name: str
    path: str
    current_branch: str = ""
    branches: List[str] = field(default_factory=list)
    sessions: List[Dict] = field(default_factory=list)
    worktrees: List[Dict] = field(default_factory=list)
    last_activity: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class BotState:
    """Global bot state."""
    current_project: str = ""
    projects: Dict[str, ProjectState] = field(default_factory=dict)
    user_id: str = ""


class ProjectManager:
    """Manages projects, branches, sessions, and worktrees."""

    def __init__(self):
        self.state = self._load_state()

    def _load_state(self) -> BotState:
        """Load state from file."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    data = json.load(f)
                    state = BotState()
                    state.current_project = data.get("current_project", "")
                    state.user_id = data.get("user_id", "")
                    for name, proj_data in data.get("projects", {}).items():
                        state.projects[name] = ProjectState(**proj_data)
                    return state
            except Exception:
                pass
        return BotState()

    def _save_state(self):
        """Save state to file."""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_project": self.state.current_project,
            "user_id": self.state.user_id,
            "projects": {
                name: asdict(proj)
                for name, proj in self.state.projects.items()
            },
        }
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def list_projects(self) -> List[Dict]:
        """List all projects in D:\Projects."""
        projects = []
        if not PROJECTS_DIR.exists():
            return projects

        for item in sorted(PROJECTS_DIR.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                is_git = (item / ".git").exists()
                is_python = (item / "pyproject.toml").exists() or (item / "setup.py").exists()
                is_node = (item / "package.json").exists()

                # Get last modified time
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    last_mod = mtime.strftime("%Y-%m-%d %H:%M")
                except:
                    last_mod = "N/A"

                projects.append({
                    "name": item.name,
                    "path": str(item),
                    "is_git": is_git,
                    "is_python": is_python,
                    "is_node": is_node,
                    "last_modified": last_mod,
                })

        return projects

    def select_project(self, name: str) -> Optional[Dict]:
        """Select a project by name."""
        # Find project
        project_path = PROJECTS_DIR / name
        if not project_path.exists():
            return None

        # Initialize project state if not exists
        if name not in self.state.projects:
            self.state.projects[name] = ProjectState(
                name=name,
                path=str(project_path),
            )

        # Get branches if git repo
        proj = self.state.projects[name]
        if (project_path / ".git").exists():
            proj.branches = self._get_branches(project_path)
            if not proj.current_branch and proj.branches:
                proj.current_branch = self._get_current_branch(project_path)

        self.state.current_project = name
        proj.last_activity = datetime.utcnow().isoformat()
        self._save_state()

        return {
            "name": name,
            "path": str(project_path),
            "branch": proj.current_branch,
            "branches": proj.branches,
            "sessions": proj.sessions,
            "worktrees": proj.worktrees,
        }

    def get_current_project(self) -> Optional[Dict]:
        """Get current project info."""
        if not self.state.current_project:
            return None
        return self.select_project(self.state.current_project)

    def list_branches(self, project_name: str = None) -> List[str]:
        """List branches for a project."""
        name = project_name or self.state.current_project
        if not name:
            return []

        project_path = PROJECTS_DIR / name
        if not (project_path / ".git").exists():
            return []

        return self._get_branches(project_path)

    def select_branch(self, branch: str, project_name: str = None) -> bool:
        """Select a branch for a project."""
        name = project_name or self.state.current_project
        if not name:
            return False

        project_path = PROJECTS_DIR / name
        if not (project_path / ".git").exists():
            return False

        # Checkout branch
        try:
            result = subprocess.run(
                ["git", "checkout", branch],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                if name in self.state.projects:
                    self.state.projects[name].current_branch = branch
                    self.state.projects[name].last_activity = datetime.utcnow().isoformat()
                    self._save_state()
                return True
        except Exception:
            pass
        return False

    def create_branch(self, branch: str, project_name: str = None) -> bool:
        """Create and checkout a new branch."""
        name = project_name or self.state.current_project
        if not name:
            return False

        project_path = PROJECTS_DIR / name
        if not (project_path / ".git").exists():
            return False

        try:
            result = subprocess.run(
                ["git", "checkout", "-b", branch],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                if name not in self.state.projects:
                    self.state.projects[name] = ProjectState(name=name, path=str(project_path))
                self.state.projects[name].current_branch = branch
                self.state.projects[name].branches = self._get_branches(project_path)
                self.state.projects[name].last_activity = datetime.utcnow().isoformat()
                self._save_state()
                return True
        except Exception:
            pass
        return False

    def list_sessions(self, project_name: str = None) -> List[Dict]:
        """List sessions for a project."""
        name = project_name or self.state.current_project
        if not name or name not in self.state.projects:
            return []
        return self.state.projects[name].sessions

    def create_session(self, title: str, project_name: str = None) -> Dict:
        """Create a new session for a project."""
        name = project_name or self.state.current_project
        if not name:
            return {"error": "No project selected"}

        if name not in self.state.projects:
            self.state.projects[name] = ProjectState(
                name=name,
                path=str(PROJECTS_DIR / name),
            )

        session = {
            "id": f"sess_{len(self.state.projects[name].sessions) + 1}",
            "title": title,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "branch": self.state.projects[name].current_branch,
            "messages": [],
        }

        self.state.projects[name].sessions.append(session)
        self.state.projects[name].last_activity = datetime.utcnow().isoformat()
        self._save_state()

        return session

    def list_worktrees(self, project_name: str = None) -> List[Dict]:
        """List worktrees for a project."""
        name = project_name or self.state.current_project
        if not name:
            return []

        project_path = PROJECTS_DIR / name
        if not (project_path / ".git").exists():
            return []

        # Get git worktrees
        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                worktrees = []
                current = {}
                for line in result.stdout.splitlines():
                    if line.startswith("worktree "):
                        if current:
                            worktrees.append(current)
                        current = {"path": line[10:]}
                    elif line.startswith("HEAD "):
                        current["head"] = line[5:]
                    elif line.startswith("branch "):
                        current["branch"] = line[7:]
                if current:
                    worktrees.append(current)

                # Save to state
                if name in self.state.projects:
                    self.state.projects[name].worktrees = worktrees
                    self._save_state()

                return worktrees
        except Exception:
            pass

        return self.state.projects.get(name, ProjectState(name="")).worktrees

    def create_worktree(self, branch: str, path: str = None, project_name: str = None) -> Dict:
        """Create a new worktree."""
        name = project_name or self.state.current_project
        if not name:
            return {"error": "No project selected"}

        project_path = PROJECTS_DIR / name
        if not (project_path / ".git").exists():
            return {"error": "Not a git repository"}

        if not path:
            path = str(project_path / ".worktrees" / branch)

        try:
            result = subprocess.run(
                ["git", "worktree", "add", path, "-b", branch],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                worktrees = self.list_worktrees(name)
                return {"success": True, "path": path, "worktrees": worktrees}
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def get_git_status(self, project_name: str = None) -> Dict:
        """Get git status for a project."""
        name = project_name or self.state.current_project
        if not name:
            return {"error": "No project selected"}

        project_path = PROJECTS_DIR / name
        if not (project_path / ".git").exists():
            return {"error": "Not a git repository"}

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            changed = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0

            result2 = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            commits = result2.stdout.strip().splitlines() if result2.stdout else []

            return {
                "branch": self._get_current_branch(project_path),
                "changed_files": changed,
                "recent_commits": commits,
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_branches(self, project_path: Path) -> List[str]:
        """Get git branches for a project."""
        try:
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return [b.strip() for b in result.stdout.splitlines() if b.strip()]
        except Exception:
            pass
        return []

    def _get_current_branch(self, project_path: Path) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""
