<template>
  <div class="flex min-h-dvh items-center justify-center">
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
          <div class="space-y-3">
            <UCheckbox v-model="aceitouTermos">
              <template #label>
                <span>
                  Li e concordo com os
                  <ULink
                    to="/termos-de-uso"
                    class="text-primary font-medium"
                    @click.stop
                  >
                    Termos de Uso
                  </ULink>
                  e estou ciente da
                  <ULink
                    to="/politica-de-privacidade"
                    class="text-primary font-medium"
                    @click.stop
                  >
                    Política de Privacidade
                  </ULink>.
                </span>
              </template>
            </UCheckbox>

            <div>
              Já tem conta?
              <ULink
                to="/login"
                class="text-primary font-medium"
              >
                Entrar
              </ULink>.
            </div>
          </div>
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
const aceitouTermos = ref(false)

const schema = z.object({
  username: zUsuarioCreate.shape.username,
  email: zUsuarioCreate.shape.email,
  password: zUsuarioCreate.shape.password,
})

type Schema = z.output<typeof schema>

const fields: AuthFormField[] = [
  {
    name: 'username',
    type: 'text',
    label: 'Usuário',
    placeholder: 'seu_usuario',
    required: true,
  },
  {
    name: 'email',
    type: 'email',
    label: 'Email',
    placeholder: 'seu@email.com',
    required: true,
  },
  {
    name: 'password',
    type: 'password',
    label: 'Senha',
    placeholder: 'Sua senha',
    required: true,
  },
]

async function onSubmit(payload: FormSubmitEvent<Schema>) {
  if (!aceitouTermos.value) {
    toast.add({
      title: 'Aceite necessário',
      description:
        'Você precisa aceitar os Termos de Uso e a Política de Privacidade.',
      color: 'error',
    })
    return
  }

  loading.value = true

  try {
    await auth.register({
      ...payload.data,
      aceitou_termos: aceitouTermos.value,
    })

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