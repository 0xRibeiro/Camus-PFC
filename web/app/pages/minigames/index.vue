<template>
  <div class="mx-auto w-full max-w-6xl space-y-8">
    <CamusBanner
      titulo="Minigames"
      descricao="Jogue, aprenda sobre a vida aquática e ganhe XP."
      imagem="/papeis-de-parede/verde/minigames.webp"
      headline="Diversão"
      icone="i-lucide-gamepad-2"
    />

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
  {
    titulo: 'Meio peixe, meio fotógrafo',
    descricao: 'Qual espécie foi mais fotografada? Acerte 5 seguidas e entre no combo de 20 XP por acerto.',
    icone: 'i-lucide-camera',
    to: '/minigames/meio-peixe-meio-fotografo',
  },
]
</script>