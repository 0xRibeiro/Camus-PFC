<template>
  <div class="overflow-hidden rounded-xl border border-default bg-default">
    <MinigameFotoZoom
      :src="especie.foto_url"
      :alt="especie.nome"
      :atribuicao="especie.foto_atribuicao"
      img-class="h-40 object-cover sm:h-[28dvh]"
    />

    <div class="space-y-2 p-4 text-center">
      <p class="text-lg font-semibold leading-tight text-highlighted sm:text-xl">
        {{ especie.nome }}
      </p>

      <!-- numero aparece animado subindo ate o valor -->
      <p
        v-if="registros !== null"
        class="text-3xl font-bold tabular-nums sm:text-4xl"
        :class="corNumero"
      >
        {{ numeroFormatado }}
        <span class="block text-xs font-normal text-muted">registros no iNaturalist</span>
      </p>

      <slot />

      <p class="truncate text-[10px] text-dimmed">
        {{ especie.foto_atribuicao }}
      </p>
    </div>
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
  return 'text-highlighted'
})
</script>
