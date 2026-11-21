<template>
  <div class="flex-1 p-4">
    <UButton
      :label="ehAdmin ? 'Voltar às denúncias' : 'Voltar aos grupos'"
      icon="i-lucide-arrow-left"
      :to="ehAdmin ? '/admin/denuncias' : '/grupos'"
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
      <!-- card do dono com as infos do grupo -->
      <UCard>
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div
            v-if="dono"
            class="self-start rounded-full bg-linear-to-b from-primary to-primary/30 p-1 sm:self-center"
          >
            <UsuarioAvatar
              :avatar="dono.avatar"
              :cor-fundo="dono.cor_fundo"
              :tamanho="96"
            />
          </div>

          <div class="min-w-0 flex-1 space-y-2">
            <h1 class="text-2xl font-bold break-words text-highlighted">
              {{ grupo.nome }}
            </h1>

            <p
              v-if="dono"
              class="flex items-center gap-1.5 text-sm text-muted"
            >
              <UIcon
                name="i-lucide-crown"
                class="size-4 text-amber-400"
              />
              Dono:
              <span class="truncate font-medium text-highlighted">{{ dono.username }}</span>
              <UBadge
                v-if="usuarioCriador"
                label="você"
                size="sm"
                variant="subtle"
              />
            </p>

            <div class="flex flex-wrap gap-2">
              <UBadge
                icon="i-lucide-users"
                color="neutral"
                variant="soft"
              >
                {{ totalAlunos }} aluno{{ totalAlunos === 1 ? '' : 's' }}
              </UBadge>
              <UBadge
                v-if="podeVerConteudo"
                icon="i-lucide-book-open"
                color="neutral"
                variant="soft"
              >
                {{ trilhas.length }} trilha{{ trilhas.length === 1 ? '' : 's' }}
              </UBadge>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2 sm:self-start">
            <!-- denunciar só aparece pra membro, dono e admin não veem -->
            <UButton
              v-if="!usuarioCriador && !ehAdmin"
              label="Denunciar grupo"
              icon="i-lucide-flag"
              color="error"
              variant="outline"
              @click="denunciando = true"
            />

            <!-- admin só visualiza o grupo, então nem sair nem excluir -->
            <UButton
              v-if="!ehAdmin"
              :label="acaoGrupo"
              :icon="usuarioCriador ? 'i-lucide-trash-2' : 'i-lucide-log-out'"
              color="error"
              variant="outline"
              @click="confirmando = true"
            />
          </div>
        </div>
      </UCard>

      <UAlert
        v-if="grupo.suspenso"
        color="warning"
        variant="subtle"
        icon="i-lucide-triangle-alert"
        :title="tituloSuspensao"
        :description="usuarioCriador
          ? 'Você consegue visualizar o grupo, mas não pode alterar nada até o fim da suspensão.'
          : 'O acesso aos conteúdos do grupo fica bloqueado até o fim da suspensão.'"
      />

      <!-- trilhas do grupo -->
      <UCard v-if="podeVerConteudo">
        <template #header>
          <div class="flex flex-wrap items-center justify-between gap-3">
            <h2 class="font-medium">
              Trilhas
            </h2>

            <UButton
              v-if="gerenciaTrilhas"
              label="Gerenciar trilhas"
              icon="i-lucide-settings-2"
              size="sm"
              :to="`/grupos/${grupoId}/trilhas/gerenciar`"
            />
          </div>
        </template>

        <p
          v-if="!trilhas.length"
          class="py-6 text-center text-sm text-muted"
        >
          Nenhuma trilha no grupo ainda.
        </p>

        <UPageGrid v-else>
          <TrilhaProgressoCard
            v-for="trilha in trilhas"
            :key="trilha.id"
            :trilha="trilha"
            :to="`/grupos/${grupoId}/trilhas/${trilha.id}`"
          />
        </UPageGrid>
      </UCard>

      <UCard v-if="usuarioCriador && !grupo.suspenso">
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

      <!-- ranking dos alunos, o dono fica de fora -->
      <UCard v-if="podeVerConteudo">
        <template #header>
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-medium">
              Alunos
            </h2>

            <UBadge
              color="neutral"
              variant="soft"
            >
              {{ ranking.length }}
            </UBadge>
          </div>
        </template>

        <p
          v-if="!ranking.length"
          class="py-6 text-center text-sm text-muted"
        >
          Nenhum aluno no grupo ainda.
        </p>

        <RankingLista
          v-else
          :ranking="ranking"
        >
          <template #acoes="{ item }">
            <UButton
              v-if="gerenciaTrilhas"
              label="Remover"
              :aria-label="`Remover ${item.username}`"
              color="error"
              variant="ghost"
              size="xs"
              :loading="removendoMembro === item.usuario_id"
              :disabled="removendoMembro !== null"
              @click="abrirRemoverMembro(item)"
            />
          </template>
        </RankingLista>

        <p
          v-if="erroRemocao"
          role="alert"
          class="mt-2 text-sm text-error"
        >
          {{ erroRemocao }}
        </p>
      </UCard>

      <UModal
        v-model:open="confirmando"
        :title="acaoGrupo"
        :description="usuarioCriador
          ? 'Isso exclui o grupo, suas trilhas e o XP do grupo para todos os membros.'
          : 'Você perde o acesso às trilhas do grupo. Para voltar, use um convite válido.'"
        :dismissible="!removendo"
        :close="!removendo"
      >
        <template #footer="{ close }">
          <UButton
            label="Cancelar"
            color="neutral"
            variant="outline"
            :disabled="removendo"
            @click="close"
          />
          <UButton
            :label="acaoGrupo"
            color="error"
            :loading="removendo"
            @click="confirmarSaida"
          />
        </template>
      </UModal>

      <UModal
        v-model:open="confirmandoRemocao"
        title="Remover aluno"
        :description="membroParaRemover
          ? `Remover ${membroParaRemover.username} do grupo? A pessoa perde o acesso às trilhas do grupo e só volta com um convite válido.`
          : ''"
        :dismissible="removendoMembro === null"
        :close="removendoMembro === null"
      >
        <template #footer="{ close }">
          <UButton
            label="Cancelar"
            color="neutral"
            variant="outline"
            :disabled="removendoMembro !== null"
            @click="close"
          />
          <UButton
            label="Remover"
            color="error"
            :loading="removendoMembro !== null"
            @click="removerMembro"
          />
        </template>
      </UModal>

      <GrupoDenunciaModal
        v-model:open="denunciando"
        :grupo-id="grupoId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { FetchError } from 'ofetch'
