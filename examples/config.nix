{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    nodejs
    go
    git
    ripgrep
  ];
  shellHook = "echo 'dev shell ready'";
}
