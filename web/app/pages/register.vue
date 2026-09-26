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
import { z } from 'zod'
import { zUsuarioCreate } from '~/types/generated/zod.gen'

definePageMeta({ layout: false })

const auth = useAuthStore()
const toast = useToast()
const loading = ref(false)

const schema = zUsuarioCreate.extend({
  password_confirm: z.string(),
}).refine(data => data.password === data.password_confirm, {
  message: 'As senhas não coincidem',
  path: ['password_confirm'],
})

type Schema = z.output<typeof schema>

const fields: AuthFormField[] = [
  { name: 'username', type: 'text', label: 'Usuário', placeholder: 'seu_usuario', required: true },
  { name: 'email', type: 'email', label: 'Email', placeholder: 'seu@email.com', required: true },
  { name: 'password', type: 'password', label: 'Senha', placeholder: 'Sua senha', required: true, hint: 'Mín. 8 caracteres' },
  { name: 'password_confirm', type: 'password', label: 'Repetir senha', placeholder: 'Repita sua senha', required: true },
]

// na store ja cria a conta E loga em seguida
async function onSubmit(payload: FormSubmitEvent<Schema>) {
  loading.value = true
  const { password_confirm, ...usuario } = payload.data
  try {
    await auth.register(usuario)
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
