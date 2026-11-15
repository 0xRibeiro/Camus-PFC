<template>
  <UModal
    v-model:open="aberto"
    :title="bloqueado ? 'Atualização obrigatória' : 'Nova versão disponível'"
    :description="bloqueado
      ? `Essa versão do app não funciona mais. Baixe a versão ${publicada.atual} para continuar usando o Camus.`
      : `A versão ${publicada.atual} do Camus já está disponível.`"
    :dismissible="!bloqueado"
    :close="!bloqueado"
  >
    <template #footer>
      <UButton
        v-if="!bloqueado"
        label="Depois"
        color="neutral"
        variant="outline"
        @click="aberto = false"
      />
      <UButton
        label="Atualizar"
        icon="i-lucide-download"
        @click="baixar"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
// aviso de versao nova do app, so aparece no android
const { estado, publicada, verificar } = useVersaoApp()

const aberto = ref(false)
const bloqueado = computed(() => estado.value === 'bloqueado')

onMounted(async () => {
  await verificar()
  aberto.value = estado.value !== 'ok'
})

// no capacitor url de fora abre no navegador do celular, q baixa o apk
function baixar() {
  window.location.href = publicada.value.apk
}
</script>
