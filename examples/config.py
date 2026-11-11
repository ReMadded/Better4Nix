env(
    languages=["nodejs", "go", "rustc", "cargo"],
    packages=["git", "ripgrep"],
    nixpkgs_rev="nixos-24.05",
    nixpkgs_sha256="sha256-OnSAY7XDSx7CtDoqNh8jwVwh4xNL/2HaJxGjryLWzX8=",
    # from_nur=["repos.milahu.sqlite"],
    shell_hook="echo 'dev shell ready'",
    # allow_unfree=True,  # раскомментируй, если NUR-пакет тянет unfree
)