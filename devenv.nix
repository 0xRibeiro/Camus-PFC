{ pkgs, lib, config, inputs, ... }:

{

  languages.javascript = {
    enable = true;
    directory = "web";
    bun = {
      enable = true;
      install.enable = true;
    };
  };

  languages.typescript.enable = true;

  packages = [
    pkgs.platformio
    pkgs.clang-tools
  ];

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

  services.redis = {
    enable = true;
    port = 6379;
  };

  services.influxdb.enable = true;

  # config do cli do influx fica no projeto, n bate com o ~/.influxdbv2 de outros projetos
  env.INFLUX_CONFIGS_PATH = "${config.env.DEVENV_STATE}/influx-configs";

  # leituras ficam 30 dias, igual producao. espera o influx setup se ainda n rodou
  processes.influxdb-retencao = {
    after = [ "devenv:processes:influxdb-server" ];
    exec = ''
      # msm token q o backend usa
      token=$(grep '^INFLUX_TOKEN=' "$DEVENV_ROOT/backend/.env" | cut -d= -f2-)

      until id=$(influx bucket list --org camus --token "$token" --name leituras --hide-headers 2>/dev/null | cut -f1) && [ -n "$id" ]; do
        sleep 5
      done
      influx bucket update --id "$id" --retention 30d --shard-group-duration 1d --token "$token"
    '';
  };

  # broker do iot, aberto na rede pro esp
  # senha fixa do admin, o plugin so usa no 1o start (quando o json ainda n existe)
  env.MOSQUITTO_DYNSEC_PASSWORD = "camus-dev";

  services.mosquitto = {
    enable = true;
    bind = null;
    port = 1883;
    extraConfig = ''
      allow_anonymous false
      plugin ${pkgs.mosquitto.lib}/lib/mosquitto_dynamic_security.so
      plugin_opt_config_file ${config.devenv.root}/.devenv/state/mosquitto-dynsec.json
    '';
  };


  processes.backend = {
    ports.http.allocate = 8000;
    after = [ "devenv:processes:postgres" "devenv:processes:redis" "devenv:processes:mosquitto" ];
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
