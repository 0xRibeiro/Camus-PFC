<template>
  <div class="flex flex-1 items-center justify-center">
    <!-- flex + items-center + justify-center = centraliza no meio. flex-1 = ocupa a altura da tela necessaria -->
    <div class="grid w-full max-w-md gap-4 md:max-w-4xl md:grid-cols-2">
      <!-- UPageCard = card pronto do nuxt ui. w-full preenche a coluna do formulário -->
      <UPageCard class="w-full">
        <!-- UAuthForm = form de login pronto: desenha os campos, valida com o schema, dispara @submit -->
        <UAuthForm
          :schema="schema"
          :fields="fields"
          :loading="loading"
          title="Entrar"
          description="Acesse sua conta no Camus."
          icon="i-lucide-lock"
          @submit="onSubmit"
        >
          <template #footer>
            <!-- ULink = link do nuxt ui, troca de rota sem recarregar a pagina -->
            <ULink
              to="/register"
              class="text-primary font-medium"
            >Cadastre-se</ULink>.
            <br>
            <br>
            <ULink
              to="/recuperar-senha"
              class="text-primary font-medium"
            >Esqueci minha senha</ULink>.
          </template>
        </UAuthForm>
      </UPageCard>

      <div class="relative -order-1 h-36 overflow-hidden rounded-xl bg-[#07182f] md:order-none md:h-auto">
        <img
          src="/papeis-de-parede/azul/acesso.webp"
          alt=""
          class="absolute inset-0 size-full object-cover object-bottom"
        >
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AuthFormField, FormSubmitEvent } from '@nuxt/ui'
import type { z } from 'zod'
import { zUsuarioLogin } from '~/types/generated/zod.gen'

// layout: false = essa pagina n usa a sidebar/menu do layout padrao
definePageMeta({ layout: false })

const auth = useAuthStore()
const toast = useToast()
const loading = ref(false)

// schema gerado do back, sem mexer em nada. mensagem pt-br ja vem do plugin zod-locale
const schema = zUsuarioLogin

// tipo do dado ja validado (o formato exato que sobra depois do schema rodar)
type Schema = z.output<typeof schema>

// lista de campos que o UAuthForm desenha na tela
const fields: AuthFormField[] = [
  { name: 'email', type: 'email', label: 'Email', placeholder: 'seu@email.com', required: true },
  { name: 'password', type: 'password', label: 'Senha', placeholder: 'Sua senha', required: true },
]

// roda quando o form ja validou td certo e a pessoa apertou entrar
async function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading.value = true
  try {
    await auth.login(payload.data)
    await navigateTo('/')
  }
  catch {
    // login errado (401) ou back fora do ar, avisa na tela
    toast.add({
      title: 'Não foi possível entrar',
      description: 'Confira seu email e senha.',
      color: 'error',
    })
  }
  finally {
    loading.value = false
  }
}
</script>
