// ------- entidades da auditoria: as tabelas com trigger, com nome e cor de cada uma.
// cor fora do tema de proposito, o tema n tem 12 cores e as de acao (verde, amarelo...) ja tao em uso.
// classe escrita inteira pro tailwind achar
export const ENTIDADES_AUDITORIA = [
  { value: 'usuarios', label: 'Usuários', classe: 'bg-sky-500/15 text-sky-400', ponto: 'bg-sky-400' },
  { value: 'trilhas', label: 'Trilhas', classe: 'bg-orange-500/15 text-orange-400', ponto: 'bg-orange-400' },
  { value: 'modulos', label: 'Módulos', classe: 'bg-amber-500/15 text-amber-300', ponto: 'bg-amber-300' },
  { value: 'conteudos', label: 'Conteúdos', classe: 'bg-lime-500/15 text-lime-400', ponto: 'bg-lime-400' },
  { value: 'questoes', label: 'Questões', classe: 'bg-teal-500/15 text-teal-300', ponto: 'bg-teal-300' },
  { value: 'alternativas', label: 'Alternativas', classe: 'bg-cyan-500/15 text-cyan-300', ponto: 'bg-cyan-300' },
  { value: 'conquistas', label: 'Conquistas', classe: 'bg-yellow-500/15 text-yellow-300', ponto: 'bg-yellow-300' },
  { value: 'grupos', label: 'Grupos', classe: 'bg-violet-500/15 text-violet-400', ponto: 'bg-violet-400' },
  { value: 'avisos', label: 'Avisos', classe: 'bg-fuchsia-500/15 text-fuchsia-400', ponto: 'bg-fuchsia-400' },
  { value: 'denuncias', label: 'Denúncias', classe: 'bg-rose-500/15 text-rose-400', ponto: 'bg-rose-400' },
  { value: 'documentos_legais', label: 'Documentos legais', classe: 'bg-indigo-500/15 text-indigo-300', ponto: 'bg-indigo-300' },
  { value: 'aceites_documentos_legais', label: 'Aceites de documentos', classe: 'bg-slate-500/20 text-slate-300', ponto: 'bg-slate-300' },
] as const

// entidade q n ta na lista (tabela nova sem cor ainda) cai no cinza com o nome cru
export function entidadeAuditoria(valor: string) {
  for (const entidade of ENTIDADES_AUDITORIA) {
    if (entidade.value === valor) return entidade
  }
  return { value: valor, label: valor, classe: 'bg-elevated text-muted', ponto: 'bg-muted' }
}
