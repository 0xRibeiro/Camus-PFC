from datetime import date

from pydantic import BaseModel


# para saber quantos cadastros foram feitos no dia
class CadastroDiaRead(BaseModel):
    data: date
    quantidade: int


# para saber quanto cada conquista foi concedida
class ConquistaResumoRead(BaseModel):
    id: int
    titulo: str
    quantidade: int

# para fornecer o total de cadastros, conquistas, trilhas e grupos
class DashboardRead(BaseModel):
    total_usuarios: int
    total_grupos: int
    total_conquistas_concedidas: int
    total_trilhas: int

    cadastros_por_dia: list[CadastroDiaRead]
    conquistas_por_quantidade: list[ConquistaResumoRead]