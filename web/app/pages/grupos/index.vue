<template>
  <div>
    <h1 class="text-xl font-semibold mb-4">
      Meus grupos
    </h1>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <UCard>
        <template #header>
          <p class="font-medium">
            Criar grupo
          </p>
        </template>

        <UForm
          :schema="zGrupoCreate"
          :state="formCriar"
          class="space-y-4"
          @submit="criarGrupo"
        >
          <UFormField
            name="nome"
            label="Nome do grupo"
          >
            <UInput
              v-model="formCriar.nome"
              class="w-full"
            />
          </UFormField>

          <UButton
            type="submit"
            label="Criar grupo"
            :loading="criando"
            :disabled="loading"
          />
        </UForm>
      </UCard>

      <UCard>
        <template #header>
          <p class="font-medium">
            Entrar em um grupo
          </p>
        </template>

        <UForm
          :schema="zGrupoEntrar"
          :state="formEntrar"
          class="space-y-4"
          @submit="entrarGrupo"
        >
          <UFormField
            name="convite"
            label="Código de convite"
          >
            <UInput
              v-model="formEntrar.convite"
              placeholder="Cole o código recebido"
              class="w-full"
            />
          </UFormField>

          <p class="text-sm text-muted">
            Os convites são válidos por 15 minutos após a geração.
          </p>

          <UButton
            type="submit"
            label="Entrar no grupo"
            :loading="entrando"
            :disabled="loading"
          />
        </UForm>
      </UCard>
    </div>

    <div
      v-if="loading"
      class="flex justify-center py-12"
    >
      <UIcon
        name="i-lucide-loader-circle"
        class="size-6 animate-spin"
      />
    </div>

    <div
      v-else-if="erroCarregamento"
      class="space-y-3"
    >
      <p class="text-muted">
        Não foi possível carregar seus grupos.
      </p>
      <UButton
        label="Tentar novamente"
        color="neutral"
        variant="outline"
        @click="fetchGrupos"
      />
    </div>

    <p
      v-else-if="grupos.length === 0"
      class="text-muted"
    >
      Você ainda não participa de nenhum grupo. Crie um ou entre usando um convite.
    </p>

    <UPageGrid v-else>
      <UCard
        v-for="grupo in grupos"
        :key="grupo.id"
      >
        <div class="flex items-center justify-between gap-3">
          <h2 class="font-medium break-words min-w-0">
            {{ grupo.nome }}
          </h2>

          <UBadge
            :color="grupo.id_dono === auth.user?.id ? 'primary' : 'neutral'"
            variant="soft"
          >
            {{ grupo.id_dono === auth.user?.id ? 'Dono' : 'Participante' }}
          </UBadge>
        </div>
        <template #footer>
          <UButton
            label="Abrir grupo"
            :to="`/grupos/${grupo.id}`"
            color="neutral"
            variant="outline"
          />
        </template>
      </UCard>
    </UPageGrid>
  </div>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import type { GrupoRead } from '~/types/generated'
import { zGrupoCreate, zGrupoEntrar } from '~/types/generated/zod.gen'

// exige login, permitindo qualquer papel de usuário
definePageMeta({ middleware: 'role' })

const api = useApi()
const auth = useAuthStore()
const toast = useToast()

const grupos = ref<GrupoRead[]>([])
const loading = ref(true)
const erroCarregamento = ref(false)

const formCriar = reactive({ nome: '' })
const formEntrar = reactive({ convite: '' })

const criando = ref(false)
const entrando = ref(false)

// usa a mensagem do backend quando ela vier como texto
function mensagemErro(error: unknown, padrao: string): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return padrao
}

async function fetchGrupos() {
  loading.value = true
  erroCarregamento.value = false

  try {
    // retorna a lista diretamente, sem o tratamento do FastCRUD
    grupos.value = await api('/grupos')
  }
  catch {
    erroCarregamento.value = true
  }
  loading.value = false
}

async function criarGrupo(event: FormSubmitEvent<typeof formCriar>) {
  criando.value = true

  try {
    const grupo: GrupoRead = await api('/grupos', { method: 'POST', body: event.data })
    grupos.value.push(grupo)
    formCriar.nome = ''
    toast.add({ title: 'Grupo criado', color: 'success' })
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível criar o grupo'), color: 'error' })
  }
  finally {
    criando.value = false
  }
}

async function entrarGrupo(event: FormSubmitEvent<typeof formEntrar>) {
  entrando.value = true

  try {
    const grupo: GrupoRead = await api('/grupos/entrar', { method: 'POST', body: event.data })

    // evita repetir o card caso o grupo já esteja na lista local
    if (!grupos.value.some(item => item.id === grupo.id)) {
      grupos.value.push(grupo)
    }

    formEntrar.convite = ''
    toast.add({ title: 'Você entrou no grupo', color: 'success' })
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível entrar no grupo'), color: 'error' })
  }
  entrando.value = false
}

onMounted(fetchGrupos)
</script>
