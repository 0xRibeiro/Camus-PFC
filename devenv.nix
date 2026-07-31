{ pkgs, lib, config, inputs, ... }:

{

  languages.python = {
    enable = true;
    venv.enable = true;
    directory = "backend";
    uv = {
      enable = true;
      sync.enable = true;
    };
  };


  # https://devenv.sh/packages/
  packages = with pkgs; [

    ];


  # https://devenv.sh/services/
  services.postgres = {
    enable = true;
    listen_addresses = "localhost";
    initialDatabases = [
      { name = "camusdb"; }
     ];
  };

  scripts.pgup.exec = ''
  port=$(awk '/^port/ {print $3}' "$PGDATA/postgresql.conf")
  echo "export PGPORT=$port"
  '';


  # https://devenv.sh/basics/
  enterShell = ''

     echo -e "\n\n\n\n  devenv carregado  \n\n\n\n"

  '';

}
