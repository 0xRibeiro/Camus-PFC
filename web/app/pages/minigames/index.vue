<template>
  <div class="mx-auto w-full max-w-6xl space-y-8 [--ui-primary:var(--ui-tertiary)]">
    <div class="relative isolate overflow-hidden rounded-xl bg-[#011f0e] px-6 sm:px-8">
      <img
        src="/papeis-de-parede/verde/minigames.webp"
        alt=""
        class="pointer-events-none absolute inset-0 -z-20 size-full object-cover object-[72%_center]"
      >

      <div
        aria-hidden="true"
        class="absolute inset-0 -z-10 bg-linear-to-r from-[#011f0e]/95 via-[#011f0e]/60 to-transparent"
      />

      <UPageHeader
        title="Minigames"
        description="Jogue, aprenda sobre a vida aquática e ganhe XP."
        :ui="{ title: 'text-white', description: 'text-emerald-100/85' }"
      >
        <template #headline>
          <div class="flex items-center gap-2 text-sm font-medium text-emerald-300">
            <UIcon
              name="i-lucide-gamepad-2"
              class="size-4"
            />
            Diversão
          </div>
        </template>
      </UPageHeader>
    </div>

    <!-- um card por jogo -->
    <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <UPageCard
        v-for="jogo in jogos"
        :key="jogo.to"
        :title="jogo.titulo"
        :description="jogo.descricao"
        :icon="jogo.icone"
        :to="jogo.to"
        spotlight
        spotlight-color="tertiary"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'role' })

const jogos = [
  {
    titulo: 'Quem é esse peixe?',
    descricao: 'Veja a foto e descubra qual é o animal. Cada acerto vale 5 XP, até 20 acertos por dia.',
    icone: 'i-lucide-fish',
    to: '/minigames/quem-e-esse-peixe',
  },
]
</script>
