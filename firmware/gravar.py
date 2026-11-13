# /// script
# requires-python = ">=3.12"
# dependencies = ["pyserial"]
# ///

# grava esp e modulos
#   uv run firmware/gravar.py esp --porta /dev/ttyUSB1
#   uv run firmware/gravar.py distancia --porta /dev/ttyUSB0

import argparse
import getpass
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import serial

PASTA = Path(__file__).parent
PASTA_ESP = PASTA / "esp32-central"

MODULOS = {
    "distancia": PASTA / "modulo-distancia",
}


def rodar(comando: list[str], pasta: Path) -> str:
    resultado = subprocess.run(comando, cwd=pasta, capture_output=True, text=True)
    if resultado.returncode != 0:
        print(resultado.stdout[-2000:])
        print(resultado.stderr[-2000:])
        sys.exit(f"falhou: {' '.join(comando)}")
    return resultado.stdout


def ler_mac(porta: str) -> str:
    saida = rodar(["pio", "pkg", "exec", "-p", "tool-esptoolpy", "--", "esptool.py", "--port", porta, "read_mac"], PASTA_ESP)

    for linha in saida.splitlines():
        if linha.startswith("MAC:"):
            return linha.split()[1].replace(":", "").lower()

    sys.exit("nao achei o mac na saida do esptool")


def chamar_api(url: str, corpo: dict, token: str | None = None) -> dict:
    cabecalhos = {"Content-Type": "application/json"}
    if token is not None:
        cabecalhos["Authorization"] = f"Bearer {token}"

    pedido = urllib.request.Request(url, data=json.dumps(corpo).encode(), headers=cabecalhos, method="POST")

    try:
        with urllib.request.urlopen(pedido) as resposta:
            return json.loads(resposta.read())
    except urllib.error.HTTPError as erro:
        sys.exit(f"api respondeu {erro.code}: {erro.read().decode()}")


def entrar(api: str) -> str:
    email = input("email do admin: ")
    senha = getpass.getpass("senha do admin: ")
    return chamar_api(f"{api}/auth/login", {"email": email, "password": senha})["access_token"]


def gravar_firmware(pasta: Path, porta: str, ambiente: str | None) -> None:
    comando = ["pio", "run", "-t", "upload", "--upload-port", porta]
    if ambiente is not None:
        comando += ["-e", ambiente]
    rodar(comando, pasta)


# espera o "mac: x" do boot e manda a senha
def enviar_senha(porta: str, mac: str, senha: str) -> None:
    with serial.Serial(porta, 115200, timeout=1) as conexao:
        limite = time.time() + 30

        while time.time() < limite:
            linha = conexao.readline().decode(errors="ignore").strip()

            if linha.startswith("mac:") and linha.split()[1] != mac:
                sys.exit(f"mac da serial ({linha}) diferente do lido ({mac})")

            if linha.startswith("mac:"):
                conexao.write(f"senha:{senha}\n".encode())

            if linha == "ok":
                return

    sys.exit("esp nao confirmou a senha")


def gravar_esp(porta: str, api: str, ambiente: str | None) -> None:
    mac = ler_mac(porta)
    print(f"mac: {mac}")

    token = entrar(api)
    credencial = chamar_api(f"{api}/admin/dispositivos", {"mac": mac}, token)
    print("cadastrado no broker")

    gravar_firmware(PASTA_ESP, porta, ambiente)
    print("firmware gravado")

    enviar_senha(porta, mac, credencial["senha"])
    print("senha salva no esp, finalizando")


def main() -> None:
    parser = argparse.ArgumentParser(description="grava o esp central ou um modulo")
    parser.add_argument("alvo", choices=["esp", *MODULOS])
    parser.add_argument("--porta", required=True)
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--ambiente", help="env do platformio.ini do esp")
    argumentos = parser.parse_args()

    if argumentos.alvo == "esp":
        gravar_esp(argumentos.porta, argumentos.api.rstrip("/"), argumentos.ambiente)
        return

    # modulo gera o serial sozinho, so grava
    gravar_firmware(MODULOS[argumentos.alvo], argumentos.porta, None)
    print("modulo gravado")


main()