<template>
  <div class="flex min-h-dvh items-center justify-center">
    <!-- flex + items-center + justify-center = centraliza no meio. min-h-dvh = ocupa a altura da tela toda -->
    <!-- UPageCard = card pronto do nuxt ui. w-full max-w-md = ocupa td a largura ate uns 448px no max -->
    <UPageCard class="w-full max-w-md">
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
          Não tem conta? <ULink
            to="/register"
            class="text-primary font-medium"
          >Cadastre-se</ULink>.
        </template>
      </UAuthForm>
    </UPageCard>
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
