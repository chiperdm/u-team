---
name: termux-android-dev
description: "Develop on an Android phone with Termux: correct install source, packages (node, python, git, ssh), storage and wake-lock, project layout, running servers and bots, Android 12+ phantom process killer, building and testing limits, proot-distro, offloading APK builds to CI, safe git and secrets. Use when the user works from Termux, a phone-only workflow, or hits Termux errors (EACCES, symlink, native module build, killed processes)."
domain: devops
---

# Termux development workflow

Termux is great for editing, git, Node/Python scripts, Telegram bots, small servers and SSH to a VPS. It is a poor place for heavy Android/Flutter builds: offload those to CI.

## Install and base setup
- Install Termux from **F-Droid** or the official GitHub releases; the old Google Play build is outdated and breaks package installs. Use the same source for add-ons (Termux:API, Termux:Boot).
```bash
pkg update && pkg upgrade -y
pkg install -y git nodejs-lts python openssh curl jq ripgrep micro   # nano/vim also fine
termux-setup-storage                 # grants ~/storage/* access (shared storage)
git config --global user.name "Name" && git config --global user.email "you@example.com"
```
- Keep projects in `$HOME` (`~/projects/...`), **not** in `/sdcard` (no symlinks, no exec bit, slow): `node_modules` and git break there. Copy deliverables out to `~/storage/downloads` when needed.
- Keep the session alive: `termux-wake-lock` (or the notification action), and exempt Termux from battery optimization in Android settings. Use `tmux` (`pkg install tmux`) so long processes survive disconnects.

## Android 12+ background kills
Android may kill Termux child processes ("phantom process killer", `[Process completed (signal 9)]`). Remedies (verify for your Android version): disable the child-process restriction in Developer options on Android 14+, or on older versions use `adb` (from another device or wireless debugging) to disable phantom process monitoring; keep wake lock; avoid spawning huge process trees (use `npm ci --no-audit --no-fund`, limit parallel jobs `-j2`).

## Node and Python
- `npm i` works for pure-JS packages. Native addons (`better-sqlite3`, `sharp`, `bcrypt`) need `pkg install python make clang binutils` and may still fail: prefer pure alternatives (`bcryptjs`, `sql.js`), or run the code on a VPS/Render.
- Python: `pip install` inside a venv (`python -m venv .venv`); heavy scientific wheels often fail on ARM/bionic: use `pkg install python-numpy` etc. where available.
- Run servers bound to `0.0.0.0` only if you mean to expose them on the network; default `127.0.0.1`. Access from the phone browser at `http://127.0.0.1:PORT`.
- Environment/secrets: `~/.env` files with `chmod 600`; never commit; `export $(grep -v '^#' .env | xargs)` or `dotenv`.

## Git and SSH
```bash
ssh-keygen -t ed25519 -C "termux" && cat ~/.ssh/id_ed25519.pub     # add to GitHub as a deploy/user key
git remote set-url origin git@github.com:user/repo.git
```
Commit small and often (phone sessions die): `git add -p`, `git commit`, `git push`. Use `.gitignore` for `node_modules`, `.env`, build outputs. The pack's `hooks/pre-commit-secret-scan.sh` runs under Termux's bash.

## Heavier needs
- **proot-distro** (`pkg install proot-distro; proot-distro install debian; proot-distro login debian`) gives a glibc userland for tools that expect Linux; slower and not for everything.
- **Android APK / Flutter builds:** possible but fragile (SDK, aapt2, memory). Recommended: push to GitHub and build in Actions (`devops-ci-flutter-node`, `devops-android-release`), download the artifact. Keep keystore in CI secrets, not on the phone.
- **Bigger IDE-like work:** SSH to a VPS and edit there (tmux + micro/vim), or use code-server on the VPS (behind TLS and auth).
- **Termux:API** (`pkg install termux-api` + the add-on app): `termux-clipboard-get`, `termux-notification`, `termux-battery-status`, `termux-tts-speak`: useful for scripts, not for production services.
- **Termux:Boot** for starting a script at device boot (needs the add-on and battery exemption).

## Safe working habits
- Backup: `git push` is the backup; also `tar czf ~/storage/downloads/proj-$(date +%F).tgz proj` before risky operations.
- `rm -rf` carefully (no undo): `ls` the path first; avoid globbing in `$HOME`.
- Don't paste real tokens into chats/AI prompts (`security-secrets-logging`).
- Screen is small: keep functions/files short, wrap long lines, use `rg -n` + `micro file:line`.

## Troubleshooting table
| Symptom | Likely cause / fix |
|---|---|
| `EACCES`/permission denied on npm | project is on `/sdcard`; move to `$HOME` |
| `ENOSPC` / watcher limit | reduce watchers, use `--no-watch`, restart; clean `~/.npm/_cacache` |
| `pkg` "unable to locate package" | `termux-change-repo`, `pkg update` |
| Killed `[Process completed (signal 9)]` | phantom process killer / OOM: see above, lower memory use |
| TLS/cert errors | `pkg install ca-certificates` and `pkg upgrade` |
| Gradle "aapt2 not found" | do not build here; use CI |
| Slow `npm install` | use `npm ci`, cache, or `pnpm` (`pkg install nodejs-lts; npm i -g pnpm`) |

## Verify
`node -v && git --version`; project runs from `$HOME` with `npm test`; a push reaches the remote; process survives screen-off with wake lock; CI builds what Termux cannot.

## Pitfalls
- Editing the same repo from phone and PC without pulling first (conflicts): `git pull --rebase` before starting.
- Leaving a server on `0.0.0.0` on public Wi-Fi.
- Treating Termux as production hosting (no supervision, killed by Android).
