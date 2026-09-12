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
    initialDatabases = [
      { name = "camusdb"; }
     ];
  };

  services.redis.enable = true;

  services.influxdb.enable = true;


  processes.backend = {
    ports.http.allocate = 8000;
    after = [ "devenv:processes:postgres" "devenv:processes:redis" ];
    exec = ''
      cd "$DEVENV_ROOT/backend"
      echo "${toString config.processes.backend.ports.http.value}" > "$DEVENV_ROOT/.devenv/backend-port"
      export CORS_ORIGINS='["http://localhost:${toString config.processes.frontend.ports.http.value}"]'
      exec uvicorn app.main:app --reload --port ${toString config.processes.backend.ports.http.value}
    '';
  };

  processes.frontend = {
    ports.http.allocate = 3000;
    exec = ''
      cd "$DEVENV_ROOT/web"
      export NUXT_PUBLIC_API_BASE="http://localhost:${toString config.processes.backend.ports.http.value}"
      exec bun run dev -- --port ${toString config.processes.frontend.ports.http.value}
    '';
  };


  # https://devenv.sh/basics/
  enterShell = ''

     if [ -f "$DEVENV_ROOT/.devenv/backend-port" ]; then
       export API_BASE="http://localhost:$(cat "$DEVENV_ROOT/.devenv/backend-port")"
     fi
     echo -e "\n\n\n\n  devenv carregado  \n\n\n\n"

  '';

}
