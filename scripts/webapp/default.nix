with import <nixpkgs> {}; {
  env = stdenv.mkDerivation {
    name = "flipdot-webapp-env";
    buildInputs = [
      python2
      python2Packages.flask
      python2Packages.pillow
    ];
  };
}
