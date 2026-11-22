<template>
  <div class="flex-1 p-4">
    <CamusBanner
      titulo="Meus grupos"
      imagem="/papeis-de-parede/laranja/grupos.webp"
    />

    <!-- recados do admin: continuam na tela até a pessoa apertar em "Entendi" -->
    <div v-if="avisos.length" class="space-y-3 mb-6">
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
          <p class="font-medium">Criar grupo</p>
        </template>

        <UForm
          :schema="zGrupoCreate"
          :state="formCriar"
          class="space-y-4"
          @submit="criarGrupo"
        >
          <UFormField name="nome" label="Nome do grupo">
            <UInput v-model="formCriar.nome" class="w-full" />
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
          <p class="font-medium">Entrar em um grupo</p>
        </template>

        <UForm
          :schema="schemaEntrar"
          :state="formEntrar"
          class="space-y-4"
          @submit="entrarGrupo"
        >
          <UFormField name="convite" label="Código de convite">
            <UInput
              v-model="formEntrar.convite"
              placeholder="000000"
              maxlength="6"
              inputmode="numeric"
              class="w-full sm:w-40"
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

    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-lucide-loader-circle" class="size-6 animate-spin" />
    </div>

    <div v-else-if="erroCarregamento" class="space-y-3">
      <p class="text-muted">Não foi possível carregar seus grupos.</p>
      <UButton
        label="Tentar novamente"
        color="neutral"
        variant="outline"
        @click="fetchGrupos"
      />
    </div>

    <p v-else-if="grupos.length === 0" class="text-muted">
      Você ainda não participa de nenhum grupo. Crie um ou entre usando um convite.
    </p>

    <div
      v-else
      class="space-y-8"
    >
      <!-- a lista e so dos grupos da pessoa, entao filtra aqui mesmo -->
      <UInput
        v-model="busca"
        icon="i-lucide-search"
        placeholder="Buscar grupo pelo nome..."
        class="w-full sm:max-w-sm"
      />

      <p
        v-if="!secoes.length"
        class="text-muted"
      >
        Nenhum grupo encontrado com esse nome.
      </p>

      <!-- separado igual nos aquarios: os que eu criei e os que eu entrei. secao vazia n aparece -->
      <section
        v-for="secao in secoes"
        :key="secao.titulo"
        class="space-y-3"
      >
        <h2 class="flex items-center gap-2 text-lg font-semibold">
          <UIcon
            :name="secao.icone"
            class="size-5 text-muted"
          />
          {{ secao.titulo }}
          <span class="text-sm font-normal text-muted">({{ secao.grupos.length }})</span>
        </h2>

        <UPageGrid>
          <UCard
            v-for="grupo in secao.grupos"
            :key="grupo.id"
          >
            <h3 class="font-medium break-words min-w-0">
              {{ grupo.nome }}
            </h3>
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
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import { useConquistasStore } from '~/stores/conquistas'
import type { AvisoRead, GrupoRead } from '~/types/generated/types.gen'
import { z } from 'zod'
import { zGrupoCreate } from '~/types/generated/zod.gen'

definePageMeta({ middleware: 'role', roles: ['aluno'] })

const api = useApi()
const auth = useAuthStore()
const toast = useToast()
const conquistas = useConquistasStore()

const grupos = ref<GrupoRead[]>([])
const loading = ref(true)
const erroCarregamento = ref(false)

// ------- busca e separacao: dono primeiro, depois os q participo, cada um em ordem alfabetica
const busca = ref('')

const secoes = computed(() => {
  const termo = busca.value.trim().toLowerCase()
  const meus: GrupoRead[] = []
  const participo: GrupoRead[] = []

  for (const grupo of grupos.value) {
    if (termo && !grupo.nome.toLowerCase().includes(termo)) continue
    if (grupo.id_dono === auth.user?.id) meus.push(grupo)
    else participo.push(grupo)
  }

  meus.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
  participo.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))

  const todas = [
    { titulo: 'Grupos que criei', icone: 'i-lucide-crown', grupos: meus },
    { titulo: 'Grupos que participo', icone: 'i-lucide-users', grupos: participo },
  ]

  const visiveis = []
  for (const secao of todas) {
    if (secao.grupos.length) visiveis.push(secao)
  }
  return visiveis
})

const formCriar = reactive({ nome: '' })
const formEntrar = reactive({ convite: '' })
const schemaEntrar = z.object({ convite: zCodigoSeisDigitos })

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
