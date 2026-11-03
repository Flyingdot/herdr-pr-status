# herdr-pr-status

A [herdr](https://herdr.dev) plugin that shows the pull request or merge request of each Space's branch in the sidebar.

- GitHub remotes (`github.com`) are queried with `gh`.
- Every other remote is queried with `glab`, so self-hosted GitLab works as long as `glab` is logged in to that host.
- If a branch has several MRs, an open one wins, otherwise the most recently updated one.

Values look like `PR #12 open ✓`, `PR #7 draft` or `MR !42 merged` and are reported as the `$pr` workspace token. They refresh every 2 minutes, when a Space is focused or created, and on the "PR/MR status: refresh all Spaces" action.

## Install

```sh
herdr plugin install Flyingdot/herdr-pr-status
```

Install it on every machine whose Spaces you want covered: each herdr server reports its own Spaces. The poller starts with the herdr server, so restart the server once after installing.

Requires `python3`, `git`, and a logged-in `gh` and/or `glab`.

## Sidebar

Add `$pr` to a Space row in `config.toml`, for example:

```toml
[ui.sidebar.spaces]
rows = [
  ["state_icon", "workspace"],
  ["branch", "git_status", { token = "$pr", fg = "#8839ef", rules = [
    { contains = "draft", dim = true },
    { contains = "merged", fg = "#7287fd" },
    { contains = "closed", hide = true },
  ] }],
]
```
