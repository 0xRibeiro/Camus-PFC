<script setup lang="ts">
const props = defineProps<{
  src: string
  mobile?: string
  media?: string
  imgClass?: string
  fetchpriority?: 'high' | 'low' | 'auto'
}>()

const tema = useColorMode()
const base = computed(() => props.src.replace(/\.webp$/, ''))

function webp(caminho: string) {
  const sufixo = tema.value === 'light' ? '-claro' : ''
  return `${caminho.replace(/\.webp$/, '')}${sufixo}.webp`
}
</script>

<template>
  <picture class="block">
    <source
      :media="media ?? '(width < 768px)'"
      :srcset="webp(mobile ?? `${base}-mobile`)"
    >
    <img
      :src="webp(src)"
      alt=""
      :class="imgClass"
      :fetchpriority="fetchpriority"
    >
  </picture>
</template>