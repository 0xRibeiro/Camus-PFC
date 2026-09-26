<template>
  <div class="flex min-h-dvh items-center justify-center">
    <UPageCard class="w-full max-w-md">
      <UAuthForm
        v-if="etapa === 'email'"
        :schema="schemaEmail"
        :fields="fieldsEmail"
        :loading="loading"
        title="Recuperar senha"
        description="Digite seu email pra receber o código de recuperação."
        icon="i-lucide-mail"
        @submit="onSubmitEmail"
      >
        <template #footer>
          <ULink
            to="/login"
            class="text-primary font-medium"
          >Voltar</ULink>.
        </template>
      </UAuthForm>

      <UAuthForm
        v-else
        :schema="schemaCodigo"
        :fields="fieldsCodigo"
        :loading="loading"
        title="Redefinir senha"
        description="Digite o código enviado pro seu email e a nova senha."
        icon="i-lucide-key-round"
        @submit="onSubmitCodigo"
      >
        <template #footer>
          Não recebeu o código? <ULink
            as="button"
            class="text-primary font-medium"
            @click="etapa = 'email'"
          >Voltar</ULink>.
        </template>
      </UAuthForm>
    </UPageCard>
  </div>
</template>

<script setup lang="ts">
import type { AuthFormField, FormSubmitEvent } from '@nuxt/ui'
import type { z } from 'zod'
import { zForgotPasswordInput, zResetPasswordInput } from '~/types/generated/zod.gen'

definePageMeta({ layout: false })

const auth = useAuthStore()
const toast = useToast()
const loading = ref(false)
const etapa = ref<'email' | 'codigo'>('email')
const email = ref('')

const schemaEmail = zForgotPasswordInput
type SchemaEmail = z.output<typeof schemaEmail>

const fieldsEmail: AuthFormField[] = [
  { name: 'email', type: 'email', label: 'Email', placeholder: 'seu@email.com', required: true },
]

async function onSubmitEmail(payload: FormSubmitEvent<SchemaEmail>) {
  loading.value = true
  try {
    await auth.forgotPassword(payload.data)
    email.value = payload.data.email
    etapa.value = 'codigo'
  }
  catch {
    toast.add({
      title: 'Não foi possível enviar o código',
      description: 'Verifique o email e tente de novo.',
      color: 'error',
    })
  }
  finally {
    loading.value = false
  }
}

const schemaCodigo = zResetPasswordInput.omit({ email: true })
type SchemaCodigo = z.output<typeof schemaCodigo>

const fieldsCodigo: AuthFormField[] = [
  { name: 'code', type: 'text', label: 'Código', placeholder: '000000', required: true },
  { name: 'password', type: 'password', label: 'Nova senha', placeholder: 'Sua nova senha', required: true, hint: 'Mín. 8 caracteres' },
]

async function onSubmitCodigo(payload: FormSubmitEvent<SchemaCodigo>) {
  loading.value = true
  try {
    await auth.resetPassword({ email: email.value, ...payload.data })
    await navigateTo('/login')
  }
  catch {
    toast.add({
      title: 'Não foi possível redefinir a senha',
      description: 'Confira o código e tente de novo.',
      color: 'error',
    })
  }
  finally {
    loading.value = false
  }
}
</script>
