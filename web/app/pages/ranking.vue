<template>
  <div class="mx-auto w-full max-w-4xl space-y-8 [--ui-primary:var(--ui-secondary)]">
    <div class="relative isolate overflow-hidden rounded-xl bg-[#1b1300] px-6 sm:px-8">
      <img
        src="/papeis-de-parede/amarelo/conquistas.webp"
        alt=""
        class="pointer-events-none absolute inset-0 -z-20 size-full object-cover object-[72%_center]"
      >

      <div
        aria-hidden="true"
        class="absolute inset-0 -z-10 bg-linear-to-r from-[#1b1300]/95 via-[#1b1300]/60 to-transparent"
      />

      <UPageHeader
        title="Ranking"
        description="Os 50 exploradores com mais XP no Camus."
        :ui="{ title: 'text-white', description: 'text-amber-100/85' }"
      >
        <template #headline>
          <div class="flex items-center gap-2 text-sm font-medium text-amber-300">
            <UIcon
              name="i-lucide-medal"
              class="size-4"
            />
            Comunidade
          </div>
        </template>
      </UPageHeader>
    </div>

    <UAlert
      v-if="erro"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-alert"
      title="Não foi possível carregar o ranking"
      :actions="[{ label: 'Tentar de novo', onClick: carregar }]"
    />

    <!-- carregando -->
    <div
      v-else-if="carregando"
      class="space-y-6"
    >
      <div class="grid grid-cols-3 items-end gap-3">
        <USkeleton class="h-48 rounded-xl" />
        <USkeleton class="h-60 rounded-xl" />
        <USkeleton class="h-40 rounded-xl" />
      </div>
      <USkeleton
        v-for="i in 5"
        :key="i"
        class="h-14 rounded-xl"
      />
    </div>

    <UCard
      v-else-if="!ranking.length"
      class="text-center"
    >
      <UIcon
        name="i-lucide-trophy"
        class="size-10 text-primary"
      />
      <p class="mt-2 text-muted">
        Ninguém ganhou XP ainda. Que tal ser o primeiro?
      </p>
    </UCard>

    <template v-else>
      <!-- podio: 2º, 1º, 3º pro primeiro ficar no meio -->
      <section class="grid grid-cols-3 items-end gap-2 sm:gap-4">
        <div
          v-for="item in podio"
          :key="item.usuario_id"
          class="row-start-1 flex min-w-0 flex-col items-center"
          :class="estiloPodio[item.posicao]?.coluna"
        >
          <UIcon
            v-if="item.posicao === 1"
            name="i-lucide-crown"
            class="mb-1 size-7 text-amber-400 drop-shadow-[0_0_8px_rgba(251,191,36,0.6)] sm:size-9"
          />

          <div
            class="rounded-full p-1"
            :class="estiloPodio[item.posicao]?.anel"
          >
            <UsuarioAvatar
              :avatar="item.avatar"
              :cor-fundo="item.cor_fundo"
              :tamanho="item.posicao === 1 ? tamanhoPrimeiro : tamanhoOutros"
            />
          </div>

          <p
            class="mt-2 w-full truncate text-center text-sm font-semibold sm:text-base"
            :class="item.usuario_id === auth.user?.id ? 'text-primary' : 'text-highlighted'"
          >
            {{ item.username }}
          </p>
          <p class="text-xs font-medium tabular-nums text-muted sm:text-sm">
            {{ formatarXp(item.xp_total) }} XP
          </p>

          <!-- degrau -->
          <div
            class="mt-2 flex w-full items-start justify-center rounded-t-xl bg-linear-to-b pt-3 text-3xl font-black text-white/90 sm:text-4xl"
            :class="estiloPodio[item.posicao]?.degrau"
          >
            {{ item.posicao }}
          </div>
        </div>
      </section>

      <!-- do 4º pra baixo -->
      <section
        v-if="resto.length"
        class="divide-y divide-default overflow-hidden rounded-xl border border-default"
      >
        <div
          v-for="item in resto"
          :key="item.usuario_id"
          class="flex items-center gap-3 px-4 py-3"
          :class="{ 'bg-primary/10': item.usuario_id === auth.user?.id }"
        >
          <span class="w-7 text-right text-sm font-semibold tabular-nums text-muted">
            {{ item.posicao }}º
          </span>
          <UsuarioAvatar
            :avatar="item.avatar"
            :cor-fundo="item.cor_fundo"
            :tamanho="36"
          />
          <span class="min-w-0 flex-1 truncate font-medium text-highlighted">
            {{ item.username }}
            <UBadge
              v-if="item.usuario_id === auth.user?.id"
              label="você"
              size="sm"
              variant="subtle"
              class="ms-1"
            />
          </span>
          <span class="text-sm font-semibold tabular-nums text-primary">
            {{ formatarXp(item.xp_total) }} XP
          </span>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { breakpointsTailwind } from '@vueuse/core'
import type { RankingItemRead } from '~/types/generated'

definePageMeta({ middleware: 'role' })

const api = useApi()
const auth = useAuthStore()

const ranking = ref<RankingItemRead[]>([])
const carregando = ref(true)
const erro = ref(false)

// ouro, prata e bronze
// coluna fixa pro 1º ficar no meio mesmo se tiver menos de 3 no ranking
const estiloPodio: Record<number, { coluna: string, anel: string, degrau: string }> = {
  1: { coluna: 'col-start-2', anel: 'bg-linear-to-b from-amber-300 to-amber-600', degrau: 'h-28 from-amber-400 to-amber-700 sm:h-36' },
  2: { coluna: 'col-start-1', anel: 'bg-linear-to-b from-slate-200 to-slate-500', degrau: 'h-20 from-slate-300 to-slate-600 sm:h-24' },
  3: { coluna: 'col-start-3', anel: 'bg-linear-to-b from-orange-300 to-orange-800', degrau: 'h-14 from-orange-400 to-orange-800 sm:h-16' },
}

const telaGrande = useBreakpoints(breakpointsTailwind).greaterOrEqual('sm')
const tamanhoPrimeiro = computed(() => (telaGrande.value ? 96 : 72))
const tamanhoOutros = computed(() => (telaGrande.value ? 72 : 56))

const podio = computed(() => {
  const ordem = [2, 1, 3]
  const lista = []
  for (const posicao of ordem) {
    const item = ranking.value[posicao - 1]
    if (item) lista.push(item)
  }
  return lista
})

const resto = computed(() => ranking.value.slice(3))

function formatarXp(xp: number) {
  return xp.toLocaleString('pt-BR')
}

async function carregar() {
  carregando.value = true
  erro.value = false
  try {
    ranking.value = await api('/pontuacao/ranking')
  }
  catch {
    erro.value = true
  }
  carregando.value = false
}

onMounted(carregar)
</script>
