<template>
  <div class="-m-4 flex flex-1 flex-col">
    <div
      class="mx-auto w-full max-w-5xl space-y-4 px-4 pt-6 pb-4"
      :style="tema"
    >
      <!-- cabecalho com o avatar, a edicao fica no modal -->
      <UCard :class="card">
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
        <section class="grid gap-4 sm:grid-cols-3">
          <UCard
            v-for="numero in numeros"
            :key="numero.titulo"
            :class="card"
          >
            <div class="flex items-center gap-3">
              <div
                class="flex size-10 shrink-0 items-center justify-center rounded-lg text-primary"
                :class="{
                  'ring ring-default': estilo === 'xadrez',
                  'bg-white/30 ring ring-white/60 backdrop-blur-sm dark:bg-white/10 dark:ring-white/20': estilo === 'vidro',
                  'bg-primary/10': !estilo,
                }"
                :style="estilo === 'xadrez' ? { background: XADREZ } : {}"
              >
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

        <PerfilXp />

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

const { estilo, tema, card } = usePerfilVisual()

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
