{
    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    };

    outputs = { self, nixpkgs }:
        let
        pkgs = nixpkgs.legacyPackages.x86_64-linux;
        in {
            devShells.x86_64-linux.default = pkgs.mkShell {
                buildInputs = with pkgs; [
                    python3
                    python3Packages.pip
                    ripgrep
                    git
                    nix
                ];
            };
    };
}