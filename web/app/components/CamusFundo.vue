<template>
  <div
    class="flex h-28 w-full justify-end overflow-hidden rounded-xl bg-[#07182f] sm:h-36 lg:h-44"
  >
    <img
      :src="src"
      alt=""
      width="1536"
      height="512"
      decoding="async"
      class="h-full w-auto max-w-none shrink-0"
    >
  </div>
</template>

<script setup lang="ts">
defineProps<{
  src: string
}>()
</script>