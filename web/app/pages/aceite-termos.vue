<template>
  <div class="relative isolate -m-4 flex flex-1 items-center justify-center overflow-hidden bg-[#10122e] px-4 py-8 sm:px-10 xl:justify-start xl:px-24 2xl:px-32">
    <img
      src="/papeis-de-parede/avulsos/lula-gigante.webp"
      alt=""
      class="pointer-events-none absolute inset-0 -z-10 size-full object-cover object-right-bottom lg:object-center"
    >
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
          <NuxtLink
            to="/termos-de-uso?from=aceite"
            class="text-primary font-medium hover:underline"
          >
            Ler os Termos de Uso
          </NuxtLink>

          <br>

          <NuxtLink
            to="/politica-de-privacidade?from=aceite"
            class="text-primary font-medium hover:underline"
          >
            Ler a Política de Privacidade
          </NuxtLink>
        </div>

        <UCheckbox
          v-model="aceito"
          label="Li e aceito os Termos de Uso e a Política de Privacidade."
        />

        <div class="space-y-2">
          <UButton
            :loading="loading"
            :disabled="!aceito"
            block
            @click="confirmarAceite"
          >
            Aceitar e continuar
          </UButton>

          <UButton
            block
            color="neutral"
            variant="outline"
            @click="voltarParaLogin"
          >
            Voltar para o login
          </UButton>
        </div>
      </div>
    </UPageCard>
  </div>
</template>

<script setup lang="ts">
import { FetchError } from 'ofetch'

definePageMeta({
  layout: false,
})

const auth = useAuthStore()
const toast = useToast()

const aceito = ref(false)
const loading = ref(false)

// middleware pula essa pagina
onMounted(() => {
  auth.fetchAceiteTermos().catch(() => {})
})

function voltarParaLogin() {
  auth.logout()
  return navigateTo('/login')
}

async function confirmarAceite() {
  if (!aceito.value) {
    return
  }

  loading.value = true

  try {
    const api = useApi()

    const documentoIds = []
    for (const documento of auth.aceitePendentes) {
      documentoIds.push(documento.id)
    }

    await api('/usuarios/me/aceite-termos', {
      method: 'POST',
      body: { documento_ids: documentoIds },
    })

    auth.aceiteTermos = true
    auth.aceitePendentes = []

    await navigateTo('/')
  }
  catch (error) {
    // 409 saiu versao nova
    const mudou = error instanceof FetchError && error.status === 409
    if (mudou) {
      await auth.fetchAceiteTermos().catch(() => {})
    }

    toast.add({
      title: mudou ? 'Os termos foram atualizados' : 'Não foi possível registrar o aceite',
      description: mudou ? 'Leia a versão nova e aceite de novo.' : 'Tente novamente.',
      color: 'error',
    })
  }
  finally {
    loading.value = false
  }
}
</script>
