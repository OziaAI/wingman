{pkgs ? import <nixpkgs>{}}:
pkgs.mkShell {
    name = "env";
    nativeBuildInputs = with pkgs; [
        python3
        python3Packages.virtualenv
        pkgs.poetry
        pkgs.python3Packages.django
        pkgs.black
        stdenv.cc
        gnupg libGL libGLU zlib
    ];
    shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
        pkgs.stdenv.cc.cc
        pkgs.libGLU
        pkgs.libGL
        pkgs.zlib
        pkgs.glib
    ]};
    '';
}
