<template>
  <div>
    <h1 class="text-xl font-semibold mb-4">
      Meus grupos
    </h1>

    <!-- recados do admin: continuam na tela até a pessoa apertar em "Entendi" -->
    <div
      v-if="avisos.length"
      class="space-y-3 mb-6"
    >
      <UAlert
        v-for="aviso in avisos"
        :key="aviso.id"
        color="warning"
        variant="subtle"
        icon="i-lucide-bell"
        title="Aviso da administração"
        :description="aviso.mensagem"
        :actions="[{ label: 'Entendi', color: 'neutral', variant: 'outline', onClick: () => dispensarAviso(aviso) }]"
      />
    </div>

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
import { useConquistasStore } from '~/stores/conquistas'
import type { AvisoRead, GrupoRead } from '~/types/generated/types.gen'
import { zGrupoCreate, zGrupoEntrar } from '~/types/generated/zod.gen'

definePageMeta({ middleware: 'role' })

const api = useApi()
const auth = useAuthStore()
const toast = useToast()
const conquistas = useConquistasStore()

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

    // conquista 8: solicita o desbloqueio depois de criar o grupo
    await conquistas.desbloquearConquista(8).catch(() => {})
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

    // conquista 9: solicita o desbloqueio depois de entrar por convite
    await conquistas.desbloquearConquista(9).catch(() => {})
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível entrar no grupo'), color: 'error' })
  }

  entrando.value = false
}

onMounted(fetchGrupos)

const avisos = ref<AvisoRead[]>([])

async function fetchAvisos() {
  try {
    avisos.value = await api('/avisos')
  }
  catch {
    avisos.value = []
  }
}

async function dispensarAviso(aviso: AvisoRead) {
  try {
    await api(`/avisos/${aviso.id}/lido`, { method: 'PATCH' })
    avisos.value = avisos.value.filter(a => a.id !== aviso.id)
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível dispensar o aviso'), color: 'error' })
  }
}

onMounted(fetchAvisos)
</script>