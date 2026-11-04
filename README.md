# Better4Nix
# 🏢 ReMadded: Better4Nix

> Better4Nix is an elegant open-source tool developed by the ReMadded indie lab that allows developers to generate and manage declarative Nix environments using pure, simple Python code.

If you know Python but want to avoid the complex functional syntax of Nix, Better4Nix handles the heavy lifting for you, including automated integration with the NUR (Nix User Repository).

---

## ✨ Features

* Pure Python Control: Define your system dependencies and development tools using familiar Python structures.
* Automated Nix Generation: Instantly compiles your configurations into native shell.nix architectures.
* NUR Support Out-of-the-Box: Easily fetch community packages and missing programming languages straight from the Nix User Repository.
* Multi-Language Workspace: Configure isolated developer environments for Go, Node.js, Rust, or any language you need.

---

## 🚀 Getting Started (Quick Setup)

### 1. Clone the Corporate Repository
git clone https://github.com
cd Better4Nix
### 2. Configure via Python
Open main.py and describe your environment using simple Python methods:
from main import Better4NixConfig

config = Better4NixConfig()
config.add_languages(["nodejs", "go", "git"])
config.add_from_nur("repos.mic92.hello") # Fetching straight from NUR
config.compile()
### 3. Launch the Environment
Run the script to generate your .nix architecture, then let Nix build your workspace:
python main.py
nix-shell
---

## 🛠 Project Roadmap
- [x] Initial Repository Architecture (MIT License & Gitignore)
- [x] Approved Brand IP & Trademark Verification (Catalonia, Spain)
- [ ] Core Better4Nix Python Compiler Module
- [ ] Interactive Console Menu Mode
- [ ] Automated nix-shell Environment Auto-Launcher

---

## 📜 Corporate License
This project is officially created by the ReMadded indie lab (Catalonia, Spain) and is distributed under the friendly MIT License. For more details, see the [LICENSE](LICENSE) file.

Copyright (c) 2026 ReMadded. All rights reserved.
