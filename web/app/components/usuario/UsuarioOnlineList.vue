<template>
  <UCard
    class="mb-6"
    :ui="{ body: 'p-0 sm:p-0' }"
  >
    <template #header>
      <p class="font-medium">
        Online agora
        <span
          v-if="!loading"
          class="text-muted"
        >({{ usuarios.length }})</span>
      </p>
    </template>

    <!-- o aquario: cada peixe e um usuario online, com a cor do perfil dele -->
    <div
      ref="aquario"
      class="relative h-64 overflow-hidden bg-cover bg-center"
      :style="{ backgroundImage: `url(${fundo})` }"
    >
      <p
        v-if="!loading && usuarios.length === 0"
        class="absolute inset-0 flex items-center justify-center text-sm font-medium text-highlighted"
      >
        Ninguém online no momento.
      </p>

      <!-- posicao muda direto no elemento a cada quadro, sem passar pelo vue -->
      <div
        v-for="peixe in peixes"
        :key="peixe.usuario.id"
        :ref="(el) => registrarElemento(peixe.usuario.id, el as HTMLElement | null)"
        class="absolute top-0 left-0 flex flex-col items-center will-change-transform"
        :style="{ width: `${LARGURA}px` }"
      >
        <img
          :src="peixe.imagem"
          :alt="peixe.usuario.username"
          :width="TAMANHO"
          :height="TAMANHO"
          class="[image-rendering:pixelated] transition-transform duration-300"
        >
        <span class="-mt-2 max-w-full truncate rounded bg-default/70 px-1.5 text-xs font-medium text-highlighted">
          {{ peixe.usuario.username }}
        </span>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { UsuarioAdminRead } from '~/types/generated'

const props = defineProps<{
  usuarios: UsuarioAdminRead[]
  loading: boolean
}>()

// ------- tamanhos: o peixe e a caixa dele (peixe + nome embaixo)
const TAMANHO = 56
const LARGURA = 96
const ALTURA = 72
// mais q isso nadando ao mesmo tempo, o resto espera na fila
const MAXIMO = 30

const tema = useColorMode()
const fundo = computed(() => tema.value === 'dark'
  ? '/papeis-de-parede/transparente/fundo1-dark.jpg'
  : '/papeis-de-parede/transparente/fundo1-claro.jpg')

const aquario = ref<HTMLElement | null>(null)
const reduzirMovimento = usePreferredReducedMotion()

// ------- quem ta na tela (reativo, pro v-for) e o movimento de cada um (n reativo, muda todo quadro)
interface Peixe {
  usuario: UsuarioAdminRead
  imagem: string
}

interface Movimento {
  x: number
  y: number
  vx: number
  vy: number
  // bateu na borda com gente na fila: continua reto ate sumir
  saindo: boolean
}

const peixes = ref<Peixe[]>([])
const movimentos = new Map<number, Movimento>()
const elementos = new Map<number, HTMLElement>()
// ids de quem ta online mas esperando a vez de nadar
let fila: number[] = []

function registrarElemento(id: number, el: HTMLElement | null) {
  if (el) {
    elementos.set(id, el)
    desenhar(id)
  }
  else {
    elementos.delete(id)
  }
}

function tamanhoDoAquario() {
  return {
    largura: aquario.value?.clientWidth ?? 600,
    altura: aquario.value?.clientHeight ?? 256,
  }
}

function sortear(min: number, max: number) {
  return min + Math.random() * (max - min)
}

// direcao meio de lado, peixe nada mais na horizontal. sentido -1 = esquerda, 1 = direita
function velocidade(sentido: number) {
  const rapidez = sortear(25, 55)
  const angulo = sortear(-0.6, 0.6)
  return { vx: Math.cos(angulo) * rapidez * sentido, vy: Math.sin(angulo) * rapidez }
}

function sentidoAleatorio() {
  return Math.random() < 0.5 ? -1 : 1
}

// primeira leva nasce espalhada; quem vem da fila entra por um dos lados
function criarMovimento(entrandoPelaBorda: boolean): Movimento {
  const { largura, altura } = tamanhoDoAquario()
  const y = sortear(0, Math.max(0, altura - ALTURA))

  if (entrandoPelaBorda) {
    const sentido = sentidoAleatorio()
    const x = sentido === 1 ? -LARGURA : largura
    return { x, y, ...velocidade(sentido), saindo: false }
  }

  return { x: sortear(0, Math.max(0, largura - LARGURA)), y, ...velocidade(sentidoAleatorio()), saindo: false }
}

async function colocarNaAgua(usuario: UsuarioAdminRead, entrandoPelaBorda: boolean) {
  movimentos.set(usuario.id, criarMovimento(entrandoPelaBorda))
  const imagem = await peixeDaCor(usuario.cor_fundo)
  // pode ter saido do online enquanto a imagem era pintada
  if (!movimentos.has(usuario.id)) return
  peixes.value = [...peixes.value, { usuario, imagem }]
}

function tirarDaAgua(id: number) {
  movimentos.delete(id)
  const restantes: Peixe[] = []
  for (const peixe of peixes.value) {
    if (peixe.usuario.id !== id) restantes.push(peixe)
  }
  peixes.value = restantes
}

