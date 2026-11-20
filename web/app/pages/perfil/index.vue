<template>
  <div class="-m-4 flex flex-1 flex-col">
    <div class="mx-auto w-full max-w-5xl space-y-4 px-4 pt-6 pb-4">
      <!-- cabecalho com o avatar, a edicao fica no modal -->
      <UCard>
        <div class="flex flex-col items-center gap-5 text-center sm:flex-row sm:text-left">
          <UsuarioAvatar
            :avatar="auth.user?.avatar ?? 'peixe-palhaco'"
            :cor-fundo="auth.user?.cor_fundo ?? '#0EA5E9'"
            :tamanho="96"
          />

          <div class="min-w-0 flex-1 space-y-1">
            <h1 class="truncate text-2xl font-semibold text-highlighted">
              {{ auth.user?.username }}
            </h1>
            <p class="truncate text-sm text-muted">
              {{ auth.user?.email }}
            </p>
            <UBadge
              :label="auth.user?.role"
              variant="subtle"
            />
          </div>

          <UButton
            label="Editar perfil"
            icon="i-lucide-pencil"
            color="neutral"
            variant="outline"
            @click="editando = true"
          />
        </div>
      </UCard>

      <!-- so aluno ganha xp global, autor e admin ficam so com a edicao -->
      <template v-if="auth.role === 'aluno'">
        <section
          class="grid gap-4 sm:grid-cols-3"
          :style="corDoPerfil"
        >
          <UCard
            v-for="numero in numeros"
            :key="numero.titulo"
          >
            <div class="flex items-center gap-3">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <UIcon
                  :name="numero.icone"
                  class="size-5"
                />
              </div>
              <div class="min-w-0">
                <p class="text-sm text-muted">
                  {{ numero.titulo }}
                </p>
                <USkeleton
                  v-if="carregando"
                  class="mt-1 h-7 w-16"
                />
                <p
                  v-else
                  class="text-2xl font-semibold text-highlighted tabular-nums"
                >
                  {{ numero.valor }}
                </p>
              </div>
            </div>
          </UCard>
        </section>

        <PerfilXp :style="corDoPerfil" />

        <div class="grid gap-4 lg:grid-cols-2">
          <PerfilConquistas :conquistas="minhasConquistas" />
          <PerfilRecordes />
        </div>

        <div class="grid gap-4 lg:grid-cols-3">
          <PerfilTrilhas
            :trilhas="trilhas"
            :carregando="carregando"
            class="lg:col-span-2"
          />
          <PerfilTrilhasConcluidas
            :trilhas="trilhas"
            :carregando="carregando"
          />
        </div>
      </template>
    </div>

    <PerfilEditarModal v-model:open="editando" />

    <CamusImagem
      src="/papeis-de-parede/anil/perfil.webp"
      class="mt-auto w-full shrink-0"
      img-class="h-auto w-full"
    />
  </div>
</template>

<script setup lang="ts">
import type { ConquistaRead, ConquistaUsuarioRead, TrilhaResumoRead, XpRead } from '~/types/generated'

// so exige estar logado, qualquer papel
definePageMeta({ middleware: 'role' })

const auth = useAuthStore()

const editando = ref(false)
const carregando = ref(true)
const xp = ref<XpRead | null>(null)
const minhasConquistas = ref<ConquistaUsuarioRead[]>([])
const totalConquistas = ref(0)
const trilhas = ref<TrilhaResumoRead[]>([])

function matizDaCor(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16) / 255
  const g = parseInt(hex.slice(3, 5), 16) / 255
  const b = parseInt(hex.slice(5, 7), 16) / 255
  const maior = Math.max(r, g, b)
  const menor = Math.min(r, g, b)
  const diferenca = maior - menor

  if (diferenca < 0.08) return null

  let matiz
  if (maior === r) matiz = ((g - b) / diferenca) % 6
  else if (maior === g) matiz = (b - r) / diferenca + 2
  else matiz = (r - g) / diferenca + 4

  return Math.round(matiz * 60 + 360) % 360
}

// troca o primary so nos cards e no grafico
const corDoPerfil = computed(() => {
  const matiz = matizDaCor(auth.user?.cor_fundo ?? '#0EA5E9')
  if (matiz === null) return {}
  return { '--ui-primary': `hsl(${matiz} 75% 50%)` }
})

const numeros = computed(() => [
  { titulo: 'XP total', icone: 'i-lucide-sparkles', valor: xp.value?.xp_total ?? 0 },
  { titulo: 'Ranking', icone: 'i-lucide-medal', valor: xp.value?.posicao ? `${xp.value.posicao}º` : '—' },
  { titulo: 'Conquistas', icone: 'i-lucide-trophy', valor: `${minhasConquistas.value.length}/${totalConquistas.value}` },
])

onMounted(async () => {
  if (auth.role !== 'aluno') return
  const api = useApi()
  try {
    const [respostaXp, respostaMinhas, respostaTodas, respostaTrilhas] = await Promise.all([
      api('/pontuacao/xp') as Promise<XpRead>,
      api('/usuarios/me/conquistas') as Promise<ConquistaUsuarioRead[]>,
      // o fastcrud manda a lista dentro de data
      api('/conquistas') as Promise<{ data: ConquistaRead[] }>,
      api('/progresso/trilhas') as Promise<TrilhaResumoRead[]>,
    ])
    trilhas.value = respostaTrilhas
    xp.value = respostaXp
    minhasConquistas.value = respostaMinhas
    totalConquistas.value = respostaTodas.data.length
  }
  catch {
    // os cards ficam zerados, o resto da tela busca sozinho
  }
  carregando.value = false
})
</script>
