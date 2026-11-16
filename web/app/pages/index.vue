<template>
  <section
    class="relative isolate flex min-h-[32rem] w-full flex-1 flex-col items-start overflow-hidden bg-sky-50 dark:bg-[#07182f] px-6 py-10 sm:min-h-0 sm:justify-center sm:px-12"
  >
    <CamusImagem
      src="/papeis-de-parede/azul/inicio.webp"
      mobile="/papeis-de-parede/verde/inicio-mobile.webp"
      media="(width < 640px)"
      fetchpriority="high"
      class="absolute inset-0 -z-20"
      img-class="size-full object-cover object-bottom sm:object-right"
    />

    <div
      aria-hidden="true"
      class="absolute inset-0 -z-10 bg-linear-to-b from-sky-50/95 via-sky-50/70 to-transparent dark:from-[#07182f]/95 dark:via-[#07182f]/65 sm:bg-linear-to-r"
    />

    <h1 class="max-w-md text-4xl font-semibold tracking-tight text-highlighted sm:text-5xl">
      Mergulhe na oceanografia
    </h1>

    <p class="mt-4 max-w-sm text-base leading-relaxed text-toned dark:text-slate-200">
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
