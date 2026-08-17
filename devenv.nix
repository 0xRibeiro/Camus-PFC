{ pkgs, lib, config, inputs, ... }:

{

  languages.javascript = {
    enable = true;
    directory = "web";
    bun.enable = true;
  };

  languages.typescript.enable = true;

  languages.python = {
    enable = true;
    venv.enable = true;
    directory = "backend";
    uv = {
      enable = true;
      sync.enable = true;
    };
  };


  # https://devenv.sh/services/
  services.postgres = {
    enable = true;
    listen_addresses = "localhost";
    initialDatabases = [
      { name = "camusdb"; }
     ];
  };

  services.redis.enable = true;

  services.influxdb.enable = true;


  # https://devenv.sh/basics/
  enterShell = ''

     echo -e "\n\n\n\n  devenv carregado  \n\n\n\n"

  '';

}
