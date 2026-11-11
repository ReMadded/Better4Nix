{ pkgs ? import (builtins.fetchTarball { url = "https://github.com/NixOS/nixpkgs/archive/nixos-24.05.tar.gz"; sha256 = "sha256-OnSAY7XDSx7CtDoqNh8jwVwh4xNL/2HaJxGjryLWzX8="; }) {} }:
pkgs.mkShell {
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
