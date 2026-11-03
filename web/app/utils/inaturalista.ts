// grupos que incluem animais relevantes para a coleção do Camus. fazendo uma iNaturalistA hahaha
export const GRUPOS_COLECAO = [
  { id: 47178, nome: 'Peixes com nadadeiras raiadas' },
  { id: 47273, nome: 'Tubarões e raias' },
  { id: 60450, nome: 'Quimeras' },
  { id: 85511, nome: 'Celacantos' },
  { id: 49099, nome: 'Mixinas' },
  { id: 47115, nome: 'Moluscos' },
  { id: 85493, nome: 'Crustáceos' },
  { id: 47534, nome: 'Cnidários' },
  { id: 47549, nome: 'Equinodermos' },
  { id: 48824, nome: 'Esponjas' },
  { id: 51508, nome: 'Ctenóforos' },
  { id: 47490, nome: 'Poliquetas' },
  { id: 68104, nome: 'Briozoários' },
  { id: 130868, nome: 'Tunicados' },
  { id: 122158, nome: 'Braquiópodes' },
  { id: 152871, nome: 'Baleias e golfinhos' },
  { id: 372843, nome: 'Focas, leões-marinhos e morsas' },
  { id: 46306, nome: 'Peixes-boi e dugongos' },
  { id: 372234, nome: 'Tartarugas marinhas' },
  { id: 67564, nome: 'Pinguins' },
  { id: 67565, nome: 'Albatrozes, petréis e afins' },
  { id: 129726, nome: 'Cefalocordados' },
  { id: 48051, nome: 'Foronídeos' },
  { id: 68235, nome: 'Hemicordados' },
  { id: 51280, nome: 'Nemertinos' },
]

// transforma os ids no formato usado pelo filtro da iNaturalist.
export const TAXONS_COLECAO = GRUPOS_COLECAO.map(grupo => grupo.id).join(',')
