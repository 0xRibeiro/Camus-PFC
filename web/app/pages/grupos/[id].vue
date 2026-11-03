<template>
  <div>
    <UButton
      label="Voltar aos grupos"
      icon="i-lucide-arrow-left"
      to="/grupos"
      color="neutral"
      variant="ghost"
      class="mb-4"
    />

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
        {{ erroCarregamento }}
      </p>

      <UButton
        label="Tentar novamente"
        color="neutral"
        variant="outline"
        @click="fetchGrupo"
      />
    </div>

    <div
      v-else-if="grupo"
      class="space-y-6"
    >
      <div>
        <h1 class="text-xl font-semibold break-words">
          {{ grupo.nome }}
        </h1>

        <p class="text-sm text-muted">
          Consulte os participantes e os conteúdos do grupo.
        </p>
      </div>

      <UCard>
        <template #header>
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-medium">
              Membros
            </h2>

            <UBadge
              color="neutral"
              variant="soft"
            >
              {{ membros.length }}
            </UBadge>
          </div>
        </template>

        <UTable
          :data="membros"
          :columns="columns"
        >
          <template #papel-cell="{ row }">
            <UBadge
              :color="row.original.papel === 'dono' ? 'primary' : 'neutral'"
              variant="soft"
            >
              {{ row.original.papel === 'dono' ? 'Dono' : 'Membro' }}
            </UBadge>
          </template>
        </UTable>
      </UCard>

      <UCard v-if="usuarioCriador">
        <template #header>
          <h2 class="font-medium">
            Convidar pessoas
          </h2>
        </template>

        <div class="space-y-4">
          <p class="text-sm text-muted">
            Gere um código e compartilhe com quem deseja convidar. Ele será válido por 15 minutos.
          </p>

          <UButton
            :label="convite ? 'Gerar outro convite' : 'Gerar convite'"
            icon="i-lucide-user-plus"
            :loading="gerando"
            @click="gerarConvite"
          />

          <div
            v-if="convite"
            class="space-y-2"
          >
            <UFormField label="Código de convite">
              <div class="flex flex-wrap gap-2">
                <UInput
                  :model-value="convite.convite"
                  readonly
                  class="w-full sm:w-64"
                />
                <UButton
                  label="Copiar"
                  icon="i-lucide-copy"
                  color="neutral"
                  variant="outline"
                  :disabled="segundosRestantes === 0"
                  @click="copiarConvite"
                />
              </div>
            </UFormField>

            <p
              v-if="segundosRestantes > 0"
              class="text-sm text-muted"
            >
              Expira em {{ tempoRestante }}.
            </p>

            <p
              v-else
              class="text-sm text-muted"
            >
              Este convite expirou. Gere outro código para convidar pessoas.
            </p>
          </div>
        </div>
      </UCard>

      <UCard>
        <template #header>
          <h2 class="font-medium">
            Conteúdos do grupo
          </h2>
        </template>

        <p class="text-muted">
          As trilhas e os demais conteúdos exclusivos deste grupo serão exibidos aqui.
        </p>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { FetchError } from 'ofetch'
import type { ConviteRead, GrupoRead, MembroGrupoRead } from '~/types/generated'

definePageMeta({ middleware: 'role', key: route => route.path })

const route = useRoute()
const api = useApi()
const auth = useAuthStore()
const toast = useToast()

const grupoId = Number(route.params.id)
const grupo = ref<GrupoRead | null>(null)
const membros = ref<MembroGrupoRead[]>([])
const loading = ref(true)
const erroCarregamento = ref('')

const convite = ref<ConviteRead | null>(null)
const gerando = ref(false)
const expiraEm = ref(0)

// módulo VueUse
const agora = useNow({ interval: 1000 })
// arredonda pra cima o tempo restante.
const segundosRestantes = computed(() => Math.max(0, Math.ceil((expiraEm.value - agora.value.getTime()) / 1000)))

const tempoRestante = computed(() => {
  const minutos = Math.floor(segundosRestantes.value / 60)
  const segundos = segundosRestantes.value % 60
  return `${minutos}:${String(segundos).padStart(2, '0')}`
})

const usuarioCriador = computed(() => !!grupo.value && grupo.value.id_dono === auth.user?.id)

const columns: TableColumn<MembroGrupoRead>[] = [
  { accessorKey: 'username', header: 'Usuário' },
  { accessorKey: 'papel', header: 'Papel' },
]

function mensagemErro(error: unknown, padrao: string): string {
  if (error instanceof FetchError && typeof error.data?.detail === 'string') {
    return error.data.detail
  }
  return padrao
}

async function fetchGrupo() {
  loading.value = true
  erroCarregamento.value = ''

  try {
    const [dadosGrupo, dadosMembros] = await Promise.all([
      api(`/grupos/${grupoId}`),
      api(`/grupos/${grupoId}/membros`),
    ])

    grupo.value = dadosGrupo
    membros.value = dadosMembros
  }
  catch (error) {
    grupo.value = null
    membros.value = []
    erroCarregamento.value = mensagemErro(error, 'Não foi possível carregar o grupo')
  }
  finally {
    loading.value = false
  }
}

async function gerarConvite() {
  gerando.value = true

  try {
    const inicio = Date.now()
    const resposta: ConviteRead = await api(`/grupos/${grupoId}/convites`, { method: 'POST' })

    convite.value = resposta
    expiraEm.value = inicio + resposta.expira_em_segundos * 1000
    toast.add({ title: 'Convite gerado', color: 'success' })
  }
  catch (error) {
    toast.add({ title: mensagemErro(error, 'Não foi possível gerar o convite'), color: 'error' })
  }
  finally {
    gerando.value = false
  }
}

async function copiarConvite() {
  if (!convite.value || segundosRestantes.value === 0) return

  try {
    await navigator.clipboard.writeText(convite.value.convite)
    toast.add({ title: 'Convite copiado', color: 'success' })
  }
  catch {
    toast.add({ title: 'Selecione o código e copie manualmente', color: 'error' })
  }
}

onMounted(fetchGrupo)
</script>
