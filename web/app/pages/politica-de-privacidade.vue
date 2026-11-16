<template>
  <div class="-m-4 flex-1 bg-[linear-gradient(to_bottom,#fecaca,#fff1f2)] dark:bg-[linear-gradient(to_bottom,#210007,#64242e)]">
    <CamusDocumentos
      imagem-esquerda="/papeis-de-parede/vermelho/privacidade-esquerda.webp"
      imagem-direita="/papeis-de-parede/vermelho/privacidade-direita.webp"
    >
      <div class="max-w-3xl mx-auto px-4 py-10">
        <UButton
          icon="i-lucide-arrow-left"
          label="Voltar"
          color="neutral"
          variant="link"
          class="px-0 mb-6"
          @click="voltar"
        />

        <CamusDocumentoLegal
          tipo="politica_de_privacidade"
          titulo="Política de Privacidade"
        />
      </div>
    </CamusDocumentos>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const route = useRoute()
const auth = useAuthStore()

function voltar() {
  if (route.query.from === 'register') {
    return navigateTo('/register')
  }

  if (auth.isAuthenticated) {
    return navigateTo('/')
  }

  return navigateTo('/aceite-termos')
}
</script>
