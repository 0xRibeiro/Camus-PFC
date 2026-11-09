<template>
  <UCard>
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="font-medium">
          Trilhas do grupo
        </h2>
        <div class="flex items-center gap-3">
          <UBadge
            v-if="xp !== null"
            variant="soft"
          >
            {{ xp }} XP no grupo
          </UBadge>
          <UButton
            v-if="dono"
            label="Nova trilha"
            icon="i-lucide-plus"
            @click="modal = true"
          />
        </div>
      </div>
    </template>

    <p
      v-if="loading"
      class="text-muted"
    >
      Carregando trilhas…
    </p>
    <UButton
      v-else-if="erro"
      label="Tentar carregar de novo"
      variant="outline"
      @click="carregar"
    />
    <p
      v-else-if="!trilhas.length"
      class="text-muted"
    >
      Nenhuma trilha disponível.
    </p>
    <div
      v-else
      class="space-y-3"
    >
      <NuxtLink
        v-for="trilha in trilhas"
        :key="trilha.id"
        :to="`/grupos/${grupoId}/trilhas/${trilha.id}`"
        class="flex items-center justify-between gap-3 rounded-lg border border-default p-3 hover:bg-elevated"
      >
        <span class="min-w-0 break-words">{{ trilha.titulo }}</span>
        <UBadge
          v-if="'progresso' in trilha"
          variant="soft"
        >{{ trilha.progresso }}%</UBadge>
        <UBadge
          v-else
          :color="trilha.is_active ? 'success' : 'neutral'"
          variant="soft"
        >
          {{ trilha.is_active ? 'Ativa' : 'Rascunho' }}
        </UBadge>
      </NuxtLink>
    </div>

    <TrilhaFormModal
      v-if="dono"
      v-model:open="modal"
      :trilha="null"
      :saving="saving"
      @submit="criar"
    />
  </UCard>
</template>

<script setup lang="ts">
import type { TrilhaRead, TrilhaResumoRead, XpRead } from '~/types/generated'

const props = defineProps<{ grupoId: number, dono: boolean }>()
const api = useApi(props.grupoId)
const toast = useToast()
const trilhas = ref<(TrilhaRead | TrilhaResumoRead)[]>([])
const xp = ref<number | null>(null)
const loading = ref(true)
const erro = ref(false)
const modal = ref(false)
const saving = ref(false)

async function carregar() {
  loading.value = true
  erro.value = false
  try {
    const [lista, pontos] = await Promise.all([
      props.dono ? api('/trilhas', { query: { sort: 'id' } }) : api('/progresso/trilhas'),
      api('/pontuacao/xp') as Promise<XpRead>,
    ])
    trilhas.value = props.dono ? lista.data : lista
    xp.value = pontos.xp_total
  }
  catch {
    erro.value = true
  }
  finally {
    loading.value = false
  }
}

async function criar(dados: { titulo: string, descricao?: string | null, tag?: string | null, foto?: string | null }) {
  saving.value = true
  try {
    const { titulo, descricao, tag, foto } = dados
    const trilha: TrilhaRead = await api('/trilhas', {
      method: 'POST',
      body: { titulo, descricao, tag, foto },
    })
    modal.value = false
    await navigateTo(`/grupos/${props.grupoId}/trilhas/${trilha.id}`)
  }
  catch {
    toast.add({ title: 'Não foi possível criar a trilha', color: 'error' })
  }
  finally {
    saving.value = false
  }
}

onMounted(carregar)
</script>
