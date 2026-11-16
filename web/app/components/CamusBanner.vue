<template>
  <div class="relative isolate mb-6 overflow-hidden rounded-xl bg-(--camus-topo) px-6 sm:px-8">
    <CamusImagem
      :src="imagem"
      class="pointer-events-none absolute inset-y-0 right-0 -z-20 w-full lg:w-3/4 xl:w-3/5"
      img-class="size-full object-cover object-right"
    />

    <div
      aria-hidden="true"
      class="camus-banner-veu pointer-events-none absolute inset-0 -z-10"
    />

    <UPageHeader
      :title="titulo"
      :headline="headline"
      :description="descricao"
      :ui="{ root: 'min-h-36 border-0 py-8', description: 'text-toned dark:text-white/85' }"
    >
      <template
        v-if="icone"
        #headline
      >
        <UIcon
          :name="icone"
          class="size-4"
        />
        {{ headline }}
      </template>

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
  headline?: string
  icone?: string
}>()
</script>
