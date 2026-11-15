from fastapi import Body, Depends
from fastcrud import CreateConfig, FilterConfig, crud_router
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.trilha.model import (
    Alternativa,
    Conteudo,
    Modulo,
    Questao,
    Trilha,
)
from app.domains.trilha.repository import exigir_item_no_escopo, filtro_escopo
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
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.service import exige_role, get_current_user

exige_staff = exige_role(RoleUsuario.author, RoleUsuario.admin)


# pega o id se tiver, se não devolve None. com isso vira global
def escopo_trilha(db: AsyncSession = Depends(get_async_session)) -> int | None:
    return db.info.get("grupo_id")


# verifica se o grupo for none se o usuario é staff
async def gerenciar_trilhas(grupo_id: int | None = Depends(escopo_trilha), usuario: Usuario = Depends(get_current_user)) -> None:
    # No prefixo de grupo, o router já passou pela verificação de dono.
    if grupo_id is None:
        await exige_staff(usuario)


# FASTCRUD ignora os None, então esse metodo devolve global se for None que depois é convertido pra null.
def escopo_listagem(grupo_id: int | None = Depends(escopo_trilha)) -> int | str:
    return grupo_id if grupo_id is not None else "global"


# validação de item no escopo do grupo
def validar_item(modelo):
    async def validar(id: int, db: AsyncSession = Depends(get_async_session), grupo_id: int | None = Depends(escopo_trilha)) -> None:
        await exigir_item_no_escopo(db, modelo, id, grupo_id)

    return validar


# valida o item "pai", que seria o item que está um nivel acima do outro (conteudo -> modulo -> trilha etc)
def validar_pai(campo, pai, schema):
    async def validar(item: schema = Body(...), db: AsyncSession = Depends(get_async_session), grupo_id: int | None = Depends(escopo_trilha)) -> None:
        await exigir_item_no_escopo(
            db, pai, getattr(item, campo), grupo_id, apenas_quiz=pai is Conteudo
        )

    return validar


######## o crud_router() gera 5 endpoints automaticamente de CRUD padrao ja com opcoes de paginacao e sort, alem de podermos adicionarmos filtros personalizados com filterconfig

filtros_personalizados = {"escopo": filtro_escopo}

trilha_router = crud_router(
    session=get_async_session,  # session injetada pra acessar DB
    model=Trilha,  # a entidade/tabela
    create_schema=TrilhaCreate,  # schema de criacao
    update_schema=TrilhaUpdate,  # schema de update
    select_schema=TrilhaRead,  # schema de resposta
    filter_config=FilterConfig(id__escopo=escopo_listagem),
    custom_filters=filtros_personalizados,
    create_config=CreateConfig(
        auto_fields={"grupo_id": escopo_trilha},
        exclude_from_schema=[],
    ),
    path="/trilhas",  # url dos endpoints gerados
    tags=["trilhas"],  # tag do swagger
    read_deps=[validar_item(Trilha)],
    # no global, escrita so pra author/admin; leitura fica publica
    create_deps=[gerenciar_trilhas],
    update_deps=[gerenciar_trilhas, validar_item(Trilha)],
    delete_deps=[gerenciar_trilhas, validar_item(Trilha)],
)

modulo_router = crud_router(
    session=get_async_session,
    model=Modulo,
    create_schema=ModuloCreate,
    update_schema=ModuloUpdate,
    select_schema=ModuloRead,
    # opcao de filtro na querie url
    filter_config=FilterConfig(trilha_id=None, id__escopo=escopo_listagem),
    custom_filters=filtros_personalizados,
    path="/modulos",
    tags=["modulos"],
    read_deps=[validar_item(Modulo)],
    create_deps=[gerenciar_trilhas, validar_pai("trilha_id", Trilha, ModuloCreate)],
    update_deps=[gerenciar_trilhas, validar_item(Modulo)],
    delete_deps=[gerenciar_trilhas, validar_item(Modulo)],
)

conteudo_router = crud_router(
    session=get_async_session,
    model=Conteudo,
    create_schema=ConteudoCreate,
    update_schema=ConteudoUpdate,
    select_schema=ConteudoRead,
    # cada um com a opcao de filtro q agrupa
    filter_config=FilterConfig(modulo_id=None, id__escopo=escopo_listagem),
    custom_filters=filtros_personalizados,
    path="/conteudos",
    tags=["conteudos"],
    read_deps=[gerenciar_trilhas, validar_item(Conteudo)],
    read_multi_deps=[gerenciar_trilhas],
    create_deps=[gerenciar_trilhas, validar_pai("modulo_id", Modulo, ConteudoCreate)],
    update_deps=[gerenciar_trilhas, validar_item(Conteudo)],
    delete_deps=[gerenciar_trilhas, validar_item(Conteudo)],
)

questao_router = crud_router(
    session=get_async_session,
    model=Questao,
    create_schema=QuestaoCreate,
    update_schema=QuestaoUpdate,
    select_schema=QuestaoRead,
    filter_config=FilterConfig(conteudo_id=None, id__escopo=escopo_listagem),
    custom_filters=filtros_personalizados,
    path="/questoes",
    tags=["questoes"],
    read_deps=[gerenciar_trilhas, validar_item(Questao)],
    read_multi_deps=[gerenciar_trilhas],
    create_deps=[
        gerenciar_trilhas,
        validar_pai("conteudo_id", Conteudo, QuestaoCreate),
    ],
    update_deps=[gerenciar_trilhas, validar_item(Questao)],
    delete_deps=[gerenciar_trilhas, validar_item(Questao)],
)

alternativa_router = crud_router(
    session=get_async_session,
    model=Alternativa,
    create_schema=AlternativaCreate,
    update_schema=AlternativaUpdate,
    select_schema=AlternativaRead,
    filter_config=FilterConfig(questao_id=None, id__escopo=escopo_listagem),
    custom_filters=filtros_personalizados,
    path="/alternativas",
    tags=["alternativas"],
    read_deps=[gerenciar_trilhas, validar_item(Alternativa)],
    read_multi_deps=[gerenciar_trilhas],
    create_deps=[
        gerenciar_trilhas,
        validar_pai("questao_id", Questao, AlternativaCreate),
    ],
    update_deps=[gerenciar_trilhas, validar_item(Alternativa)],
    delete_deps=[gerenciar_trilhas, validar_item(Alternativa)],
)