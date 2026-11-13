<template>
  <section class="mx-auto flex min-h-[50vh] w-full max-w-2xl flex-col items-center justify-center px-4 py-16 text-center">
    <h1 class="text-4xl font-semibold tracking-tight text-highlighted sm:text-5xl">
      Mergulhe na oceanografia
    </h1>

    <p class="mt-4 max-w-lg text-base leading-relaxed text-muted sm:text-lg">
      Conheça a vida marinha, descubra como os oceanos funcionam e teste seus conhecimentos nas trilhas do Camus.
    </p>

    <UButton
      to="/trilhas"
      label="Explorar trilhas"
      trailing-icon="i-lucide-arrow-right"
      color="neutral"
      variant="link"
      class="mt-5"
    />
  </section>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'role' })
</script>
