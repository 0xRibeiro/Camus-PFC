import { FetchError } from 'ofetch'

// envio generico de imagem, serve pro editor, foto da trilha e oq mais precisar
export function useUploadImagem() {
  const api = useApi()

  // manda o arquivo pro POST /imagens e devolve so a url salva
  async function enviarImagem(arquivo: File): Promise<string> {
    const formData = new FormData()
    formData.append('file', arquivo)

    const resultado = await api('/imagens', { method: 'POST', body: formData })
    return resultado.url
  }

  // pega a msg q o backend mandou (formato errado, maior q 10 MB...)
  function mensagemDeErro(erro: unknown): string {
    if (erro instanceof FetchError && erro.data?.detail) {
      return erro.data.detail
    }
    return 'Não foi possível enviar a imagem'
  }

  return { enviarImagem, mensagemDeErro }
}
