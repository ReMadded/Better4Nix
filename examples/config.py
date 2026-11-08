env(
    languages=["nodejs", "go", "rustc", "cargo"],
    packages=["git", "ripgrep"],
    from_nur=["repos.milahu.sqlite"],
    shell_hook="echo 'dev shell ready'",
    # allow_unfree=True,  # раскомментируй, если NUR-пакет тянет unfree
)