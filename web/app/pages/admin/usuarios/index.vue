<template>
  <div>
    <h1 class="text-xl font-semibold mb-4">
      Usuários
    </h1>

    <!-- form de cadastro, so author/admin (aluno se cadastra sozinho por /auth/register) -->
    <UCard class="mb-6">
      <template #header>
        <p class="font-medium">
          Cadastrar usuário
        </p>
      </template>

      <UForm :schema="schema" :state="formState" class="flex flex-wrap items-end gap-3" @submit="onCreate">
        <UFormField name="username" label="Usuário">
          <UInput v-model="formState.username" />
        </UFormField>

        <UFormField name="email" label="Email">
          <UInput v-model="formState.email" type="email" />
        </UFormField>

        <UFormField name="password" label="Senha">
          <UInput v-model="formState.password" type="password" />
        </UFormField>

        <UFormField name="role" label="Papel">
          <USelect v-model="formState.role" :items="roleOptions" class="w-32" />
        </UFormField>

        <UButton type="submit" label="Cadastrar" :loading="creating" />
      </UForm>
    </UCard>

    <!-- UTable = tabela pronta do nuxt ui, so precisa de data + columns -->
    <UTable :data="usuarios" :columns="columns" :loading="loading" />
  </div>
</template>

<script setup lang="ts">
import type { FormSubmitEvent, TableColumn } from '@nuxt/ui'
import type { RoleUsuario, UsuarioRead } from '~/types/generated'
import { zUsuarioStaffCreate } from '~/types/generated/zod.gen'

// so admin acessa essa pagina
definePageMeta({ middleware: 'role', roles: ['admin'] })

const toast = useToast()

const usuarios = ref<UsuarioRead[]>([])
const loading = ref(true)

async function fetchUsuarios() {
  loading.value = true
  const api = useApi()
  // GET /admin/usuarios e rota escrita na mao no back (n fastcrud), devolve array direto,
  // sem o { data: [...] } que a gente ve nas rotas de trilha/modulo/conteudo
  usuarios.value = await api('/admin/usuarios')
  loading.value = false
}

// busca assim que a pagina abre
onMounted(fetchUsuarios)

// define quais colunas a UTable desenha e o nome de cada uma. accessorKey tem
// que bater com o nome do campo la no UsuarioRead (username, email, role, is_active)
const columns: TableColumn<UsuarioRead>[] = [
  { accessorKey: 'username', header: 'Usuário' },
  { accessorKey: 'email', header: 'Email' },
  { accessorKey: 'role', header: 'Papel' },
  { accessorKey: 'is_active', header: 'Ativo' },
]

// opcoes do select de papel - so author/admin (aluno n cadastra por aqui)
const roleOptions = [
  { label: 'Autor', value: 'author' },
  { label: 'Admin', value: 'admin' },
]

// schema gerado do back, ja com as regras de tamanho minimo/maximo
const schema = zUsuarioStaffCreate
const formState = reactive<{ username: string, email: string, password: string, role: RoleUsuario }>({
  username: '',
  email: '',
  password: '',
  role: 'author',
})

const creating = ref(false)

async function onCreate(event: FormSubmitEvent<typeof formState>) {
  creating.value = true
  try {
    const api = useApi()
    const novo = await api('/admin/usuarios', { method: 'POST', body: event.data })
    // adiciona na lista e limpa o form, sem precisar buscar tudo de novo
    usuarios.value.push(novo)
    formState.username = ''
    formState.email = ''
    formState.password = ''
    formState.role = 'author'
  }
  catch {
    toast.add({ title: 'Não foi possível cadastrar o usuário', color: 'error' })
  }
  finally {
    creating.value = false
  }
}
</script>
