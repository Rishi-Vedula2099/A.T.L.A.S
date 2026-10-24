# A.T.L.A.S Installer

One-shot, cross-platform installer that brings the full ATLAS stack up with
**zero manual setup**: OS / arch / RAM / GPU detection, Docker installation,
secure secret generation, image pull + build, service startup, healthchecks,
and (on success) opening the desktop app.

> **Goal:** the user downloads the repo, runs ONE command, and the entire stack
> is running. No `docker compose up`, no `.env` editing, no manual key
> generation.

---

## Quick start

**macOS / Linux**

```bash
./install
```

**Windows** (cmd, PowerShell, or double-click in Explorer)

```bat
install.bat
```

That's it. On a clean machine the installer will:

1. Detect OS, CPU architecture, RAM, GPU, and disk space.
2. Detect Docker; install it if missing (see [platform notes](#platform-notes)).
3. Generate cryptographically strong secrets into `~/.atlas/.env` (or
   `%USERPROFILE%\.atlas\.env` on Windows).
4. Build and pull all images.
5. Start the stack with `docker compose up -d`.
6. Wait for `http://localhost/readyz` to return healthy.
7. Open the dashboard at `http://localhost`.

Re-running the installer is **idempotent** — secrets are preserved, only
changed images are rebuilt.

---

## Flags

| Flag                    | Effect                                                       |
|-------------------------|--------------------------------------------------------------|
| `--force-secrets`       | Regenerate ALL secrets (rotates DB passwords, JWT keys, backup key). Destructive. |
| `--no-pull`             | Skip `docker compose pull`; use cached images.              |
| `--profile <name>`      | Enable a compose profile (`observability`, `messaging`, `gpu`, `backup`). Repeatable. |
| `--skip-open`           | Do not auto-open the browser/app at the end.                |

POSIX flags are passed to `install` / `install.ps1`. On Windows cmd use
`install.bat --profile observability` (forwarded through to PowerShell).

---

## Where secrets live

All secrets are written to a single per-user file outside the repo:

- **macOS / Linux:** `~/.atlas/.env`
- **Windows:** `%USERPROFILE%\.atlas\.env`

The installer mirrors this file into `<repo>/.env` so that `docker compose`
picks it up automatically. Both locations are covered by `.gitignore` — secrets
are never committed.

To **add API keys** (OpenAI, Anthropic, Gemini, ElevenLabs, Porcupine) after
install, edit `~/.atlas/.env` directly and re-run the installer (it preserves
all existing values).

---

## Platform notes

### Linux
- Docker Engine installed via `https://get.docker.com`.
- Current user is added to the `docker` group; you may need to log out and back
  in (or run `newgrp docker`) for the change to take effect.
- If systemd is present, the daemon is enabled and started.

### macOS
- Docker Desktop is installed via `brew install --cask docker` (Homebrew must
  be present).
- Docker Desktop is launched automatically and the installer waits up to 3
  minutes for the daemon. If you have never launched it before you must accept
  the license agreement when prompted.

### Windows
- Docker Desktop is installed via `winget install Docker.DockerDesktop`.
- **Docker Desktop cannot be started silently.** After install, the installer
  prints instructions and exits. Launch Docker Desktop from the Start Menu,
  accept the license, wait for the whale tray icon to become steady, then
  re-run `install.bat`. This is the only unavoidable manual step on Windows.

---

## What the installer detects

```
============================================================
 A.T.L.A.S — host detection report
============================================================
  OS            : linux | macos | windows
  Architecture  : x64 | arm64
  RAM (MB)      : 32768
  Disk free (MB): 204800
  GPU           : NVIDIA GeForce RTX 4090  (or "none")
  Docker        : 27.0.1
  Compose v2    : yes
============================================================
```

---

## Layout

```
install                    # POSIX entrypoint (bash)
install.bat                # Windows cmd entrypoint -> install.ps1
install.ps1                # Windows PowerShell entrypoint
installer/
├── README.md              # this file
└── lib/
    ├── detect.sh          # POSIX detection
    ├── detect.ps1         # Windows detection
    ├── docker_install.sh  # POSIX Docker install
    ├── docker_install.ps1 # Windows Docker install
    ├── bootstrap.sh       # POSIX orchestrator
    ├── bootstrap.ps1      # Windows orchestrator
    ├── secrets.py         # Secure .env generation (shared by both platforms)
    └── healthcheck.py     # Poll /readyz until healthy (shared by both platforms)
```

The Python helpers are shared — both the POSIX and Windows paths use the same
`secrets.py` and `healthcheck.py` so secret format and health semantics are
identical across platforms.

---

## Troubleshooting

If the installer fails:

```bash
python scripts/doctor.py    # POSIX
python scripts\doctor.py    # Windows
```

`doctor.py` checks Docker daemon state, port conflicts, `.env` integrity, and
each compose service's health, then prints a traffic-light report pointing at
the most likely cause. See [docs/deployment.md](../docs/deployment.md) for the
full troubleshooting matrix.
