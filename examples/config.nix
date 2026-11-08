{ pkgs ? import <nixpkgs> {} }:
let
  nur = import (builtins.fetchTarball "https://github.com/nix-community/NUR/archive/master.tar.gz") { inherit pkgs; };
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    nodejs
    go
    rustc
    cargo
    git
    ripgrep
    nur.repos.milahu.sqlite
  ];
  shellHook = "echo 'dev shell ready'";
}
