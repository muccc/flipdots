with import <nixpkgs> {}; {
  env = stdenv.mkDerivation {
    name = "flipdots-env";
    buildInputs = [
      python3
      python3Packages.numpy
      python3Packages.gevent
      python3Packages.flask
    ];
  };
}
