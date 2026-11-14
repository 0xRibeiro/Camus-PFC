<template>
  <section
    class="relative isolate mx-auto flex min-h-[32rem] w-full max-w-6xl flex-col items-start overflow-hidden rounded-2xl bg-[#07182f] px-6 py-10 sm:min-h-[50svh] sm:justify-center sm:px-12"
  >
    <picture class="absolute inset-0 -z-20">
      <source media="(max-width: 639px)" srcset="/papeis-de-parede/inicio-mobile.webp">
      <img
        src="/papeis-de-parede/inicio.webp"
        alt=""
        fetchpriority="high"
        class="size-full object-cover object-bottom sm:object-right"
      >
    </picture>

    <div
      aria-hidden="true"
      class="absolute inset-0 -z-10 bg-linear-to-b from-[#07182f]/90 to-transparent sm:bg-linear-to-r"
    />

    <h1 class="max-w-md text-4xl font-semibold tracking-tight text-white sm:text-5xl">
      Mergulhe na oceanografia
    </h1>

    <p class="mt-4 max-w-sm text-base leading-relaxed text-slate-200">
      Conheça a vida marinha, descubra como os oceanos funcionam e teste seus conhecimentos nas trilhas do Camus.
    </p>

    <UButton
      to="/trilhas"
      label="Explorar trilhas"
      trailing-icon="i-lucide-arrow-right"
      color="primary"
      class="mt-6"
    />
  </section>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'role' })
</script>
