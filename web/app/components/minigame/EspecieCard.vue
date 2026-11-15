<template>
  <div class="relative overflow-hidden rounded-xl bg-elevated">
    <img
      :src="especie.foto_url"
      :alt="especie.nome"
      class="h-44 w-full object-cover sm:h-[32dvh]"
    >

    <div class="absolute inset-0 bg-linear-to-t from-black/85 via-black/30 to-transparent" />

    <div class="absolute inset-x-0 bottom-0 space-y-2 p-4 text-center text-white">
      <p class="text-lg font-semibold leading-tight sm:text-xl">
        {{ especie.nome }}
      </p>

      <!-- numero aparece animado subindo ate o valor -->
      <p
        v-if="registros !== null"
        class="text-3xl font-bold tabular-nums sm:text-4xl"
        :class="corNumero"
      >
        {{ numeroFormatado }}
        <span class="block text-xs font-normal text-white/70">registros no iNaturalist</span>
      </p>

      <slot />
    </div>

    <p class="absolute right-2 top-2 max-w-[80%] truncate rounded bg-black/50 px-1.5 py-0.5 text-[10px] text-white/70">
      {{ especie.foto_atribuicao }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { TransitionPresets } from '@vueuse/core'
import type { EspecieComparadaRead } from '~/types/generated'

// sem o default o vue transforma acertou n passado em false e pinta de vermelho
const props = withDefaults(defineProps<{
  especie: EspecieComparadaRead
  registros: number | null
  animar?: boolean
  acertou?: boolean | null
}>(), {
  animar: false,
  acertou: null,
})

const alvo = computed(() => props.registros ?? 0)
const animado = useTransition(alvo, {
  duration: 900,
  transition: TransitionPresets.easeOutCubic,
  disabled: computed(() => !props.animar),
})

const numeroFormatado = computed(() => Math.round(animado.value).toLocaleString('pt-BR'))

const corNumero = computed(() => {
  if (props.acertou === true) return 'text-success'
  if (props.acertou === false) return 'text-error'
  return ''
})
</script>
