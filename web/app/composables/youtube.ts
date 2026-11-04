// pega o ID do video não importa o formato do link (normal, curto, embed, shorts)
export function extrairYoutubeId(url: string): string | null {
  const match = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{11})/)
  return match?.[1] ?? null
}
