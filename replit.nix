{ pkgs }: {
  deps = [
    pkgs.nodejs-20
    pkgs.nodePackages.typescript
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.sqlite
    pkgs.ffmpeg-full
  ];
}
