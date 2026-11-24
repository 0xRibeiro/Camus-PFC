import random
from datetime import datetime, timedelta

from app.domains.pontuacao.model import LancamentoPontos, OrigemLancamento
from app.domains.progresso.model import ConclusaoConteudo, TentativaQuiz
from app.domains.trilha.model import ConteudoTipo
from scripts.seed.config import AGORA, INICIO
from scripts.seed.trilhas import percorrer_conteudos
from scripts.seed.util import depois, inserir, momento_entre


# salva tudo em lote no fim
class Progresso:
    def __init__(self):
        self.conclusoes = []
        self.tentativas = []
        self.lancamentos = []
        self.ultima_atividade = {}

    # acerta conforme a habilidade
    def responder_quiz(self, conteudo: dict, habilidade: float) -> tuple[dict, int]:
        respostas = {}
        acertos = 0
        for questao in conteudo["questoes"]:
            certa = None
            erradas = []
            for alternativa in questao["alternativas"]:
                if alternativa["correta"]:
                    certa = alternativa
                else:
                    erradas.append(alternativa)
            escolhida = random.choice(erradas)
            if certa is not None and random.random() < habilidade:
                escolhida = certa
                acertos += 1
            respostas[str(questao["linha"]["id"])] = escolhida["id"]
        return respostas, acertos

    # para se desistir ou chegar em hoje
    def fazer_trilha(
        self, aluno: dict, trilha: dict, comeco: datetime, habilidade: float
    ) -> None:
        grupo_id = (
            trilha["grupo"]["linha"]["id"] if trilha["grupo"] is not None else None
        )
        momento = comeco

        for conteudo in percorrer_conteudos([trilha]):
            linha = conteudo["linha"]
            if momento > AGORA:
                break

            versao = linha["versao"]
            pontos = linha["pontos"]
            if linha["tipo"] == ConteudoTipo.quiz:
                respostas, acertos = self.responder_quiz(conteudo, habilidade)
                total = len(conteudo["questoes"])
                self.tentativas.append(
                    {
                        "usuario_id": aluno["id"],
                        "conteudo_id": linha["id"],
                        "versao_conteudo": versao,
                        "respostas": respostas,
                        "acertos": acertos,
                        "total": total,
                        "criado_em": momento,
                    }
                )
                pontos = linha["pontos"] * acertos // total

            self.conclusoes.append(
                {
                    "usuario_id": aluno["id"],
                    "conteudo_id": linha["id"],
                    "versao_conteudo": versao,
                    "concluido_em": momento,
                }
            )
            if pontos > 0:
                self.lancamentos.append(
                    {
                        "usuario_id": aluno["id"],
                        "origem_tipo": OrigemLancamento.conteudo,
                        "origem_id": linha["id"],
                        "versao": versao,
                        "pontos": pontos,
                        "grupo_id": grupo_id,
                        "criado_em": momento,
                    }
                )
            if momento > self.ultima_atividade.get(aluno["id"], INICIO):
                self.ultima_atividade[aluno["id"]] = momento

            # desistencia pro funil
            if random.random() > 0.85:
                break
            if random.random() < 0.7:
                momento = depois(momento, timedelta(minutes=3), timedelta(minutes=40))
            else:
                momento = depois(momento, timedelta(days=1), timedelta(days=10))

    def simular(
        self,
        alunos: list[dict],
        trilhas_globais: list[dict],
        trilhas_de_grupo: list[dict],
    ) -> None:
        habilidade = {}
        for aluno in alunos:
            habilidade[aluno["id"]] = random.uniform(0.45, 0.95)

        for aluno in alunos:
            for trilha in random.sample(
                trilhas_globais, random.choice([0, 1, 1, 2, 2, 3, 4])
            ):
                comeco = momento_entre(
                    max(aluno["criado_em"], trilha["linha"]["criado_em"]),
                    AGORA,
                    curva=1.5,
                )
                self.fazer_trilha(aluno, trilha, comeco, habilidade[aluno["id"]])

        for trilha in trilhas_de_grupo:
            for aluno, entrou in trilha["grupo"]["membros"]:
                if random.random() < 0.75:
                    comeco = momento_entre(
                        max(entrou, trilha["linha"]["criado_em"]), AGORA, curva=2
                    )
                    self.fazer_trilha(aluno, trilha, comeco, habilidade[aluno["id"]])

    async def salvar(self, db) -> None:
        await inserir(db, ConclusaoConteudo, self.conclusoes)
        await inserir(db, TentativaQuiz, self.tentativas)
        await inserir(db, LancamentoPontos, self.lancamentos)
