<template>
  <div class="h-32 flex items-center justify-center bg-muted overflow-hidden rounded-md">
    <img
      v-if="src"
      :src="src"
      :alt="alt"
      class="h-full w-full object-cover"
    >
  </div>
</template>

<script setup lang="ts">
defineProps<{
  src?: string | null
  alt?: string
}>()
</script>
