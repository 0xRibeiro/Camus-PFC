<template>
  <div class="relative isolate mb-6 overflow-hidden rounded-xl bg-black px-6 sm:px-8">
    <img
      :src="imagem"
      alt=""
      class="pointer-events-none absolute inset-0 -z-20 size-full object-cover object-[72%_center]"
    >

    <div
      aria-hidden="true"
      class="pointer-events-none absolute inset-0 -z-10 bg-linear-to-r from-black/90 via-black/55 to-black/15"
    />

    <UPageHeader
      :title="titulo"
      :description="descricao"
      :ui="{ root: 'py-8', title: 'text-white', description: 'text-white/85' }"
    >
      <template
        v-if="$slots.acoes"
        #links
      >
        <slot name="acoes" />
      </template>
    </UPageHeader>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  titulo: string
  imagem: string
  descricao?: string
}>()
</script>
