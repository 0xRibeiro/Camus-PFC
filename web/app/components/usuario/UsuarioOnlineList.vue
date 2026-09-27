<template>
  <UCard class="mb-6">
    <template #header>
      <p class="font-medium">
        Online agora
      </p>
    </template>

    <p v-if="!loading && usuarios.length === 0" class="text-sm text-muted">
      Ninguém online no momento.
    </p>

    <div v-else class="flex flex-wrap gap-2">
      <UBadge
        v-for="usuario in usuarios"
        :key="usuario.id"
        :label="usuario.username"
        color="success"
        variant="soft"
      />
    </div>
  </UCard>
</template>

<script setup lang="ts">
import type { UsuarioRead } from '~/types/generated'

defineProps<{
  usuarios: UsuarioRead[]
  loading: boolean
}>()
</script>
