<template>
  <div class="-m-4 flex-1 bg-[linear-gradient(to_bottom,#eff6ff,#93c5fd)] dark:bg-[linear-gradient(to_bottom,#1e3a5f,#07182f)]">
    <CamusDocumentos
      imagem-esquerda="/papeis-de-parede/azul/termos-esquerda.webp"
      imagem-direita="/papeis-de-parede/azul/termos-direita.webp"
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
          tipo="termos_de_uso"
          titulo="Termos de Uso"
        />
      </div>
    </CamusDocumentos>
  </div>
</template>

<script setup lang="ts">
import { useConquistasStore } from '~/stores/conquistas'

definePageMeta({ layout: false })

const route = useRoute()
const auth = useAuthStore()
const conquistas = useConquistasStore()

// desbloqueia somente se o usuario estiver conectado
onMounted(async () => {
  if (!auth.isAuthenticated) return

  await conquistas.desbloquearConquista(3).catch(() => {})
})

function voltar() {
  if (route.query.from === 'register') {
    return navigateTo('/register')
  }

  if (route.query.from === 'aceite') {
    return navigateTo('/aceite-termos')
  }

  if (auth.isAuthenticated) {
    return navigateTo('/')
  }

  return navigateTo('/login')
}
</script>
