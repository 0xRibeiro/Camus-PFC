

<!-- MODELO PROJETO EM ANDAMENTO -->
<h1 align="center"> 
	🚧 Camus - Em contrução 🚧
</h1>


<!-- MODELO MENU DE NAVEGAÇÃO -->
<p align="center">
 <a href="#-sobre-o-projeto">Sobre</a> •
 <a href="#-funcionalidades">Funcionalidades</a> •
 <a href="#-layout">Layout</a> • 
 <a href="#-como-executar-o-projeto">Como executar</a> • 
 <a href="#-tecnologias">Tecnologias</a> • 
 <a href="#-autor">Autor</a> • 
 <a href="#user-content--licença">Licença</a>
</p>



<!-- MODELO DESCRIÇÃO SOBRE O PROJETO: -->
## 💻 Sobre o projeto

<!-- EXPLICA O MOTIVO DO PROJETO -->
Camus é um projeto criado para a conclusão da nossa graduação em Engenharia de Software. ele é um projeto que integra IoT e desnevolvimento de software para construção de um SUMP inteligente com um app mobile para aprendizado e ensino sobre oceanografia limnologia e controle do sump em seus aquarios e microcosmos de estudo.


<!-- LINHA DE DIVISÃO: -->
---

<!-- ---------------------------------------------------------------------- -->

<!-- MODELO FUNCIONALIDADES: -->
## ⚙️ Funcionalidades

<!-- EXEMPLO DE FUNCIONALIDADES: -->
- [x] Se o usuário não enviar mensagens dentro de 1 minuto o chat deve responder uma mensagem automaticamente.
- [x]

---

<!-- ---------------------------------------------------------------------- -->

<!-- EXEMPLO DE LAYOUT: -->
## 🎨 Layout

### Widget

<!-- AQUI VOCÊ PASSA O CAMINHO DA IMAGEM -->
![Mobile1]()<br>
![Mobile2]()<br>
![Mobile3]()

---

<!-- ---------------------------------------------------------------------- -->

## 🚀 Como executar o projeto

Esse projeto usa [devenv](https://devenv.sh) (Nix) pra gerenciar o ambiente de desenvolvimento inteiro: Python, Node/bun, Postgres, Redis e InfluxDB sobem juntos, sem precisar instalar nada disso manualmente.

**1 - Instalar o Nix e o devenv**, seguindo o guia oficial: [devenv.sh/getting-started](https://devenv.sh/getting-started/)

**2 - Clonar o projeto e entrar na pasta**
```bash
git clone https://github.com/0xRibeiro/Camus-PFC.git
cd Camus-PFC
```

**3 - Entrar no ambiente**
```bash
devenv shell
# ou, se você usa direnv:
direnv allow
```

**4 - Subir os serviços** (Postgres, Redis, InfluxDB)
```bash
devenv up
```

**5 - Configurar o backend**
```bash
cp backend/.env.example backend/.env
# depois, preencha os valores em backend/.env
```

**6 - Rodar o backend**
```bash
cd backend
uvicorn app.main:app --reload
```

**7 - Rodar o web (Nuxt)**
```bash
cd web
bun run dev
```

<!-- ---------------------------------------------------------------------- -->

### Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina:
[Git](https://git-scm.com) e [Nix + devenv](https://devenv.sh/getting-started/).
Além disto é bom ter um editor para trabalhar com o código como [VSCode](https://code.visualstudio.com/).

---

<!-- ---------------------------------------------------------------------- -->

## 🛠 Tecnologias

As seguintes ferramentas estao sendo usadas na construção do projeto:

#### **Ambiente de desenvolvimento**

- **[devenv](https://devenv.sh)** (Nix) — Python, JS/bun, Postgres, Redis e InfluxDB gerenciados juntos

#### **Back-End** ([FastAPI](https://fastapi.tiangolo.com/) / Python)

- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)

#### **Front-End Web** ([Nuxt](https://nuxt.com/) / Vue / TypeScript)

- [bun](https://bun.sh/)

#### **Mobile** ([Flutter](https://flutter.dev/) / Dart)

#### **Firmware / IoT** (C++ / [Arduino](https://www.arduino.cc/))

#### **Bancos de dados**

- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [InfluxDB](https://www.influxdata.com/)

---

<!-- ---------------------------------------------------------------------- -->


<!-- MODELO DE AUTOR-->
## 🦸 Autor

---

<!-- ---------------------------------------------------------------------- -->

<!-- MODELO DE LICENÇA -->
## 📝 Licença

