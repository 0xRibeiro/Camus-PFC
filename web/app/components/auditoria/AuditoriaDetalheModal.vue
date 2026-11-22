<template>
  <UModal
    v-model:open="open"
    :title="ehVisualizacao ? 'Detalhes da visualização' : 'Detalhes da alteração'"
  >
    <template #body>
      <!-- view n muda nada, so registra q alguem olhou um dado -->
      <p
        v-if="ehVisualizacao"
        class="text-sm"
      >
        Visualizou o campo
        <span class="font-semibold">{{ props.log?.alteracoes.campo }}</span>
        de {{ props.log?.entidade }} #{{ props.log?.entidade_id }}.
      </p>

      <div
        v-else
        class="grid grid-cols-2 gap-4"
      >
        <div>
          <p class="font-medium mb-2">
            Antes
          </p>
          <pre class="text-xs bg-elevated p-3 rounded overflow-auto">{{ antigoFormatado }}</pre>
        </div>

        <div>
          <p class="font-medium mb-2">
            Depois
          </p>
          <pre class="text-xs bg-elevated p-3 rounded overflow-auto">{{ novoFormatado }}</pre>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { LogAuditoriaRead } from '~/types/generated'

const props = defineProps<{
  log: LogAuditoriaRead | null
}>()

const open = defineModel<boolean>('open', { required: true })

const ehVisualizacao = computed(() => props.log?.acao === 'view')

const antigoFormatado = computed(() => JSON.stringify(props.log?.alteracoes.antigo, null, 2))
const novoFormatado = computed(() => JSON.stringify(props.log?.alteracoes.novo, null, 2))
</script>
