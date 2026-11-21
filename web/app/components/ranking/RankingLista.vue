<template>
  <div class="space-y-6">
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

        <div class="rounded-full p-1" :class="estiloPodio[item.posicao]?.anel">
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

        <slot name="acoes" :item="item" />

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
        <UsuarioAvatar :avatar="item.avatar" :cor-fundo="item.cor_fundo" :tamanho="36" />
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

        <slot name="acoes" :item="item" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { breakpointsTailwind } from '@vueuse/core'
import type { RankingItemRead } from '~/types/generated'

const props = defineProps<{
  ranking: RankingItemRead[]
}>()

defineSlots<{
  acoes?: (props: { item: RankingItemRead }) => unknown
}>()

const auth = useAuthStore()

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
    const item = props.ranking[posicao - 1]
    if (item) lista.push(item)
  }
  return lista
})

const resto = computed(() => props.ranking.slice(3))

function formatarXp(xp: number) {
  return xp.toLocaleString('pt-BR')
}
</script>
