<!-- MODELO PROJETO EM ANDAMENTO -->
<h1 align="center">
  🐟 Camus - Construido 🐟
</h1>

<!-- MODELO MENU DE NAVEGAÇÃO -->
<p align="center">
  <a href="#-sobre-o-projeto">Sobre</a> •
  <a href="#-funcionalidades">Funcionalidades</a> •
  <a href="#-layout">Layout</a> •
  <a href="#-como-executar-o-projeto">Como executar</a> •
  <a href="#-tecnologias">Tecnologias</a>
</p>

<!-- MODELO DESCRIÇÃO SOBRE O PROJETO: -->
## 🐟 Sobre o projeto

<!-- EXPLICA O MOTIVO DO PROJETO -->
O Camus é uma plataforma de apoio ao ensino de oceanografia, limnologia e biologia marinha. Estudantes podem seguir trilhas com artigos, vídeos e quizzes, participar de grupos de estudo e acompanhar seu progresso. A plataforma também oferece uma coleção de espécies integrada ao iNaturalist e permite cadastrar aquários e peixes. Ao vincular um dispositivo IoT a um aquário, é possível acompanhar leituras recentes de temperatura e distância em gráficos.

Link do deploy: [CAMUS](https://camus.gardiencor.app.br)

<!-- LINHA DE DIVISÃO: -->
---

<!-- ---------------------------------------------------------------------- -->

<!-- MODELO FUNCIONALIDADES: -->
## 🐡 Funcionalidades

<!-- EXEMPLO DE FUNCIONALIDADES: -->
- [x] Gerenciamento de trilhas globais e seus módulos por autores e administradores.
- [x] Editor de artigos com imagens e inclusão de informações sobre espécies do iNaturalist.
- [x] Reprodução de vídeos do YouTube nas trilhas.
- [x] Criação de quizzes de múltipla escolha com correção automática.
- [x] Acompanhamento do progresso, pontos de experiência (XP), conquistas e ranking global.
- [x] Grupos de estudo com entrada por convite, trilhas privadas e pontuação própria por grupo.
- [x] Coleção para pesquisar espécies e consultar seus detalhes pelo iNaturalist.
- [x] Cadastro de aquários e peixes, com opção de compartilhamento e vínculo com dispositivos IoT.
- [x] Visualização de leituras recentes de temperatura e distância nos aquários vinculados a sensores.
- [x] Minigames de identificação de peixes e comparação do número de observações entre espécies.
- [x] Painel administrativo com gerenciamento de usuários, indicadores de uso e registros de auditoria.
- [x] Interface responsiva com temas claro e escuro e aplicativo para Android.

---

<!-- ---------------------------------------------------------------------- -->

<!-- EXEMPLO DE LAYOUT: -->
## 🐧 Layout

### Telas do sistema

<!-- AQUI VOCÊ PASSA O CAMINHO DA IMAGEM -->
<img width="500" height="300" alt="tela de login" src="https://github.com/user-attachments/assets/2f376a08-d22b-4b6c-891a-12dbc504b9d2" />
<img width="500" height="300" alt="esqueci minha senha" src="https://github.com/user-attachments/assets/5614f327-9821-46fa-a7e6-43d1c875e680" />
<img width="500" height="300" alt="tela de minigames" src="https://github.com/user-attachments/assets/f4156024-21f7-4f96-8a73-e2ac52451dc3" />
<img width="500" height="300" alt="tela da API" src="https://github.com/user-attachments/assets/ab7cbae1-4c82-445a-bd1e-9a42ed67839b" />

<!-- ---------------------------------------------------------------------- -->

## 🦈 Como executar o projeto

### Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina:
[Git](https://git-scm.com) e [Nix + devenv](https://devenv.sh/getting-started/).
Além disto é bom ter um editor para trabalhar com o código como [VSCode](https://code.visualstudio.com/).

---

Esse projeto usa [devenv](https://devenv.sh) (Nix) pra gerenciar o ambiente de desenvolvimento inteiro: Python, Node/bun, Postgres, Redis, InfluxDB e Mosquitto (broker MQTT do IoT) sobem juntos, sem precisar instalar nada disso manualmente.

**1 - Instalar o Nix e o devenv**, seguindo o guia oficial: [devenv.sh/getting-started](https://devenv.sh/getting-started/)


**2 - Clonar o projeto e entrar na pasta**
```bash
git clone https://github.com/0xRibeiro/Camus-PFC.git
cd Camus-PFC
```

**3 - Entrar no ambiente** (a primeira vez demora, ele baixa tudo e instala as dependências do back e do front)
```bash
devenv shell
# ou, se você usa direnv:
direnv allow
```

**4 - Criar o `.env` do backend**
```bash
cp backend/.env.example backend/.env
```
Só precisa trocar o `JWT_SECRET` (gera com `openssl rand -hex 32`). A senha do Mosquitto e o token do Influx já vêm prontos.

**5 - Subir tudo** (Postgres, Redis, InfluxDB, Mosquitto, backend e frontend)
```bash
devenv up
```
Deixa esse terminal rodando. No primeiro start o backend vai reclamar do Influx, é normal, ainda falta configurar.

> As portas são fixas (8000, 3000, 1883...). Se alguma já estiver ocupada o `devenv up` dá erro em vez de trocar de porta, então fecha o que estiver usando ela.
>
> Se der erro com `you are not a trusted user`, quase sempre é isso: outro `devenv up` ficou rodando (ex: terminal fechado sem Ctrl+C) e tá segurando as portas. Mata esses processos com:
> ```bash
> pkill redis-server; pkill influxd; pkill mosquitto; pkill postgres; pkill -f uvicorn; pkill -f nuxt
> ```
> Se não tiver o `pkill`, abre o monitor de sistema da sua distro, procura por `redis`, `influxd`, `mosquitto`, `postgres`, `uvicorn` (back) e `nuxt` (front) e encerra eles por lá.

Os passos 6 e 7 são feitos **em outro terminal**, dentro da pasta do projeto e com o ambiente ativo (`devenv shell` de novo ou direnv).

**6 - Configurar o InfluxDB** (só na primeira vez)
```bash
influx setup --org camus --bucket leituras --username admin --password senha-influx --token camus-dev-token --force
```
> Se der `instance has already been set up`, é porque você já tinha rodado o projeto antes e ficaram dados antigos do Influx e do Mosquitto no `.devenv`. Para o `devenv up` (Ctrl+C), apaga eles:
> ```bash
> rm -rf .devenv/state/influxdb .devenv/state/influx-configs .devenv/state/mosquitto-dynsec.json*
> ```
> Sobe o `devenv up` de novo e roda o `influx setup` outra vez. Isso apaga as leituras e os dispositivos cadastrados só da sua máquina, o Postgres não é mexido.

**7 - Rodar as migrations**
```bash
cd backend
alembic upgrade head
```

**8 - Reiniciar o `devenv up`** (Ctrl+C no primeiro terminal e `devenv up` de novo) pra o backend conectar no Influx já configurado.

**9 - Acessar o projeto**
- Front-end: http://localhost:3000
- Back-end: http://localhost:8000/docs

### 📱 App Android

O app Android é o próprio front web empacotado com o [Capacitor](https://capacitorjs.com/). A cada atualização na `main` o GitHub Actions builda o APK e coloca ele na [release](https://github.com/0xRibeiro/Camus-PFC/releases) da versão atual do `web/package.json` (a mesma do footer). Pra instalar é só baixar o `camus-vX.Y.Z.apk` da release mais recente no celular.

Pra gerar o APK localmente (precisa do JDK 21 e do Android SDK):
```bash
cd web
NUXT_PUBLIC_API_BASE=https://api.camus.gardiencor.app.br bun run build:android
cd android && ./gradlew assembleDebug
```
> O APK sai em `web/android/app/build/outputs/apk/debug/`. Se der erro de `SDK location not found`, cria o `web/android/local.properties` com `sdk.dir=/caminho/do/Android/Sdk`.

<!-- ---------------------------------------------------------------------- -->


---


<!-- ---------------------------------------------------------------------- -->

## 🎣 Tecnologias

As seguintes ferramentas estao sendo usadas na construção do projeto:

#### **Ambiente de desenvolvimento**

- **[devenv](https://devenv.sh)** (Nix) — Python/UV, TS/bun, Postgres, Redis, InfluxDB e Mosquitto gerenciados juntos

#### **Back-End** ([FastAPI](https://fastapi.tiangolo.com/) / Python)

- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)

#### **Front-End Web** ([Nuxt](https://nuxt.com/) / Vue / TypeScript)

- [bun](https://bun.sh/)
- [Capacitor](https://capacitorjs.com/) (app Android)

#### **Firmware / IoT** (C++ / [Arduino](https://www.arduino.cc/))

- [Mosquitto](https://mosquitto.org/) (broker MQTT)

#### **Bancos de dados**

- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [InfluxDB](https://www.influxdata.com/)

---
<!-- ---------------------------------------------------------------------- -->


