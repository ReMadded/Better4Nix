# 🏢 ReMadded: Better4Nix

> **Better4Nix** is an elegant open-source tool developed by the ReMadded indie lab that lets you generate and manage declarative Nix environments using pure, simple Python code.

If you know Python but want to avoid the complex functional syntax of Nix, Better4Nix handles the heavy lifting for you: you describe your environment in familiar syntax, and Better4Nix compiles it into a native `shell.nix`. Nix still provides the isolation, reproducibility, and atomic rollbacks — Better4Nix just gives you a friendly frontend.

> **Status: v0.3 (beta).** The core works end-to-end. Rust (`rustc` + `cargo`) is verified. Pinning is implemented via `nixpkgs_rev` + `nixpkgs_sha256` and via flakes (`flake.nix` + `flake.lock`). One frontend (Python) is available. NUR support exists in the DSL but is not fully enabled in the demo.

---

## ✨ Features

  * **Pure Python Control** — Define your system dependencies and development tools using familiar Python structures.
  * **Automated Nix Generation** — Instantly compiles your configuration into a native `shell.nix` architecture based on `pkgs.mkShell`.
  * **Verified Languages** — `nodejs`, `go`, `python3`, `rustc` + `cargo` (Rust) are tested. Also available in `nixpkgs`: `jdk`, `gcc`, `zig`, `ruby`, `php`, `lua`.
  * **Arbitrary Packages** — Add any `nixpkgs` package with `packages=[...]` (`git`, `ripgrep`, ...).
  * **Shell Hooks** — Run a command when the environment starts with `shell_hook="..."`.
  * **Unfree Support** — Set `allow_unfree=True` to allow unfree packages (generates `config.allowUnfree = true`).
  * **Plugin Architecture** — Frontends are separate packages named `better4nix-frontend-<ext>`, discovered on `PATH`. The core contains no parsers.

### Rust note

For Rust, use `rustc` and `cargo` (not `rustup`, not `rust`):

    env(
        languages=["rustc", "cargo"],
    )

  * `rustc` and `cargo` are real derivations in `nixpkgs` — reproducible, no network download at runtime.
  * `rustup` downloads toolchains from the internet on first run — **not** reproducible.
  * `rust` in `nixpkgs` is a helper attrset for building Rust packages, **not** a package — it cannot be placed in `buildInputs`.

---

## 🚧 Not Ready Yet

  * **`from_nur=[...]`** — exists in the DSL, but is **not enabled in the demo**. NUR packages can fail due to unfree licenses, missing `cargoHash`, outdated `hash`, or incompatibility with the current `<nixpkgs>`. Even with `nixpkgs_rev` + `nixpkgs_sha256` pinning, NUR packages may be broken upstream. A hash fix for the `sqlite` NUR package was sent to `milahu/nur-packages`, but the PR was closed: that package is for the `reuse-schema` branch and is outdated for `main`. **Use `sqlite` from `nixpkgs` instead.**
  * **Flakes** — not supported yet.
  * **Other frontends** (JS, Go, ...) — on the roadmap.

---

## 🚀 Getting Started (Quick Setup)

### 0. Requirements

  * Python 3.10+
  * `pip`
  * Nix with `nix-shell`

### 1. Clone the Corporate Repository

    git clone https://github.com/ReMadded/Better4Nix
    cd Better4Nix

### 2. Install the Core

    pip install -e .

### 3. Install the Python Frontend

    cd frontends/python
    pip install -e .
    cd ../..

> If `better4nix` or `better4nix-frontend-py` is not found, add the scripts directory to `PATH`:
>
>     export PATH="$(python -c "import sysconfig; print(sysconfig.get_path('scripts'))"):$PATH"hash -r

### 4. Configure via Python

Open `examples/config.py` and describe your environment using simple Python methods:

    env(
        languages=["nodejs", "go", "rustc", "cargo"],
        packages=["git", "ripgrep"],
        nixpkgs_rev="nixos-24.05",
        nixpkgs_sha256="sha256-OnSAY7XDSx7CtDoqNh8jwVwh4xNL/2HaJxGjryLWzX8=",
        shell_hook="echo 'dev shell ready'",
    )

### 5. Launch the Environment

    better4nix build examples/config.py
    nix-shell examples/config.nix --run 'node --version; go version; rustc --version; echo OK'

Generated `examples/config.nix`:

    { pkgs ? import (builtins.fetchTarball { url = "https://github.com/NixOS/nixpkgs/archive/nixos-24.05.tar.gz"; sha256 = "sha256-OnSAY7..."; }) {} }:
    pkgs.mkShell{
      buildInputs = with pkgs; [
        nodejs
        go
        rustc
        cargo
        git
        ripgrep
      ];
      shellHook = "echo 'dev shell ready'";
    }

Alternatively, the repository ships a `flake.nix`. To enter the dev shell:

    nix develop

This pins all inputs via `flake.lock` — no need for `nixpkgs_rev` / `nixpkgs_sha256`.

---

## 🐍 The Python Subset

A config file must contain **exactly one** top-level `env(...)` call. Inside it, only these constructs are allowed:

  * literals: `dict`, `list`, `str`, `int`, `bool`, `None`;
  * calls to `env(...)`, `let(...)`, `with_(...)`;
  * keyword arguments.

Anything else — `class`, `def`, `for`, `while`, `if`, `import`, `try`, generators, decorators, f-strings — is rejected with an error and a line number. The Python frontend parses with `ast.parse` and **does not execute** your file.

---

## 🧠 How It Works

    config.py  →  [better4nix-frontend-py]  →  JSON AST (ast-v1)  →  [better4nix core]  →  shell.nix

  * The **frontend** knows Python, produces a JSON AST, and rejects anything outside the allowed subset.
  * The **core** knows the JSON AST and Nix; it validates the AST and renders Nix.
  * The contract is `schemas/ast-v1.json`. Any language can be a frontend as long as it produces that JSON.

---

## 🛠 Project Roadmap

  * [x] Initial Repository Architecture (MIT License & Gitignore)
  * [x] Core Better4Nix Python Compiler Module
  * [x] Python Frontend (`better4nix-frontend-py`)
  * [x] End-to-end: `config.py` → `shell.nix` → `nix-shell`
  * [x] Rust support verified (`rustc` + `cargo` via `languages=[...]`)
  * [x] Pin nixpkgs (`nixpkgs_rev`) for reproducibility and stable NUR packages
  * [ ] `from_nur` examples verified against a pinned nixpkgs
  * [ ] Own NUR repo / flake with a small set of verified packages
  * [ ] JS / Go frontends
  * [x] Flake output (`flake.nix` \+ `nix develop`)

---

## 📜 Corporate License

This project is officially created by the ReMadded indie lab (Catalonia, Spain) and is distributed under the friendly MIT License. For more details, see the LICENSE file.

Copyright (c) 2026 ReMadded. All rights reserved.