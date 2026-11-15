import json
import random

import httpx

from app.core.redis import redis_client

INAT_URL = "https://api.inaturalist.org/v1"
BRASIL = 6878
CACHE_SEGUNDOS = 60 * 60 * 24
# muda o nome qnd mudar os campos da especie, se n le o cache velho
CHAVE_ESPECIES = "minigame:especies:v2"

# msm grupos da colecao no front (web/app/utils/inaturalista.ts)
GRUPOS_COLECAO = [
    47178, 47273, 60450, 85511, 49099, 47115, 85493, 47534, 47549, 48824, 51508, 47490, 68104,
    130868, 122158, 152871, 372843, 46306, 372234, 67564, 67565, 129726, 48051, 68235, 51280,
]

# so licenca q deixa reusar a foto dando credito
LICENCAS_LIVRES = "cc0,cc-by,cc-by-nc,cc-by-sa,cc-by-nc-sa,cc-by-nd,cc-by-nc-nd"


async def buscar(caminho: str, params: dict) -> dict:
    async with httpx.AsyncClient(base_url=INAT_URL, timeout=10) as client:
        resposta = await client.get(caminho, params=params)
        resposta.raise_for_status()
        return resposta.json()


def achar_grupo(ancestor_ids: list[int]) -> int | None:
    for ancestral in ancestor_ids:
        if ancestral in GRUPOS_COLECAO:
            return ancestral
    return None


# especies mais vistas no brasil q tem nome popular em pt, o iNat limita req entao fica 1 dia no redis
async def listar_especies() -> list[dict]:
    em_cache = await redis_client.get(CHAVE_ESPECIES)
    if em_cache:
        return json.loads(em_cache)

    especies = []
    for pagina in (1, 2):
        dados = await buscar("/observations/species_counts", {
            "taxon_id": ",".join(map(str, GRUPOS_COLECAO)),
            "place_id": BRASIL,
            "quality_grade": "research",
            "locale": "pt-BR",
            "per_page": 500,
            "page": pagina,
        })
        for item in dados["results"]:
            taxon = item["taxon"]
            nome = taxon.get("preferred_common_name")
            # sem nome em pt o iNat n manda nada
            if not nome:
                continue
            especies.append({
                "taxon_id": taxon["id"],
                "nome": nome[0].upper() + nome[1:],
                "nome_cientifico": taxon["name"],
                "grupo": achar_grupo(taxon["ancestor_ids"]),
                # total no mundo, o count do species_counts é so do brasil
                "registros": taxon["observations_count"],
            })

    await redis_client.set(CHAVE_ESPECIES, json.dumps(especies), ex=CACHE_SEGUNDOS)
    return especies


# guarda um lote de fotos da especie e sorteia uma, assim n chama o iNat toda rodada
async def sortear_foto(taxon_id: int) -> dict | None:
    chave = f"minigame:fotos:{taxon_id}"
    em_cache = await redis_client.get(chave)
    if em_cache:
        fotos = json.loads(em_cache)
    else:
        dados = await buscar("/observations", {
            "taxon_id": taxon_id,
            "quality_grade": "research",
            "photos": "true",
            "photo_license": LICENCAS_LIVRES,
            "order_by": "random",
            "per_page": 20,
        })
        fotos = []
        for observacao in dados["results"]:
            foto = observacao["photos"][0]
            # a obs pode ter outra foto c licenca e essa n
            if not foto.get("license_code"):
                continue
            fotos.append({
                "url": foto["url"].replace("/square.", "/medium."),
                "atribuicao": foto["attribution"],
            })
        await redis_client.set(chave, json.dumps(fotos), ex=CACHE_SEGUNDOS)

    if not fotos:
        return None
    return random.choice(fotos)
