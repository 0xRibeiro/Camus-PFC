<template>
  <div class="mx-auto w-full max-w-3xl space-y-6 [--ui-primary:var(--ui-tertiary)]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <UButton
        to="/minigames"
        label="Minigames"
        icon="i-lucide-arrow-left"
        color="neutral"
        variant="ghost"
      />

      <!-- quantos acertos ainda dao xp hoje -->
      <div
        v-if="acertosHoje !== null"
        class="w-48 space-y-1"
      >
        <p class="text-right text-xs text-muted">
          Acertos com XP hoje: {{ acertosHoje }}/{{ limite }}
        </p>
        <UProgress
          :model-value="acertosHoje"
          :max="limite"
          size="sm"
        />
      </div>
    </div>

    <h1 class="text-2xl font-semibold text-highlighted">
      Quem é esse peixe?
    </h1>

    <UAlert
      v-if="erro"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-alert"
      :title="erro"
      :actions="[{ label: 'Tentar de novo', onClick: novaRodada }]"
    />

    <template v-else>
      <figure class="space-y-2">
        <USkeleton
          v-if="!rodada"
          class="h-[40dvh] min-h-56 w-full rounded-xl"
        />
        <!-- alt neutro pra n entregar a resposta no titulo do modal -->
        <MinigameFotoZoom
          v-else
          :key="rodada.id"
          :src="rodada.foto_url"
          alt="Animal misterioso"
          :atribuicao="`Foto: ${rodada.foto_atribuicao} · iNaturalist`"
          img-class="h-[40dvh] min-h-56 object-contain"
          class="rounded-xl"
        />
        <figcaption
          v-if="rodada"
          class="text-xs text-muted"
        >
          Foto: {{ rodada.foto_atribuicao }} · iNaturalist
        </figcaption>
      </figure>

      <div class="grid gap-3 sm:grid-cols-2">
        <template v-if="!rodada">
          <USkeleton
            v-for="i in 4"
            :key="i"
            class="h-12 w-full"
          />
        </template>
        <UButton
          v-for="opcao in rodada?.opcoes"
          v-else
          :key="opcao.taxon_id"
          :label="opcao.nome"
          :color="corDaOpcao(opcao.taxon_id)"
          :variant="resultado ? 'soft' : 'outline'"
          :loading="respondendo && escolhida === opcao.taxon_id"
          :disabled="!!resultado || respondendo"
          size="xl"
          block
          class="disabled:opacity-100"
          @click="responder(opcao.taxon_id)"
        />
      </div>

      <template v-if="resultado">
        <UAlert
          :color="resultado.acertou ? 'success' : 'error'"
          variant="subtle"
          :icon="resultado.acertou ? 'i-lucide-party-popper' : 'i-lucide-circle-x'"
          :title="tituloResultado"
        >
          <template #description>
            {{ resultado.resposta_nome }} · <i>{{ resultado.resposta_nome_cientifico }}</i>
          </template>
        </UAlert>

        <UButton
          label="Próximo"
          trailing-icon="i-lucide-arrow-right"
          size="lg"
          block
          @click="novaRodada"
        />
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ResultadoRead, RodadaRead } from '~/types/generated'

definePageMeta({ middleware: 'role' })

const api = useApi()

const rodada = ref<RodadaRead | null>(null)
const resultado = ref<ResultadoRead | null>(null)
const escolhida = ref<number | null>(null)
const respondendo = ref(false)
const erro = ref('')
const acertosHoje = ref<number | null>(null)
const limite = ref(20)

const tituloResultado = computed(() => {
  if (!resultado.value) return ''
  if (!resultado.value.acertou) return 'Não foi dessa vez! A resposta era:'
  if (resultado.value.pontos > 0) return `Acertou! +${resultado.value.pontos} XP`
  return 'Acertou! O XP de hoje já acabou, mas pode continuar jogando'
})

async function novaRodada() {
  rodada.value = null
  resultado.value = null
  escolhida.value = null
  erro.value = ''
  try {
    const nova: RodadaRead = await api('/minigames/quem-e-esse-peixe/rodadas', { method: 'POST' })
    rodada.value = nova
    acertosHoje.value = nova.acertos_com_xp_hoje
    limite.value = nova.limite_acertos_com_xp
  }
  catch {
    erro.value = 'Não foi possível carregar o minigame'
  }
}

async function responder(taxonId: number) {
  if (!rodada.value) return
  escolhida.value = taxonId
  respondendo.value = true
  try {
    const resposta: ResultadoRead = await api(`/minigames/quem-e-esse-peixe/rodadas/${rodada.value.id}/resposta`, {
      method: 'POST',
      body: { taxon_id: taxonId },
    })
    resultado.value = resposta
    acertosHoje.value = resposta.acertos_com_xp_hoje
  }
  catch {
    erro.value = 'Não foi possível enviar a resposta'
  }
  finally {
    respondendo.value = false
  }
}

// dps de responder a certa fica verde e a errada q escolheu fica vermelha
function corDaOpcao(taxonId: number) {
  if (!resultado.value) return 'neutral'
  if (taxonId === resultado.value.resposta_taxon_id) return 'success'
  if (taxonId === escolhida.value) return 'error'
  return 'neutral'
}

onMounted(novaRodada)
</script>
