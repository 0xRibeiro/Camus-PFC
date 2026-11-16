<script setup lang="ts">
defineProps<{
  imagemEsquerda: string
  imagemDireita: string
}>()
</script>

<template>
  <div class="mx-auto grid max-w-7xl grid-cols-2 items-start gap-x-4 px-4 py-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,48rem)_minmax(0,1fr)] xl:gap-6 xl:py-10">
    <CamusImagem
      :src="imagemEsquerda"
      media="(width < 1280px)"
      class="w-full max-w-36 justify-self-end xl:sticky xl:top-10 xl:max-w-none"
      img-class="aspect-[24/19] w-full rounded-xl object-cover xl:h-[calc(100dvh-2.5rem)]"
    />

    <div class="col-span-2 row-start-2 mx-auto w-full min-w-0 max-w-3xl xl:col-span-1 xl:col-start-2 xl:row-start-1">
      <slot />
    </div>

    <CamusImagem
      :src="imagemDireita"
      media="(width < 1280px)"
      class="col-start-2 row-start-1 w-full max-w-36 xl:sticky xl:top-10 xl:col-start-3 xl:max-w-none"
      img-class="aspect-[24/19] w-full rounded-xl object-cover xl:h-[calc(100dvh-2.5rem)]"
    />
  </div>
</template>
