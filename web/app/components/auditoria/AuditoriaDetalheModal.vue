<template>
  <UModal v-model:open="open" title="Detalhes da alteração">
    <template #body>
      <div class="grid grid-cols-2 gap-4">
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

const antigoFormatado = computed(() => JSON.stringify(props.log?.alteracoes.antigo, null, 2))
const novoFormatado = computed(() => JSON.stringify(props.log?.alteracoes.novo, null, 2))
</script>
