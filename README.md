

<!-- MODELO PROJETO EM ANDAMENTO -->
<h1 align="center"> 
	🐟 Camus - Em contrução 🐟
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
Camus é um projeto que auxilia no ensino de Oceanografia/Limnologia com foco em ambientes acadêmicos. Ele possui um sistema de trilhas de conteúdo para dividir os temas, cria grupos de estudo para maior coordenação entre os alunos e utiliza de IoT para disponibilizar dashboards de dados de microcosmos em tempo real


<!-- LINHA DE DIVISÃO: -->
---

<!-- ---------------------------------------------------------------------- -->

<!-- MODELO FUNCIONALIDADES: -->
## 🐡 Funcionalidades

<!-- EXEMPLO DE FUNCIONALIDADES: -->
- [x] Usuarios staff podem gerenciar conteudos de ensino no app atraves de trilhas e modulos
- [x] Usuarios alunos podem ganhar conquistas e visualiizar elas em seus perfis podendo acumular e obter conquistas atraves de acoes
- [ ] Editor de texto estilo notion para conteudos de artigo
- [ ] visualizador de video integrado para consumo de videos do youtube
- [ ] gerador de quiz para diferentes tipos de questionarios
- [ ] sistema de pontuacao e ranking entre usuarios

---

<!-- ---------------------------------------------------------------------- -->

<!-- EXEMPLO DE LAYOUT: -->
## 🐧 Layout

### telas de gerenciamento de conteudo

<!-- AQUI VOCÊ PASSA O CAMINHO DA IMAGEM -->
<img width="400" alt="image" src="https://github.com/user-attachments/assets/cc6630cf-ca22-485d-bcea-9e237335da9d" />
<img width="400" alt="image" src="https://github.com/user-attachments/assets/b77b5f9b-9c9e-45e2-b3e9-7a9aa24066fc" />

### tela de conquistas do usuario
<img width="400"  alt="image" src="https://github.com/user-attachments/assets/5ae06523-abbe-4885-bbbe-6c1b36b83536" />



---

<!-- ---------------------------------------------------------------------- -->

## 🦈 Como executar o projeto

### Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina:
[Git](https://git-scm.com) e [Nix + devenv](https://devenv.sh/getting-started/).
Além disto é bom ter um editor para trabalhar com o código como [VSCode](https://code.visualstudio.com/).

---

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
**4 - Configurar o backend**
```bash
cp backend/.env.example backend/.env
# depois, preencha os valores em backend/.env
```

**5 - Subir tudo** (Postgres, Redis, InfluxDB, backend e frontend)
```bash
devenv up
```

**6 - Rodar Migrations
```bash
cd backend
alembic upgrade head
```

**7 - Acessar o projeto**
- Front-end: http://localhost:3000
- Back-end: http://localhost:8000/docs
  
  ou outras portas caso vc ja tiver com essas ocupadas (o devenv up gerencia automaticamente e é exibido no terminal)

<!-- ---------------------------------------------------------------------- -->


---


<!-- ---------------------------------------------------------------------- -->

## 🎣 Tecnologias

As seguintes ferramentas estao sendo usadas na construção do projeto:

#### **Ambiente de desenvolvimento**

- **[devenv](https://devenv.sh)** (Nix) — Python/UV, TS/bun, Postgres, Redis e InfluxDB gerenciados juntos

#### **Back-End** ([FastAPI](https://fastapi.tiangolo.com/) / Python)

- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)

#### **Front-End Web** ([Nuxt](https://nuxt.com/) / Vue / TypeScript)

- [bun](https://bun.sh/)

#### **Firmware / IoT** (C++ / [Arduino](https://www.arduino.cc/))

#### **Bancos de dados**

- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [InfluxDB](https://www.influxdata.com/)

---
<!-- ---------------------------------------------------------------------- -->


