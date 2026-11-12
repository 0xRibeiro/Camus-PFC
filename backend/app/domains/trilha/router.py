from fastapi import Depends
from fastcrud import CreateConfig, FilterConfig, crud_router

from app.core.database import get_async_session
from app.domains.grupo.service import grupo_dono
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha
from app.domains.trilha.repository import CAMPOS, TrilhaCRUD
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
    session=get_async_session,  # session injetada pra acessar DB
    model=Trilha,  # a entidade/tabela
    crud=TrilhaCRUD(Trilha),
    create_schema=TrilhaCreate,  # schema de criacao
    update_schema=TrilhaUpdate,  # schema de update
    select_schema=TrilhaRead,  # schema de resposta
    path="/trilhas",  # url dos endpoints gerados
    tags=["trilhas"],  # tag do swagger
    create_deps=apenas_staff,  # escrita so pra author/admin; leitura fica publica
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

modulo_router = crud_router(
    session=get_async_session,
    model=Modulo,
    crud=TrilhaCRUD(Modulo),
    create_schema=ModuloCreate,
    update_schema=ModuloUpdate,
    select_schema=ModuloRead,
    filter_config=FilterConfig(trilha_id=None),  # opcao de filtro na querie url
    path="/modulos",
    tags=["modulos"],
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

conteudo_router = crud_router(
    session=get_async_session,
    model=Conteudo,
    crud=TrilhaCRUD(Conteudo),
    create_schema=ConteudoCreate,
    update_schema=ConteudoUpdate,
    select_schema=ConteudoRead,
    filter_config=FilterConfig(modulo_id=None),  # cada um com a opcao de filtro q agrupa
    path="/conteudos",
    tags=["conteudos"],
    read_deps=apenas_staff,
    read_multi_deps=apenas_staff,
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

questao_router = crud_router(
    session=get_async_session,
    model=Questao,
    crud=TrilhaCRUD(Questao),
    create_schema=QuestaoCreate,
    update_schema=QuestaoUpdate,
    select_schema=QuestaoRead,
    filter_config=FilterConfig(conteudo_id=None),
    path="/questoes",
    tags=["questoes"],
    read_deps=apenas_staff,
    read_multi_deps=apenas_staff,
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)

alternativa_router = crud_router(
    session=get_async_session,
    model=Alternativa,
    crud=TrilhaCRUD(Alternativa),
    create_schema=AlternativaCreate,
    update_schema=AlternativaUpdate,
    select_schema=AlternativaRead,
    filter_config=FilterConfig(questao_id=None),
    path="/alternativas",
    tags=["alternativas"],
    read_deps=apenas_staff,
    read_multi_deps=apenas_staff,
    create_deps=apenas_staff,
    update_deps=apenas_staff,
    delete_deps=apenas_staff,
)


# Reaproveita os schemas e filtros nos endpoints privados do grupo.
for modelo, path, criar, editar, ler in (
    (Trilha, "/trilhas", TrilhaCreate, TrilhaUpdate, TrilhaRead),
    (Modulo, "/modulos", ModuloCreate, ModuloUpdate, ModuloRead),
    (Conteudo, "/conteudos", ConteudoCreate, ConteudoUpdate, ConteudoRead),
    (Questao, "/questoes", QuestaoCreate, QuestaoUpdate, QuestaoRead),
    (Alternativa, "/alternativas", AlternativaCreate, AlternativaUpdate, AlternativaRead),
):
    router_grupo = crud_router(
        session=get_async_session,
        model=modelo,
        crud=TrilhaCRUD(modelo, privado=True),
        create_schema=criar,
        update_schema=editar,
        select_schema=ler,
        path=path,
        tags=["trilhas de grupo"],
        filter_config=FilterConfig(**{CAMPOS[modelo][0]: None}) if modelo in CAMPOS else None,
        create_config=(CreateConfig(auto_fields={"grupo_id": grupo_dono}, exclude_from_schema=[])if modelo is Trilha else None),
        deleted_methods=["db_delete"],
    )
    trilha_router.include_router(
        router_grupo,
        prefix="/grupos/{grupo_id}",
        dependencies=[Depends(grupo_dono)],
    )
