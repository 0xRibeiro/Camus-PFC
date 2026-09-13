<!-- pagina piada usada para testar o desbloqueio de conquistas usando certas rotas -->
<template>
  <div class="flex min-h-[70vh] flex-col items-center justify-center gap-10 px-4 text-center">
    <div class="flex w-full max-w-7xl items-center justify-center gap-6">
      <!-- o eslint na teoria ajuda, mas acho horrivel essa ordem de atributos... -->
      <img
        src="/camus-logo-inicial.png"
        alt="Logo do Camus"
        class="size-48 shrink-0 object-contain sm:size-64 lg:size-80"
      >
      <h1 class="min-w-0 text-5xl font-black tracking-tight text-highlighted sm:text-7xl lg:text-9xl">
        transparente não é cor
      </h1>
    </div>

    <UButton
      to="/"
      icon="i-lucide-arrow-left"
      size="lg"
    >
      Voltar
    </UButton>
  </div>
</template>
