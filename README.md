# 🏢 ReMadded: Better4Nix

> **Better4Nix** is an elegant open-source tool developed by the ReMadded indie lab that lets you generate and manage declarative Nix environments using pure, simple Python code.

If you know Python but want to avoid the complex functional syntax of Nix, Better4Nix handles the heavy lifting for you: you describe your environment in familiar syntax, and Better4Nix compiles it into a native `shell.nix`. Nix still provides the isolation, reproducibility, and atomic rollbacks — Better4Nix just gives you a friendly frontend.

> **Status: v0.1 (beta).** The core works end-to-end. One frontend (Python) is available. NUR support exists in the DSL but is not enabled in the demo — see the Roadmap.

---

## ✨ Features

- **Pure Python Control** — Define your system dependencies and development tools using familiar Python structures.
- **Automated Nix Generation** — Instantly compiles your configuration into a native `shell.nix` architecture based on `pkgs.mkShell`.
- **Verified Languages** — `nodejs`, `go`, `rustup` (Rust), `python3` are tested. Also available in `nixpkgs`: `jdk`, `gcc`, `zig`, `ruby`, `php`, `lua`.
- **Arbitrary Packages** — Add any `nixpkgs` package with `packages=[...]` (`git`, `ripgrep`, ...).
- **Shell Hooks** — Run a command when the environment starts with `shell_hook="..."`.
- **Unfree Support** — Set `allow_unfree=True` to allow unfree packages (generates `config.allowUnfree = true`).
- **Plugin Architecture** — Frontends are separate packages named `better4nix-frontend-<ext>`, discovered on `PATH`. The core contains no parsers.

## 🚧 Not Ready Yet

- **`from_nur=[...]`** — exists in the DSL, but is **not used in the demo**. NUR packages can fail due to unfree licenses, missing `cargoHash`, or incompatibility with the current `<nixpkgs>`. Pinning nixpkgs is on the roadmap.
- **`nixpkgs_rev`** — accepted by the DSL, not implemented yet.
- **Flakes** — not supported yet.
- **Other frontends** (JS, Go, ...) — on the roadmap.

---

## 🚀 Getting Started (Quick Setup)

### 0. Requirements

- Python 3.10+
- `pip`
- Nix with `nix-shell`

### 1. Clone the Corporate Repository

```bash
git clone https://github.com/ReMadded/Better4Nix
cd Better4Nix
```

### 2. Install the Core

```bash
pip install -e .
```

### 3. Install the Python Frontend

```bash
cd frontends/python
pip install -e .
cd ../..
```

> If `better4nix` or `better4nix-frontend-py` is not found, add the scripts directory to `PATH`:
> ```bash
> export PATH="$(python -c "import sysconfig; print(sysconfig.get_path('scripts'))"):$PATH"
> hash -r
> ```

### 4. Configure via Python

Open `examples/config.py` and describe your environment using simple Python methods:

```python
env(
    languages=["nodejs", "go", "rustup"],
    packages=["git", "ripgrep"],
    shell_hook="echo 'dev shell ready'",
)
```

### 5. Launch the Environment

```bash
better4nix build examples/config.py
nix-shell examples/config.nix --run 'node --version; go version; echo OK'
```

Generated `examples/config.nix`:

```nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    nodejs
    go
    rustup
    git
    ripgrep
  ];
  shellHook = "echo 'dev shell ready'";
}
```

---

## 🐍 The Python Subset

A config file must contain **exactly one** top-level `env(...)` call. Inside it, only these constructs are allowed:

- literals: `dict`, `list`, `str`, `int`, `bool`, `None`;
- calls to `env(...)`, `let(...)`, `with_(...)`;
- keyword arguments.

Anything else — `class`, `def`, `for`, `while`, `if`, `import`, `try`, generators, decorators, f-strings — is rejected with an error and a line number. The Python frontend parses with `ast.parse` and **does not execute** your file.

## 🧠 How It Works

```
config.py  →  [better4nix-frontend-py]  →  JSON AST (ast-v1)  →  [better4nix core]  →  shell.nix
```

- The **frontend** knows Python, produces a JSON AST, and rejects anything outside the allowed subset.
- The **core** knows the JSON AST and Nix; it validates the AST and renders Nix.
- The contract is `schemas/ast-v1.json`. Any language can be a frontend as long as it produces that JSON.

---

## 🛠 Project Roadmap

- [x] Initial Repository Architecture (MIT License & Gitignore)
- [x] Core Better4Nix Python Compiler Module
- [x] Python Frontend (`better4nix-frontend-py`)
- [x] End-to-end: `config.py` → `shell.nix` → `nix-shell`
- [ ] Pin nixpkgs (`nixpkgs_rev`) for reproducibility and stable NUR packages
- [ ] `from_nur` examples verified against a pinned nixpkgs
- [ ] Own NUR repo / flake with a small set of verified packages
- [ ] JS / Go frontends
- [ ] Flake output (`flake.nix` + `nix develop`)

---

## 📜 Corporate License

This project is officially created by the ReMadded indie lab (Catalonia, Spain) and is distributed under the friendly MIT License. For more details, see the LICENSE file.

Copyright (c) 2026 ReMadded. All rights reserved.