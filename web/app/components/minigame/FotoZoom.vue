<template>
  <div class="overflow-hidden">
    <button
      type="button"
      class="group relative block w-full cursor-zoom-in overflow-hidden bg-elevated"
      :aria-label="`Ampliar foto de ${alt}`"
      @click="aberto = true"
    >
      <img
        :src="src"
        :alt="alt"
        class="w-full transition-transform duration-300 group-hover:scale-105"
        :class="imgClass"
      >
      <span class="absolute right-2 top-2 flex size-8 items-center justify-center rounded-full bg-black/50 text-white">
        <UIcon
          name="i-lucide-zoom-in"
          class="size-4"
        />
      </span>
    </button>

    <UModal
      v-model:open="aberto"
      :title="alt"
      :description="atribuicao"
      :ui="{ content: 'max-w-5xl' }"
      @after:leave="zoom = false"
    >
      <template #body>
        <!-- clica pra dar zoom no ponto, arrastando passeia pela foto -->
        <div
          class="relative flex max-h-[65dvh] touch-none select-none items-center justify-center overflow-hidden rounded-lg bg-black"
          :class="zoom ? 'cursor-zoom-out' : 'cursor-zoom-in'"
          @click="alternarZoom"
          @pointermove="mover"
        >
          <img
            :src="srcGrande"
            :alt="alt"
            draggable="false"
            class="max-h-[65dvh] w-auto max-w-full object-contain transition-transform duration-200"
            :style="{ transform: zoom ? 'scale(2.5)' : 'none', transformOrigin: origem }"
          >
        </div>
        <p class="mt-2 text-center text-xs text-muted">
          {{ zoom ? 'Clique de novo pra afastar' : 'Clique na foto pra aproximar' }}
        </p>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  src: string
  alt: string
  atribuicao: string
  imgClass?: string
}>()

const aberto = ref(false)
const zoom = ref(false)
const origem = ref('50% 50%')

// o iNat tem a msm foto em tamanho maior so trocando o nome
const srcGrande = computed(() => props.src.replace('/medium.', '/large.'))

function posicao(evento: MouseEvent) {
  const caixa = (evento.currentTarget as HTMLElement).getBoundingClientRect()
  const x = ((evento.clientX - caixa.left) / caixa.width) * 100
  const y = ((evento.clientY - caixa.top) / caixa.height) * 100
  origem.value = `${x}% ${y}%`
}

function alternarZoom(evento: MouseEvent) {
  posicao(evento)
  zoom.value = !zoom.value
}

function mover(evento: PointerEvent) {
  if (zoom.value) posicao(evento)
}
</script>
