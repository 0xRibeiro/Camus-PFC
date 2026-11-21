import { FetchError } from 'ofetch'

// 429 do rate limit do back: devolve a msg dele, senao null e a tela usa a msg dela
export function mensagemDeLimite(error: unknown): string | null {
  if (error instanceof FetchError && error.status === 429 && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return null
}
