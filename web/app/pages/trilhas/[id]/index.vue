<script setup lang="ts">
import type { ConteudoStatusRead, ConteudoTipo, TrilhaAlunoRead } from '~/types/generated'

definePageMeta({ middleware: 'role' })

const route = useRoute()
const toast = useToast()
const trilhaId = Number(route.params.id)
const NuxtLink = resolveComponent('NuxtLink')

const trilha = ref<TrilhaAlunoRead | null>(null)
const loading = ref(true)

async function fetchTrilha() {
  loading.value = true
  try {
    const api = useApi()
    trilha.value = await api(`/progresso/trilhas/${trilhaId}`)
  }
  catch {
    toast.add({ title: 'Não foi possível carregar a trilha', color: 'error' })
  }
  loading.value = false
}

onMounted(fetchTrilha)

const icones: Record<ConteudoTipo, string> = {
  video: 'i-lucide-play-circle',
  artigo: 'i-lucide-file-text',
  quiz: 'i-lucide-list-checks',
}

// concluido > bloqueado > tipo do conteudo
function iconeDoConteudo(conteudo: ConteudoStatusRead) {
  if (conteudo.concluido) return 'i-lucide-circle-check'
  if (!conteudo.liberado) return 'i-lucide-lock'
  return icones[conteudo.tipo]
}
</script>

<template>
  <div>
    <UButton
      icon="i-lucide-arrow-left"
      label="Trilhas"
      color="neutral"
      variant="link"
      class="px-0 mb-3"
      to="/trilhas"
    />

    <div
      v-if="loading"
      class="flex justify-center py-12"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <template v-else-if="trilha">
      <div class="mb-6 space-y-2">
        <h1 class="text-xl font-semibold">
          {{ trilha.titulo }}
        </h1>
        <p
          v-if="trilha.descricao"
          class="text-sm text-muted"
        >
          {{ trilha.descricao }}
        </p>
        <div class="flex items-center gap-3">
          <UProgress
            :model-value="trilha.progresso"
            size="sm"
            class="flex-1"
          />
          <span class="text-xs text-muted">
            {{ trilha.concluidos }}/{{ trilha.total }} · {{ trilha.progresso }}%
          </span>
        </div>
      </div>

      <div class="space-y-4">
        <UCard
          v-for="modulo in trilha.modulos"
          :key="modulo.id"
        >
          <template #header>
            <div class="flex items-center justify-between">
              <p class="font-semibold">
                {{ modulo.titulo }}
              </p>
              <span class="text-xs text-muted">
                {{ modulo.concluidos }}/{{ modulo.total }}
              </span>
            </div>
          </template>

          <p
            v-if="!modulo.conteudos.length"
            class="text-sm text-muted"
          >
            Nenhum conteúdo neste módulo.
          </p>

          <ul class="divide-y divide-default">
            <li
              v-for="conteudo in modulo.conteudos"
              :key="conteudo.id"
            >
              <!-- so vira link se ja ta liberado -->
              <component
                :is="conteudo.liberado ? NuxtLink : 'div'"
                :to="conteudo.liberado ? `/trilhas/${trilhaId}/conteudos/${conteudo.id}` : undefined"
                class="flex items-center gap-3 py-2"
                :class="conteudo.liberado ? 'hover:text-primary' : 'text-dimmed cursor-not-allowed'"
              >
                <UIcon
                  :name="iconeDoConteudo(conteudo)"
                  class="size-5 shrink-0"
                  :class="{ 'text-success': conteudo.concluido }"
                />
                <span class="flex-1 text-sm">{{ conteudo.titulo }}</span>
                <UBadge
                  v-if="conteudo.atualizado"
                  label="Atualizado"
                  color="warning"
                  variant="soft"
                  size="sm"
                />
                <span class="text-xs text-muted">{{ conteudo.pontos }} XP</span>
              </component>
            </li>
          </ul>
        </UCard>
      </div>
    </template>
  </div>
</template>
