# herdr-pr-status

A [herdr](https://herdr.dev) plugin that shows the pull request or merge request of each Space's branch in the sidebar.

- GitHub remotes (`github.com`) are queried with `gh`.
- Every other remote is queried with `glab`, so self-hosted GitLab works as long as `glab` is logged in to that host.
- If a branch has several MRs, an open one wins, otherwise the most recently updated one.

Each value is a state icon followed by the number (`#12` for a GitHub PR, `!42` for a GitLab MR). GitHub PRs also get a review icon once they're approved or have changes requested. The value is reported as the `$pr` workspace token and refreshes every 2 minutes, when a Space is focused or created, and on the "PR/MR status: refresh all Spaces" action.

The icons are [Nerd Font](https://www.nerdfonts.com) octicons, so your terminal needs a Nerd Font:

| State | Octicon | Codepoint |
|---|---|---|
| open | `git_pull_request` | U+F407 |
| draft | `git_pull_request_draft` | U+F4DD |
| merged | `git_merge` | U+F419 |
| closed | `git_pull_request_closed` | U+F4DC |
| approved (GitHub) | `check` | U+F42E |
| changes requested (GitHub) | `x` | U+F467 |

## Install

```sh
herdr plugin install Flyingdot/herdr-pr-status
```

Install it on every machine whose Spaces you want covered: each herdr server reports its own Spaces. The poller starts with the herdr server, so restart the server once after installing.

Requires `python3`, `git`, and a logged-in `gh` and/or `glab`.

## Sidebar

Add `$pr` to a Space row in `config.toml`. Sidebar rules match on the icon, so each state can get its own color. The first matching rule wins, so the review icons come first. The strings below contain the icon glyphs, which only show up with a Nerd Font.

```toml
[ui.sidebar.spaces]
rows = [
  ["state_icon", "workspace"],
  ["branch", "git_status", { token = "$pr", fg = "#38913a", rules = [
    { contains = "", fg = "#e0404a" },              # changes requested: red
    { contains = "", fg = "#38913a", bold = true }, # approved: bold green
    { contains = "", fg = "#7c7f93" },              # draft: grey
    { contains = "", fg = "#8a5cf0" },              # merged: violet
    { contains = "", hide = true },                 # closed: hidden
  ] }],
]
```

Open PRs use the token's default color (green). These colors have similar contrast on light and dark Catppuccin sidebars.
