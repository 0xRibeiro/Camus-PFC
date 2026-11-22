<template>
  <div class="flex items-center gap-2">
    <UBadge
      :label="rotuloDaSecaoTrilha(chave)"
      :color="corDaSecaoTrilha(chave)"
      variant="soft"
    />
    <span class="text-xs text-muted">
      {{ quantidade }} trilha{{ quantidade === 1 ? '' : 's' }}
    </span>
    <USeparator class="flex-1" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  chave: string
  quantidade: number
}>()
</script>
