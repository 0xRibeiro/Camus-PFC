<template>
  <div class="mx-auto w-full max-w-4xl space-y-5 [--ui-primary:var(--ui-tertiary)]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <UButton
        to="/minigames"
        label="Minigames"
        icon="i-lucide-arrow-left"
        color="neutral"
        variant="ghost"
      />

      <div
        v-if="rodada"
        class="w-48 space-y-1"
      >
        <p class="text-right text-xs text-muted">
          Acertos com XP hoje: {{ acertosHoje }}/{{ rodada.limite_acertos_com_xp }}
        </p>
        <UProgress
          :model-value="acertosHoje"
          :max="rodada.limite_acertos_com_xp"
          size="sm"
        />
      </div>
    </div>

    <div>
      <h1 class="text-2xl font-semibold text-highlighted">
        Meio peixe, meio fotógrafo
      </h1>
      <p class="text-sm text-muted">
        Qual dos dois foi mais registrado por pessoas no iNaturalist?
      </p>
    </div>

    <!-- placar da sequencia -->
    <div
      v-if="rodada"
      class="flex flex-wrap items-center gap-x-6 gap-y-3 rounded-xl border border-default p-4"
    >
      <div class="flex items-center gap-2">
        <UIcon
          name="i-lucide-flame"
          class="size-6"
          :class="emCombo ? 'animate-pulse text-warning' : 'text-tertiary'"
        />
        <span class="text-2xl font-bold tabular-nums text-highlighted">{{ sequencia }}</span>
        <span class="text-sm text-muted">seguidas</span>
      </div>

      <div class="flex items-center gap-2 text-sm text-muted">
        <UIcon
          name="i-lucide-trophy"
          class="size-4"
        />
        Recorde {{ recorde }}
      </div>

      <div class="ms-auto flex items-center gap-2">
        <UBadge
          v-if="emCombo"
          label="COMBO · 20 XP por acerto"
          color="warning"
          variant="solid"
          icon="i-lucide-zap"
        />
        <template v-else>
          <span class="text-xs text-muted">Combo</span>
          <span
            v-for="i in rodada.sequencia_para_combo"
            :key="i"
            class="size-2.5 rounded-full transition-colors"
            :class="i <= sequencia ? 'bg-tertiary' : 'bg-accented'"
          />
        </template>
      </div>
    </div>

    <UAlert
      v-if="erro"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-alert"
      :title="erro"
      :actions="[{ label: 'Tentar de novo', onClick: carregar }]"
    />

    <div
      v-else-if="!rodada"
      class="grid gap-4 sm:grid-cols-2"
    >
      <USkeleton class="h-64 rounded-xl sm:h-[42dvh]" />
      <USkeleton class="h-64 rounded-xl sm:h-[42dvh]" />
    </div>

    <!-- duelo -->
    <div
      v-else
      class="relative grid gap-4 sm:grid-cols-2"
    >
      <MinigameEspecieCard
        :key="`base-${rodada.base.taxon_id}`"
        :especie="rodada.base"
        :registros="rodada.base.registros ?? null"
      />

      <!-- no celular fica entre os cards, no desktop na altura do meio das fotos -->
      <div class="pointer-events-none relative z-10 mx-auto -my-8 flex size-12 items-center justify-center rounded-full border-4 border-(--ui-bg) bg-tertiary text-sm font-bold text-inverted sm:absolute sm:left-1/2 sm:top-[14dvh] sm:my-0 sm:-translate-x-1/2 sm:-translate-y-1/2">
        VS
      </div>

      <MinigameEspecieCard
        :key="`desafiante-${rodada.desafiante.taxon_id}`"
        :especie="rodada.desafiante"
        :registros="resultado ? resultado.registros_desafiante : null"
        :acertou="resultado ? resultado.acertou : null"
        animar
      >
        <div
          v-if="!resultado"
          class="space-y-2"
        >
          <p class="text-sm text-muted">
            tem
          </p>
          <div class="grid grid-cols-2 gap-2">
            <UButton
              label="Mais"
              icon="i-lucide-chevron-up"
              size="lg"
              block
              :loading="respondendo && palpite === 'mais'"
              :disabled="respondendo"
              @click="responder('mais')"
            />
            <UButton
              label="Menos"
              icon="i-lucide-chevron-down"
              size="lg"
              block
              color="neutral"
              :loading="respondendo && palpite === 'menos'"
              :disabled="respondendo"
              @click="responder('menos')"
            />
          </div>
          <p class="text-xs text-muted">
            registros que {{ rodada.base.nome }}
          </p>
        </div>
      </MinigameEspecieCard>
    </div>

    <!-- acertou: mostra o xp e passa sozinho -->
    <div
      v-if="resultado?.acertou"
      class="flex items-center justify-center gap-2 text-lg font-semibold"
      :class="resultado.combo ? 'text-warning' : 'text-success'"
    >
      <UIcon
        :name="resultado.combo ? 'i-lucide-zap' : 'i-lucide-check'"
        class="size-5"
      />
      <template v-if="resultado.pontos > 0">
        +{{ resultado.pontos }} XP{{ resultado.combo ? ' de combo!' : '' }}
      </template>
      <template v-else>
        Acertou! O XP de hoje já acabou, mas o combo ainda vale
      </template>
    </div>

    <!-- errou: fim da sequencia -->
    <UCard
      v-if="resultado && !resultado.acertou"
      class="text-center"
    >
      <div class="space-y-3">
        <UIcon
          name="i-lucide-fish-off"
          class="size-10 text-error"
        />
        <p class="text-xl font-semibold text-highlighted">
          Fim da sequência!
        </p>
        <p class="text-muted">
          {{ rodada?.desafiante.nome }} (<i>{{ resultado.nome_cientifico_desafiante }}</i>) tem
          {{ resultado.registros_desafiante.toLocaleString('pt-BR') }} registros.
        </p>
        <p class="text-sm text-muted">
          Você fez {{ sequenciaFinal }} {{ sequenciaFinal === 1 ? 'acerto seguido' : 'acertos seguidos' }} · recorde {{ recorde }}
        </p>
        <UButton
          label="Jogar de novo"
          icon="i-lucide-rotate-ccw"
          size="lg"
          @click="carregar"
        />
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import type { ResultadoMaisOuMenosRead, RodadaMaisOuMenosRead } from '~/types/generated'

