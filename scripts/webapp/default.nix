with import <nixpkgs> {}; {
  env = stdenv.mkDerivation {
    name = "flipdot-webapp-env";
    buildInputs = [
      python3
      python3Packages.flask
      python3Packages.numpy
      python3Packages.pillow
    ];
  };
}
