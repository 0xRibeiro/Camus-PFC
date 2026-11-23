<!-- pagina piada usada para testar o desbloqueio de conquistas usando certas rotas -->
<template>
  <div class="flex min-h-[70vh] flex-col items-center justify-center gap-10 px-4 text-center">
    <div class="flex w-full max-w-7xl items-center justify-center gap-6">
      <!-- o eslint na teoria ajuda, mas acho horrivel essa ordem de atributos... -->
      <!-- <img
        <src="/favicon.png" >
        alt="Logo do Camus"
        class="size-48 shrink-0 object-contain sm:size-64 lg:size-80"
      > -->
      <h1 class="min-w-0 text-5xl font-black tracking-tight text-highlighted sm:text-7xl lg:text-9xl">
        {{ textoSegredo }}
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

<script setup lang="ts">
import type { ConquistaUsuarioRead } from '~/types/generated'

const api = useApi()

const ids_conquistas_desbloqueadas = ref(new Set<number>())

// verifica quais das duas conquistas de cor o usuario possui
const textoSegredo = computed(() => {
  const temMelhorCor = ids_conquistas_desbloqueadas.value.has(11)
  const temNemTudoECor = ids_conquistas_desbloqueadas.value.has(12)

  return temMelhorCor && temNemTudoECor
    ? 'transparente é... NÃO SEI!!!'
    : temMelhorCor
      ? 'transparente é cor!'
      : temNemTudoECor
        ? 'transparente não é cor!'
        : 'transparente é.....'
})

// busca as conquistas do usuario ao entrar na pagina
onMounted(async () => {
  try {
    const conquistas = await api('/usuarios/me/conquistas') as ConquistaUsuarioRead[]

    ids_conquistas_desbloqueadas.value = new Set(
      conquistas.map(conquista => conquista.id),
    )
  }
  catch {
    // mantem a frase padrao caso nao consiga carregar as conquistas
  }
})
</script>