definePageMeta({ middleware: 'role' })

const api = useApi()
const url = '/minigames/meio-peixe-meio-fotografo/rodadas'

const rodada = ref<RodadaMaisOuMenosRead | null>(null)
const resultado = ref<ResultadoMaisOuMenosRead | null>(null)
const palpite = ref<'mais' | 'menos' | null>(null)
const respondendo = ref(false)
const erro = ref('')
const sequencia = ref(0)
const recorde = ref(0)
const acertosHoje = ref(0)
// guarda quantas fez antes de errar pra mostrar no fim
const sequenciaFinal = ref(0)

const emCombo = computed(() => !!rodada.value && sequencia.value >= rodada.value.sequencia_para_combo)

async function buscar(): Promise<RodadaMaisOuMenosRead> {
  return await api(url, { method: 'POST' })
}

// troca tudo junto qnd a nova chega, se n os botoes da antiga piscam
function aplicar(nova: RodadaMaisOuMenosRead) {
  resultado.value = null
  palpite.value = null
  rodada.value = nova
  sequencia.value = nova.sequencia
  recorde.value = nova.recorde
  acertosHoje.value = nova.acertos_com_xp_hoje
}

async function carregar() {
  erro.value = ''
  try {
    aplicar(await buscar())
  }
  catch {
    rodada.value = null
    erro.value = 'Não foi possível carregar o minigame'
  }
}

function esperar(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function responder(escolha: 'mais' | 'menos') {
  if (!rodada.value) return
  palpite.value = escolha
  respondendo.value = true
  const sequenciaAntes = sequencia.value
  try {
    const resposta: ResultadoMaisOuMenosRead = await api(`${url}/${rodada.value.id}/resposta`, {
      method: 'POST',
      body: { palpite: escolha },
    })
    resultado.value = resposta
    sequencia.value = resposta.sequencia
    recorde.value = resposta.recorde
    acertosHoje.value = resposta.acertos_com_xp_hoje

    if (!resposta.acertou) {
      sequenciaFinal.value = sequenciaAntes
    }
  }
  catch {
    erro.value = 'Não foi possível enviar a resposta'
  }
  finally {
    respondendo.value = false
  }

  if (resultado.value?.acertou) {
    // ja pede a proxima enquanto o numero anima, o back pode demorar buscando foto no iNat
    try {
      const [nova] = await Promise.all([buscar(), esperar(1600)])
      if (!saiu) aplicar(nova)
    }
    catch {
      erro.value = 'Não foi possível carregar o minigame'
    }
  }
}

let saiu = false

onMounted(carregar)
onBeforeUnmount(() => {
  saiu = true
})
</script>