import { useConquistasStore } from '~/stores/conquistas'
import type { ConviteRead, GrupoRead, MembroGrupoRead, RankingItemRead, TrilhaResumoRead } from '~/types/generated/types.gen'

// admin entra so pra moderar, vindo das denuncias
definePageMeta({ middleware: 'role', roles: ['aluno', 'admin'], key: route => route.path })

const route = useRoute()
const auth = useAuthStore()
const toast = useToast()
const conquistas = useConquistasStore()

const grupoId = Number(route.params.id)
const api = useApi(grupoId)
const grupo = ref<GrupoRead | null>(null)
const membros = ref<MembroGrupoRead[]>([])
const trilhas = ref<TrilhaResumoRead[]>([])
const ranking = ref<RankingItemRead[]>([])
const loading = ref(true)
const erroCarregamento = ref('')

const convite = ref<ConviteRead | null>(null)
const gerando = ref(false)
const expiraEm = ref(0)

// módulo VueUse
const agora = useNow({ interval: 1000 })

// arredonda para cima o tempo restante
const segundosRestantes = computed(() => Math.max(0, Math.ceil((expiraEm.value - agora.value.getTime()) / 1000)))

const tempoRestante = computed(() => {
  const minutos = Math.floor(segundosRestantes.value / 60)
  const segundos = segundosRestantes.value % 60
  return `${minutos}:${String(segundos).padStart(2, '0')}`
})

