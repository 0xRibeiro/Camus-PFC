<script setup lang="ts">
defineProps<{
  imagemEsquerda: string
  imagemDireita: string
}>()
</script>

<template>
  <div class="mx-auto grid max-w-7xl grid-cols-1 items-start gap-6 px-4 py-10 xl:grid-cols-[minmax(0,1fr)_minmax(0,48rem)_minmax(0,1fr)]">
    <div class="sticky top-6 hidden xl:block">
      <img
        :src="imagemEsquerda"
        alt=""
        width="480"
        height="1440"
        class="block h-auto max-h-[calc(100dvh-3rem)] w-full rounded-xl object-cover"
      >
    </div>

    <div class="mx-auto w-full min-w-0 max-w-3xl">
      <slot />
    </div>

    <div class="sticky top-6 hidden xl:block">
      <img
        :src="imagemDireita"
        alt=""
        width="480"
        height="100%"
        class="block h-auto max-h-[calc(100dvh-3rem)] w-full rounded-xl object-cover"
      >
    </div>
  </div>
</template>