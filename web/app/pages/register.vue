<template>
  <div class="flex min-h-dvh items-center justify-center">
    <!-- mesma estrutura da tela de login: UPageCard + UAuthForm, so troca os campos -->
    <UPageCard class="w-full max-w-md">
      <UAuthForm
        :schema="schema"
        :fields="fields"
        :loading="loading"
        title="Criar conta"
        description="Cadastre-se como aluno no Camus."
        icon="i-lucide-user-plus"
        @submit="onSubmit"
      >
        <template #footer>
          Já tem conta? <ULink
            to="/login"
            class="text-primary font-medium"
          >Entrar</ULink>.
        </template>
      </UAuthForm>
    </UPageCard>
  </div>
</template>

<script setup lang="ts">
import type { AuthFormField, FormSubmitEvent } from '@nuxt/ui'
import type { z } from 'zod'
import { zUsuarioCreate } from '~/types/generated/zod.gen'

definePageMeta({ layout: false })

const auth = useAuthStore()
const toast = useToast()
const loading = ref(false)

// schema gerado do back, sem mexer em nada. mensagem pt-br ja vem do plugin zod-locale
const schema = zUsuarioCreate

type Schema = z.output<typeof schema>

const fields: AuthFormField[] = [
  { name: 'username', type: 'text', label: 'Usuário', placeholder: 'seu_usuario', required: true },
  { name: 'email', type: 'email', label: 'Email', placeholder: 'seu@email.com', required: true },
  { name: 'password', type: 'password', label: 'Senha', placeholder: 'Sua senha', required: true },
]

// na store ja cria a conta E loga em seguida
async function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading.value = true
  try {
    await auth.register(payload.data)
    await navigateTo('/')
  }
  catch {
    toast.add({
      title: 'Não foi possível criar a conta',
      description: 'Verifique os dados e tente de novo.',
      color: 'error',
    })
  }
  finally {
    loading.value = false
  }
}
</script>
