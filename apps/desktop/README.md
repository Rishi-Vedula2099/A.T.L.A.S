# A.T.L.A.S — Desktop Shell (Tauri)

This directory contains the Tauri v2 wrapper that packages the Next.js dashboard as a native desktop application.

## Prerequisites

- [Rust](https://rustup.rs/) (stable toolchain)
- [Node.js](https://nodejs.org/) 20+
- Platform-specific native build tools:
  - **Windows:** Visual Studio Build Tools + Windows SDK
  - **macOS:** Xcode Command Line Tools (`xcode-select --install`)
  - **Linux:** `libwebkit2gtk-4.1-dev`, `libgtk-3-dev`, `libappindicator3-dev`, `librsvg2-dev`, `libssl-dev`, `patchelf`

## Development

```bash
cd apps/desktop/src-tauri
cargo tauri dev
```

This launches both the Next.js dev server and the Tauri window.

## Production Build

```bash
cd apps/desktop/src-tauri
cargo tauri build
```

Output installers are in `src-tauri/target/release/bundle/`:
- Windows: `.msi`, `.exe` (NSIS)
- macOS: `.dmg`
- Linux: `.deb`, `.AppImage`

## First-Run Bootstrap

When the desktop app launches, it checks for `~/.atlas/.env`. If missing, it invokes the installer script (`install` or `install.bat`) to bootstrap Docker, generate secrets, and start the stack. A loading screen is shown until the healthchecks pass.

## Icons

Replace the placeholder files in `src-tauri/icons/` with branded icons. See [Tauri icon docs](https://v2.tauri.app/reference/config/#bundleconfig.icons).