function buscarUsuario(id: number) {
  for (const usuario of props.usuarios) {
    if (usuario.id === id) return usuario
  }
  return null
}

// proximo da fila entra no lugar de quem saiu
function chamarDaFila() {
  const id = fila.shift()
  if (id === undefined) return
  const usuario = buscarUsuario(id)
  if (usuario) colocarNaAgua(usuario, true)
}

// ------- lista nova do back (a cada 1 min): tira quem saiu, atualiza cor, poe quem chegou na fila
let primeiraLeva = true

async function sincronizar(usuarios: UsuarioAdminRead[]) {
  const online = new Set<number>()
  for (const usuario of usuarios) online.add(usuario.id)

  for (const peixe of [...peixes.value]) {
    if (!online.has(peixe.usuario.id)) tirarDaAgua(peixe.usuario.id)
  }

  const novaFila: number[] = []
  for (const id of fila) {
    if (online.has(id)) novaFila.push(id)
  }
  fila = novaFila

  // trocou a cor do perfil: repinta o peixe
  for (const peixe of peixes.value) {
    const atual = buscarUsuario(peixe.usuario.id)
    if (atual && atual.cor_fundo !== peixe.usuario.cor_fundo) {
      peixe.usuario = atual
      peixe.imagem = await peixeDaCor(atual.cor_fundo)
    }
  }

  const naTela = new Set<number>()
  for (const id of movimentos.keys()) naTela.add(id)

  for (const usuario of usuarios) {
    if (naTela.has(usuario.id) || fila.includes(usuario.id)) continue
    if (naTela.size < MAXIMO) {
      naTela.add(usuario.id)
      colocarNaAgua(usuario, !primeiraLeva)
    }
    else {
      fila.push(usuario.id)
    }
  }
  primeiraLeva = false
}

// so depois de montar: precisa do canvas (n existe no servidor) e do tamanho do aquario
watch(() => props.usuarios, sincronizar)

// ------- animacao
function desenhar(id: number) {
  const el = elementos.get(id)
  const movimento = movimentos.get(id)
  if (!el || !movimento) return

  el.style.transform = `translate(${movimento.x}px, ${movimento.y}px)`
  // a imagem olha pra esquerda, vira quando nada pra direita
  const imagem = el.querySelector('img')
  if (imagem) imagem.style.transform = movimento.vx > 0 ? 'scaleX(-1)' : ''
}

// bateu: sem fila escolhe outro rumo pra dentro, com fila sai e da a vez
function bateu(id: number, movimento: Movimento, horizontal: boolean, paraDentro: number) {
  if (fila.length) {
    movimento.saindo = true
    return
  }

  if (horizontal) {
    const nova = velocidade(paraDentro)
    movimento.vx = nova.vx
    movimento.vy = nova.vy
  }
  else {
    // em cima ou embaixo: mantem o lado q tava indo, so vira o vertical
    const nova = velocidade(movimento.vx > 0 ? 1 : -1)
    movimento.vx = nova.vx
    movimento.vy = Math.abs(nova.vy || 10) * paraDentro
  }
}

function passo(segundos: number) {
  const { largura, altura } = tamanhoDoAquario()
  const sairam: number[] = []

  for (const [id, movimento] of movimentos) {
    movimento.x += movimento.vx * segundos
    movimento.y += movimento.vy * segundos

    if (movimento.saindo) {
      const sumiu = movimento.x < -LARGURA || movimento.x > largura
        || movimento.y < -ALTURA || movimento.y > altura
      if (sumiu) sairam.push(id)
    }
    // so conta batida indo pra fora, assim quem ta entrando pela borda n bate
    else if (movimento.x < 0 && movimento.vx < 0) {
      bateu(id, movimento, true, 1)
    }
    else if (movimento.x > largura - LARGURA && movimento.vx > 0) {
      bateu(id, movimento, true, -1)
    }
    else if (movimento.y < 0 && movimento.vy < 0) {
      bateu(id, movimento, false, 1)
    }
    else if (movimento.y > altura - ALTURA && movimento.vy > 0) {
      bateu(id, movimento, false, -1)
    }

    desenhar(id)
  }

  // quem saiu vai pro fim da fila e o proximo entra
  for (const id of sairam) {
    tirarDaAgua(id)
    fila.push(id)
    chamarDaFila()
  }
}

let anterior = 0

// requestAnimationFrame pausa sozinho com a aba escondida
const { pause, resume } = useRafFn(({ timestamp }) => {
  // limita o salto quando volta de uma aba escondida, senao o peixe teleporta
  const segundos = anterior ? Math.min((timestamp - anterior) / 1000, 0.1) : 0
  anterior = timestamp
  passo(segundos)
}, { immediate: false })

onMounted(() => {
  sincronizar(props.usuarios)
  if (reduzirMovimento.value !== 'reduce') resume()
})

watch(reduzirMovimento, (valor) => {
  if (valor === 'reduce') pause()
  else resume()
})
</script>
