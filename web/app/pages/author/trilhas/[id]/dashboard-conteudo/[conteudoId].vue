<template>
  <div class="flex-1">
    <UButton
      icon="i-lucide-arrow-left"
      label="Dashboard da trilha"
      color="neutral"
      variant="link"
      class="mb-3 px-0"
      :to="`${caminhoTrilha}/dashboard`"
    />

    <!-- o corpo ta no componente pq o modal da tela da trilha usa o msm -->
    <DashboardConteudo :conteudo-id="conteudoId">
      <template #acoes>
        <UButton
          label="Editar conteúdo"
          icon="i-lucide-pencil"
          color="neutral"
          variant="outline"
          :to="`${caminhoTrilha}/conteudos/${conteudoId}`"
        />
      </template>
    </DashboardConteudo>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'role', roles: ['author', 'admin'], key: route => route.path })

const route = useRoute()
const grupoId = route.params.grupoId
const trilhaId = Number(route.params.id)
const conteudoId = Number(route.params.conteudoId)
const caminhoTrilha = grupoId ? `/grupos/${grupoId}/trilhas/${trilhaId}/editar` : `/author/trilhas/${trilhaId}`
</script>
