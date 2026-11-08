<template>
  <div
    class="inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full"
    :style="{ backgroundColor: corFundo, width: `${tamanho}px`, height: `${tamanho}px` }"
  >
    <!-- se a imagem nao existir (ainda nao foi feita), mostra um peixe generico -->
    <UIcon
      v-if="falhou"
      name="i-lucide-fish"
      class="text-white"
      :style="{ width: `${tamanho * 0.5}px`, height: `${tamanho * 0.5}px` }"
    />
    <img
      v-else
      :src="`/avatares/${avatar}.png`"
      :alt="avatar"
      class="size-full object-contain p-[10%]"
      @error="falhou = true"
    >
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  avatar: string
  corFundo: string
  tamanho?: number
}>(), {
  tamanho: 40,
})

const falhou = ref(false)

// trocou de avatar, tenta carregar a imagem de novo
watch(() => props.avatar, () => {
  falhou.value = false
})
</script>