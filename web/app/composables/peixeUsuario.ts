// ------- peixe do usuario: pega o peixe-user.png e troca o vermelho puro pela cor do perfil.
// borda preta e olho branco ficam iguais. cor transparente vira so o contorno

const TAMANHO_PEIXE = 64

let base: Promise<ImageData> | null = null
const cache = new Map<string, string>()

// carrega a imagem uma vez so e reduz pra 64x64 sem suavizar (pixel art continua igual)
function carregarBase() {
  if (base) return base

  base = new Promise((resolve, reject) => {
    const imagem = new Image()
    imagem.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = TAMANHO_PEIXE
      canvas.height = TAMANHO_PEIXE
      const contexto = canvas.getContext('2d')!
      contexto.imageSmoothingEnabled = false
      contexto.drawImage(imagem, 0, 0, TAMANHO_PEIXE, TAMANHO_PEIXE)
      resolve(contexto.getImageData(0, 0, TAMANHO_PEIXE, TAMANHO_PEIXE))
    }
    imagem.onerror = reject
    imagem.src = '/peixe-user.png'
  })
  return base
}

// #RRGGBB ou #RRGGBBAA (o do konami code) em numeros de 0 a 255
function lerCor(hex: string) {
  const limpo = hex.replace('#', '')
  return {
    r: parseInt(limpo.slice(0, 2), 16),
    g: parseInt(limpo.slice(2, 4), 16),
    b: parseInt(limpo.slice(4, 6), 16),
    a: limpo.length === 8 ? parseInt(limpo.slice(6, 8), 16) : 255,
  }
}

// devolve a imagem pronta (data url), cada cor so e pintada uma vez
export async function peixeDaCor(hex: string) {
  const chave = hex.toUpperCase()
  const pronto = cache.get(chave)
  if (pronto) return pronto

  const original = await carregarBase()
  const pixels = new ImageData(new Uint8ClampedArray(original.data), TAMANHO_PEIXE, TAMANHO_PEIXE)
  const cor = lerCor(chave)

  // cada pixel ocupa 4 posicoes: r, g, b, alpha
  for (let i = 0; i < pixels.data.length; i += 4) {
    const vermelho = pixels.data[i] === 255 && pixels.data[i + 1] === 0 && pixels.data[i + 2] === 0
    if (!vermelho || pixels.data[i + 3] === 0) continue

    pixels.data[i] = cor.r
    pixels.data[i + 1] = cor.g
    pixels.data[i + 2] = cor.b
    pixels.data[i + 3] = cor.a
  }

  const canvas = document.createElement('canvas')
  canvas.width = TAMANHO_PEIXE
  canvas.height = TAMANHO_PEIXE
  canvas.getContext('2d')!.putImageData(pixels, 0, 0)

  const url = canvas.toDataURL('image/png')
  cache.set(chave, url)
  return url
}
