"""Report each herdr Space's PR (gh) or MR (glab) as the `$pr` workspace token.

  daemon            poll all Spaces every POLL_SECS (single instance via pidfile)
  refresh           refresh the Space in HERDR_WORKSPACE_ID (or all if unset)
  refresh --all     refresh all Spaces
"""
import json
import os
import subprocess
import sys
import time

HERDR = os.environ.get("HERDR_BIN_PATH", "herdr")
SOURCE = "flyingdot.pr-status"
POLL_SECS = 120
TTL_MS = POLL_SECS * 3 * 1000  # stale values vanish if the poller dies


def run(cmd, cwd=None, timeout=20):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.stdout if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def workspaces():
    out = run([HERDR, "workspace", "list"])
    if not out:
        return []
    return json.loads(out)["result"]["workspaces"]


def github(path):
    out = run(["gh", "pr", "view", "--json", "number,state,isDraft,reviewDecision"], cwd=path)
    if not out:
        return None
    pr = json.loads(out)
    state = "draft" if pr["isDraft"] and pr["state"] == "OPEN" else pr["state"].lower()
    review = {"APPROVED": " ✓", "CHANGES_REQUESTED": " ✗"}.get(pr.get("reviewDecision") or "", "")
    return f"PR #{pr['number']} {state}{review}"


def gitlab(path):
    branch = (run(["git", "branch", "--show-current"], cwd=path) or "").strip()
    out = run(["glab", "mr", "list", "--source-branch", branch, "--all", "--output", "json"], cwd=path) if branch else None
    mrs = json.loads(out) if out else []
    if not mrs:
        return None
    # A branch can have several MRs: prefer an open one, then the most recently updated.
    mr = max(mrs, key=lambda m: (m["state"] == "opened", m["updated_at"]))
    state = "draft" if mr.get("draft") and mr["state"] == "opened" else mr["state"].replace("opened", "open")
    return f"MR !{mr['iid']} {state}"


def pr_label(path):
    remote = run(["git", "config", "--get", "remote.origin.url"], cwd=path) or ""
    if not remote:
        return None
    if "github.com" in remote:
        return github(path)
    return gitlab(path)  # gitlab.com or any self-hosted GitLab glab is logged in to


def refresh(only=None):
    for ws in workspaces():
        if only and ws["workspace_id"] != only:
            continue
        path = (ws.get("worktree") or {}).get("checkout_path")
        label = pr_label(path) if path else None
        args = [HERDR, "workspace", "report-metadata", ws["workspace_id"], "--source", SOURCE]
        args += ["--token", f"pr={label}", "--ttl-ms", str(TTL_MS)] if label else ["--clear-token", "pr"]
        run(args)


def daemon():
    pidfile = os.path.join(os.environ.get("HERDR_PLUGIN_STATE_DIR", "/tmp"), "daemon.pid")
    try:
        with open(pidfile) as f:
            os.kill(int(f.read()), 0)
        return  # already running
    except (OSError, ValueError):
        pass
    with open(pidfile, "w") as f:
        f.write(str(os.getpid()))
    while True:
        refresh()
        time.sleep(POLL_SECS)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "refresh"
    if cmd == "daemon":
        daemon()
    else:
        refresh(None if "--all" in sys.argv else os.environ.get("HERDR_WORKSPACE_ID"))
