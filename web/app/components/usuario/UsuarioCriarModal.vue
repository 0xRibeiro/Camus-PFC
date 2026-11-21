<template>
  <UModal
    v-model:open="open"
    title="Novo usuário"
    description="Contas de aluno são criadas pelo cadastro normal."
    :dismissible="!criando"
  >
    <template #body>
      <UForm
        id="form-novo-usuario"
        :schema="schema"
        :state="formState"
        class="space-y-4"
        @submit="onSubmit"
      >
        <!-- papel em dois botoes, nenhum vem marcado -->
        <UFormField
          name="role"
          label="Papel"
          required
        >
          <div class="grid grid-cols-2 gap-2">
            <UButton
              v-for="opcao in roleOptions"
              :key="opcao.value"
              :label="opcao.label"
              :icon="opcao.icon"
              :variant="formState.role === opcao.value ? 'solid' : 'outline'"
              :color="formState.role === opcao.value ? 'primary' : 'neutral'"
              size="lg"
              block
              @click="formState.role = opcao.value"
            />
          </div>
        </UFormField>

        <UFormField
          name="username"
          label="Usuário"
          required
        >
          <UInput
            v-model="formState.username"
            class="w-full"
          />
        </UFormField>

        <UFormField
          name="email"
          label="Email"
          required
        >
          <UInput
            v-model="formState.email"
            type="email"
            class="w-full"
          />
        </UFormField>

        <UFormField
          name="password"
          label="Senha"
          required
        >
          <UInput
            v-model="formState.password"
            type="password"
            class="w-full"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer="{ close }">
      <div class="flex w-full justify-end gap-2">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="outline"
          :disabled="criando"
          @click="close"
        />
        <UButton
          type="submit"
          form="form-novo-usuario"
          label="Criar"
          :loading="criando"
        />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import { z } from 'zod'
import type { UsuarioAdminRead } from '~/types/generated'
import { zUsuarioStaffCreate } from '~/types/generated/zod.gen'

const open = defineModel<boolean>('open', { required: true })

const emit = defineEmits<{
  criado: [usuario: UsuarioAdminRead]
}>()

const toast = useToast()
const api = useApi()

const roleOptions = [
  { label: 'Autor', value: 'author', icon: 'i-lucide-pen-tool' },
  { label: 'Admin', value: 'admin', icon: 'i-lucide-shield' },
] as const

// regras de tamanho vem do back, o papel tem q ser escolhido na mao
const schema = zUsuarioStaffCreate.extend({
  role: z.enum(['author', 'admin'], { error: 'Escolha o papel' }),
})

const formState = reactive<{ username: string, email: string, password: string, role: 'author' | 'admin' | undefined }>({
  username: '',
  email: '',
  password: '',
  role: undefined,
})

const criando = ref(false)

// toda vez q abre vem limpo
watch(open, (aberto) => {
  if (!aberto) return
  formState.username = ''
  formState.email = ''
  formState.password = ''
  formState.role = undefined
})

async function onSubmit(event: FormSubmitEvent<z.output<typeof schema>>) {
  criando.value = true
  try {
    const novo: UsuarioAdminRead = await api('/admin/usuarios', { method: 'POST', body: event.data })
    emit('criado', novo)
    toast.add({ title: 'Usuário criado', color: 'success' })
    open.value = false
  }
  catch (error) {
    let titulo = 'Não foi possível criar o usuário'
    if (error instanceof FetchError && typeof error.data?.detail === 'string') titulo = error.data.detail
    toast.add({ title: titulo, color: 'error' })
  }
  finally {
    criando.value = false
  }
}
</script>
