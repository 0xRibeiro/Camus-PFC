from fastcrud import FilterConfig, crud_router

from app.core.database import get_async_session
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha
from app.domains.trilha.schema import (
    AlternativaCreate,
    AlternativaRead,
    AlternativaUpdate,
    ConteudoCreate,
    ConteudoRead,
    ConteudoUpdate,
    ModuloCreate,
    ModuloRead,
    ModuloUpdate,
    QuestaoCreate,
    QuestaoRead,
    QuestaoUpdate,
    TrilhaCreate,
    TrilhaRead,
    TrilhaUpdate,
)
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

######## o crud_router() gera 5 endpoints automaticamente de CRUD padrao ja com opcoes de paginacao e sort, alem de podermos adicionarmos filtros personalizados com filterconfig

apenas_staff = [exige_role(RoleUsuario.author, RoleUsuario.admin)]

trilha_router = crud_router(
    session=get_async_session, # session injetada pra acessar DB
    model=Trilha, # a entidade/tabela
    create_schema=TrilhaCreate, # schema de criacao
    update_schema=TrilhaUpdate, # schema de update
    select_schema=TrilhaRead, #schema de resposta
    path="/trilhas", # url dos endpoints gerados
    tags=["trilhas"], # tag do swagger
    create_deps=apenas_staff, # escrita so pra author/admin; leitura fica publica
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

modulo_router = crud_router(
    session=get_async_session,
    model=Modulo,
    create_schema=ModuloCreate,
    update_schema=ModuloUpdate,
    select_schema=ModuloRead,
    filter_config=FilterConfig(trilha_id=None), # opcao de filtro na querie url
    path="/modulos",
    tags=["modulos"],
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

conteudo_router = crud_router(
    session=get_async_session,
    model=Conteudo,
    create_schema=ConteudoCreate,
    update_schema=ConteudoUpdate,
    select_schema=ConteudoRead,
    filter_config=FilterConfig(modulo_id=None), # cada um com a opcao de filtro q agrupa
    path="/conteudos",
    tags=["conteudos"],
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

questao_router = crud_router(
    session=get_async_session,
    model=Questao,
    create_schema=QuestaoCreate,
    update_schema=QuestaoUpdate,
    select_schema=QuestaoRead,
    filter_config=FilterConfig(conteudo_id=None),
    path="/questoes",
    tags=["questoes"],
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

alternativa_router = crud_router(
    session=get_async_session,
    model=Alternativa,
    create_schema=AlternativaCreate,
    update_schema=AlternativaUpdate,
    select_schema=AlternativaRead,
    filter_config=FilterConfig(questao_id=None),
    path="/alternativas",
    tags=["alternativas"],
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)
