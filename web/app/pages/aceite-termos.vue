<template>
  <div class="flex min-h-dvh items-center justify-center p-4">
    <UPageCard class="w-full max-w-2xl">
      <div class="space-y-6">
        <div>
          <h1 class="text-2xl font-bold">
            Antes de continuar
          </h1>

          <p class="mt-2 text-muted">
            Para continuar utilizando o Camus, você precisa aceitar os
            Termos de Uso e a Política de Privacidade.
          </p>
        </div>

        <div class="space-y-2">
          <ULink
            to="/termos-de-uso"
            target="_blank"
            class="text-primary font-medium"
          >
            Ler os Termos de Uso
          </ULink>

          <br>

          <ULink
            to="/politica-de-privacidade"
            target="_blank"
            class="text-primary font-medium"
          >
            Ler a Política de Privacidade
          </ULink>
        </div>

        <UCheckbox
          v-model="aceito"
          label="Li e aceito os Termos de Uso e a Política de Privacidade."
        />

        <UButton
          :loading="loading"
          :disabled="!aceito"
          block
          @click="confirmarAceite"
        >
          Aceitar e continuar
        </UButton>
      </div>
    </UPageCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

const auth = useAuthStore()
const toast = useToast()

const aceito = ref(false)
const loading = ref(false)

async function confirmarAceite() {
  if (!aceito.value) {
    return
  }

  loading.value = true

  try {
    const api = useApi()

    await api('/usuarios/me/aceite-termos', {
      method: 'POST',
    })

    auth.aceiteTermos = true

    await navigateTo('/')
  }
  catch {
    toast.add({
      title: 'Não foi possível registrar o aceite',
      description: 'Tente novamente.',
      color: 'error',
    })
  }
  finally {
    loading.value = false
  }
}
</script>
