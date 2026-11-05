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
