from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.core.security import criar_hash
from app.domains.usuario.model import Usuario
from app.domains.usuario.schema import UsuarioCreate, UsuarioLogin

SENHA_PADRAO: str = "senha12345"


# gera um Usuario (model) com dados falsos validos sem precisar de banco
# todo user sai com a senha padrao pros testes saberem a senha certa
class UsuarioFactory(SQLAlchemyFactory[Usuario]):
    # o polyfactory precisa usa o faker pra regra combinada (email + minimo)
    email = Use(SQLAlchemyFactory.__faker__.email)
    hashed_password = criar_hash(SENHA_PADRAO)


# gera o payload do cadastro (schema) ja passando nas validacoes do schema
# aceitou_termos valor padrao em True pq o schema recusa False e o teste quebraria antes de ir no service
class UsuarioCreateFactory(ModelFactory[UsuarioCreate]):
    email = Use(ModelFactory.__faker__.email)
    password = SENHA_PADRAO
    aceitou_termos = True

# msm coisa mas pro schema de login
class UsuarioLoginFactory(ModelFactory[UsuarioLogin]):
    password = SENHA_PADRAO
