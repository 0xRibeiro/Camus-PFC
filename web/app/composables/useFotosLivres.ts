import type { FotoInat, TaxonInat } from '~/utils/inaturalista'
import { fotoLivre } from '~/utils/inaturalista'

// so foto c licenca livre no sistema todo, msm regra do back (minigame/inat.py buscar_taxon):
// principal se for livre, se n a 1a livre do taxon
export function useFotosLivres() {
  const inat = useInat()

  // sem chave = buscando, null = n tem foto livre
  const fotos = ref<Record<number, FotoInat | null>>({})

  async function carregar(taxons: Pick<TaxonInat, 'id' | 'default_photo'>[]) {
    const faltando: number[] = []
    for (const taxon of taxons) {
      if (taxon.id in fotos.value) continue

      const foto = fotoLivre(taxon.default_photo)
      if (foto) fotos.value[taxon.id] = foto
      else faltando.push(taxon.id)
    }
    if (!faltando.length) return

    // o /taxa aceita varios ids, entao e uma req so
    try {
      const resposta = await inat<{ results?: TaxonInat[] }>(`/taxa/${faltando.join(',')}`)
      for (const taxon of resposta.results ?? []) {
        let achou: FotoInat | null = null
        for (const item of taxon.taxon_photos ?? []) {
          achou = fotoLivre(item.photo)
          if (achou) break
        }
        fotos.value[taxon.id] = achou
      }
    }
    catch {
      // deu erro fica sem foto msm
    }

    for (const id of faltando) {
      if (!(id in fotos.value)) fotos.value[id] = null
    }
  }

  function carregando(id: number) {
    return !(id in fotos.value)
  }

  return { fotos, carregar, carregando }
}
