<script setup lang="ts">
// card so de exibicao, usado no editor do author e na leitura do aluno
defineProps<{
  nome: string
  nomePopular?: string | null
  foto?: string | null
  observacoes?: number | null
  wikipedia?: string | null
}>()
</script>

<template>
  <div class="not-prose flex gap-4 rounded-xl border border-default bg-elevated/40 p-4 my-4">
    <img
      v-if="foto"
      :src="foto"
      :alt="`Imagem de ${nomePopular || nome}`"
      class="size-24 shrink-0 rounded-lg object-cover"
    >
    <div
      v-else
      class="flex size-24 shrink-0 items-center justify-center rounded-lg bg-elevated text-muted"
    >
      <UIcon
        name="i-lucide-fish"
        class="size-8"
      />
    </div>

    <div class="min-w-0 space-y-2">
      <div>
        <p class="font-semibold text-highlighted">
          {{ nomePopular || nome }}
        </p>
        <p class="text-sm italic text-muted">
          {{ nome }}
        </p>
      </div>

      <UBadge
        color="neutral"
        variant="subtle"
      >
        {{ new Intl.NumberFormat('pt-BR').format(observacoes ?? 0) }} observações
      </UBadge>

      <div v-if="wikipedia">
        <UButton
          label="Ver mais informações"
          icon="i-lucide-external-link"
          variant="link"
          size="sm"
          class="px-0"
          :to="wikipedia"
          target="_blank"
        />
      </div>
    </div>
  </div>
</template>
