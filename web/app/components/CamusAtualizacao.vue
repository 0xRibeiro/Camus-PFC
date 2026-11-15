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
import { App } from '@capacitor/app'

// aviso de versao nova do app, so aparece no android
const { estado, publicada, verificar } = useVersaoApp()

const aberto = ref(false)
const bloqueado = computed(() => estado.value === 'bloqueado')
// o aviso com "depois" so aparece 1x enquanto o app ta aberto, o bloqueio sempre
let jaAvisou = false

async function checar() {
  await verificar()
  if (estado.value === 'bloqueado') {
    aberto.value = true
  }
  else if (estado.value === 'aviso' && !jaAvisou) {
    aberto.value = true
    jaAvisou = true
  }
}

onMounted(checar)

// voltar do segundo plano n recarrega a pagina, entao checa dnv qnd o app volta pra tela
App.addListener('appStateChange', ({ isActive }) => {
  if (isActive) {
    checar()
  }
})

// no capacitor url de fora abre no navegador do celular, q baixa o apk
function baixar() {
  window.location.href = publicada.value.apk
}
</script>