const usuarioCriador = computed(() => !!grupo.value && grupo.value.id_dono === auth.user?.id)
const confirmando = ref(false)
const removendo = ref(false)
const acaoGrupo = computed(() => usuarioCriador.value ? 'Excluir grupo' : 'Sair do grupo')
const removendoMembro = ref<number | null>(null)
const erroRemocao = ref('')
const denunciando = ref(false)

// admin só olha o grupo, então o botão de denunciar não aparece pra ele
const ehAdmin = computed(() => auth.role === 'admin')

// grupo suspenso: o dono só olha, não consegue gerenciar nada
const gerenciaTrilhas = computed(() => usuarioCriador.value && !grupo.value?.suspenso)

// o título do aviso depende de a suspensão ter data de fim ou de o grupo estar inabilitado
const tituloSuspensao = computed(() => {
  if (!grupo.value?.suspenso_ate) return 'Este grupo foi inabilitado'

  return `Este grupo está suspenso até ${new Date(grupo.value.suspenso_ate).toLocaleDateString('pt-BR')}`
})

// membro com o grupo suspenso n ve trilhas nem ranking (o back barra)
const podeVerConteudo = computed(() => !!grupo.value && (!grupo.value.suspenso || usuarioCriador.value || ehAdmin.value))

const dono = computed(() => {
  for (const membro of membros.value) {
    if (membro.papel === 'dono') return membro
  }
  return null
})

const totalAlunos = computed(() => Math.max(0, membros.value.length - 1))

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

    // as duas rotas passam pelo prefixo do grupo no useApi
    if (podeVerConteudo.value) {
      const [dadosTrilhas, dadosRanking] = await Promise.all([
        api('/progresso/trilhas'),
        api('/pontuacao/ranking'),
      ])
      trilhas.value = dadosTrilhas
      ranking.value = dadosRanking
    }
  }
  catch (error) {
    grupo.value = null
    membros.value = []
    trilhas.value = []
    ranking.value = []
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

    // conquista 10: solicita o desbloqueio depois de gerar o convite
    await conquistas.desbloquearConquista(10).catch(() => {})
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

async function confirmarSaida() {
  if (removendo.value) return

  const excluir = usuarioCriador.value
  const caminho = excluir ? `/grupos/${grupoId}` : `/grupos/${grupoId}/membros/me`
  removendo.value = true

  try {
    await api(caminho, { method: 'DELETE' })
    confirmando.value = false
    toast.add({ title: excluir ? 'Grupo excluído' : 'Você saiu do grupo', color: 'success' })
    await navigateTo('/grupos', { replace: true })
  }
  catch (error) {
    const padrao = excluir ? 'Não foi possível excluir o grupo' : 'Não foi possível sair do grupo'
    toast.add({ title: mensagemErro(error, padrao), color: 'error' })
  }
  finally {
    removendo.value = false
  }
}

// a lixeira so abre o modal, quem remove de fato e o botao de confirmar
const confirmandoRemocao = ref(false)
const membroParaRemover = ref<RankingItemRead | null>(null)

function abrirRemoverMembro(aluno: RankingItemRead) {
  membroParaRemover.value = aluno
  confirmandoRemocao.value = true
}

async function removerMembro() {
  const aluno = membroParaRemover.value
  if (!aluno || removendoMembro.value !== null) return

  removendoMembro.value = aluno.usuario_id
  erroRemocao.value = ''

  try {
    await api(`/grupos/${grupoId}/membros/${aluno.usuario_id}`, { method: 'DELETE' })
    membros.value = membros.value.filter(item => item.id !== aluno.usuario_id)
    // recarrega pra recalcular as posicoes
    ranking.value = await api('/pontuacao/ranking')
  }
  catch (error) {
    erroRemocao.value = mensagemErro(error, 'Não foi possível remover o membro')
  }
  finally {
    removendoMembro.value = null
    // fecha tb no erro, a msg aparece embaixo do ranking
    confirmandoRemocao.value = false
  }
}
onMounted(fetchGrupo)
</script>
